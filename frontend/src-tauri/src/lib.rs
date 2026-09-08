use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tauri::{AppHandle, Emitter};
use serde::{Deserialize, Serialize};

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

// Windows 下隐藏控制台窗口
#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

#[derive(Serialize, Deserialize, Debug)]
pub struct EngineStatus {
    pub yt_dlp: Option<String>,
    pub ffmpeg: Option<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct DownloadProgress {
    pub percent: f32,
    pub speed: String,
    pub eta: String,
    pub status: String,
    pub filename: String,
}

/// 获取底层引擎 (yt-dlp, ffmpeg) 的当前安装状态与版本号
#[tauri::command]
fn get_engine_status() -> EngineStatus {
    let yt_dlp_ver = get_cmd_version("yt-dlp", &["--version"]);
    let ffmpeg_ver = get_cmd_version("ffmpeg", &["-version"]);

    EngineStatus {
        yt_dlp: yt_dlp_ver,
        ffmpeg: ffmpeg_ver,
    }
}

fn get_cmd_version(cmd: &str, args: &[&str]) -> Option<String> {
    let mut command = Command::new(cmd);
    command.args(args);

    #[cfg(target_os = "windows")]
    command.creation_flags(CREATE_NO_WINDOW);

    match command.output() {
        Ok(output) if output.status.success() => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let first_line = stdout.lines().next().unwrap_or("").trim().to_string();
            if !first_line.is_empty() {
                Some(first_line)
            } else {
                None
            }
        }
        _ => None,
    }
}

/// 一键更新解析引擎 (调用 yt-dlp -U)
#[tauri::command]
fn update_engine(name: String) -> Result<String, String> {
    if name == "yt-dlp" {
        let mut command = Command::new("yt-dlp");
        command.arg("-U");

        #[cfg(target_os = "windows")]
        command.creation_flags(CREATE_NO_WINDOW);

        match command.output() {
            Ok(output) => {
                let stdout = String::from_utf8_lossy(&output.stdout).to_string();
                let stderr = String::from_utf8_lossy(&output.stderr).to_string();
                if output.status.success() {
                    Ok(if stdout.is_empty() { "更新完成".to_string() } else { stdout })
                } else {
                    Err(format!("更新失败: {}{}", stdout, stderr))
                }
            }
            Err(e) => Err(format!("无法调用更新程序: {}", e)),
        }
    } else {
        Err(format!("不支持该组件的自动升级: {}", name))
    }
}

/// 本地使用用户本地 IP 解析视频元数据，0 流量损耗
#[tauri::command]
fn parse_video_local(url: String) -> Result<String, String> {
    let mut command = Command::new("yt-dlp");
    command.args(&[
        "-J",
        "--no-warnings",
        "--skip-download",
        &url,
    ]);

    #[cfg(target_os = "windows")]
    command.creation_flags(CREATE_NO_WINDOW);

    match command.output() {
        Ok(output) if output.status.success() => {
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            Ok(stdout)
        }
        Ok(output) => {
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            Err(format!("解析失败: {}", stderr))
        }
        Err(e) => Err(format!("无法运行 yt-dlp 解析引擎: {}", e)),
    }
}

/// 执行极速下载并通过 Tauri 事件流式推送进度
#[tauri::command]
async fn start_download(
    app: AppHandle,
    url: String,
    format: String,
    is_audio: bool,
) -> Result<String, String> {
    let download_dir = dirs_next::download_dir()
        .map(|d| d.join("VidSnap"))
        .unwrap_or_else(|| std::path::PathBuf::from("downloads"));

    std::fs::create_dir_all(&download_dir)
        .map_err(|e| format!("无法创建下载目录: {}", e))?;

    let outtmpl = download_dir.join("%(title)s.%(ext)s").to_string_lossy().to_string();

    let mut cmd = Command::new("yt-dlp");
    cmd.arg("-o").arg(&outtmpl);
    cmd.arg("--newline"); // 确保每一行进度都有独立换行以便解析

    if is_audio {
        cmd.args(&[
            "-f", "bestaudio/best",
            "-x",
            "--audio-format", &format,
            "--audio-quality", "192K",
        ]);
    } else if format == "best" {
        cmd.args(&[
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
        ]);
    } else {
        cmd.args(&[
            "-f", &format,
            "--merge-output-format", "mp4",
        ]);
    }

    cmd.arg(&url);

    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);

    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    let mut child = cmd.spawn().map_err(|e| format!("启动下载进程失败: {}", e))?;

    let stdout = child.stdout.take().ok_or("无法捕获下载输出")?;
    let reader = BufReader::new(stdout);

    let progress_re = regex::Regex::new(r"\[download\]\s+([\d\.]+)%\s+of\s+\S+\s+at\s+(\S+)\s+ETA\s+(\S+)").unwrap();
    let dest_re = regex::Regex::new(r"Destination:\s+(.+)").unwrap();

    let mut current_filename = "downloading".to_string();

    for line in reader.lines() {
        if let Ok(l) = line {
            if let Some(caps) = dest_re.captures(&l) {
                if let Some(dest) = caps.get(1) {
                    current_filename = dest.as_str().trim().to_string();
                }
            }

            if let Some(caps) = progress_re.captures(&l) {
                let percent: f32 = caps[1].parse().unwrap_or(0.0);
                let speed = caps[2].to_string();
                let eta = caps[3].to_string();

                let progress = DownloadProgress {
                    percent,
                    speed,
                    eta,
                    status: "downloading".to_string(),
                    filename: current_filename.clone(),
                };

                let _ = app.emit("download-progress", progress);
            }
        }
    }

    let status = child.wait().map_err(|e| format!("等待下载进程失败: {}", e))?;

    if status.success() {
        let _ = app.emit("download-progress", DownloadProgress {
            percent: 100.0,
            speed: "0KB/s".to_string(),
            eta: "00:00".to_string(),
            status: "completed".to_string(),
            filename: current_filename,
        });
        Ok(download_dir.to_string_lossy().to_string())
    } else {
        Err("下载非正常退出，请检查网络或格式设置".to_string())
    }
}

/// 打开下载保存目录
#[tauri::command]
fn open_download_folder() -> Result<(), String> {
    let download_dir = dirs_next::download_dir()
        .map(|d| d.join("VidSnap"))
        .unwrap_or_else(|| std::path::PathBuf::from("downloads"));

    #[cfg(target_os = "windows")]
    {
        Command::new("explorer")
            .arg(&download_dir)
            .spawn()
            .map_err(|e| format!("无法打开目录: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(&download_dir)
            .spawn()
            .map_err(|e| format!("无法打开目录: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&download_dir)
            .spawn()
            .map_err(|e| format!("无法打开目录: {}", e))?;
    }

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_engine_status,
            update_engine,
            parse_video_local,
            start_download,
            open_download_folder,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
