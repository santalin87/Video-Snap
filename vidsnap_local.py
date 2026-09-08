"""
VidSnap Local Downloader — 本地满速视频下载器
使用本地 IP 直接向 YouTube / 抖音 / X 下载，0 VPS 流量消耗，跑满本地宽带！
"""
import os
import sys
import subprocess
import yt_dlp

# 保存目录：默认保存在当前目录下的 downloads 文件夹
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_clipboard_url():
    """尝试从剪贴板读取 URL"""
    try:
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        text = r.clipboard_get().strip()
        r.destroy()
        if text.startswith("http://") or text.startswith("https://"):
            return text
    except Exception:
        pass
    return ""


def print_banner():
    print("=" * 55)
    print("    VidSnap 本地极速下载器 (0 VPS流量 · 跑满本地网速)")
    print("=" * 55)


def select_format_menu(formats, default_title=""):
    """展示画质菜单供用户选择"""
    print("\n请选择你想要下载的类型：")
    print("  [1] ⭐ 最佳画质 (4K/1080p 自动音画合并，最清晰)")
    print("  [2] 🎬 1080p 高清 MP4 (含音频)")
    print("  [3] 🎬 720p 标清 MP4 (含音频，体积适中)")
    print("  [4] 🎵 提取纯音频 MP3 (高品质音乐/播客)")
    print("  [5] 🎵 提取纯音频 M4A (原声音质)")
    print("  [6] 📄 下载中英文字幕 (SRT)")
    print("  [7] 📋 列出所有详细格式手工选择")

    choice = input("\n请输入选项编号 [默认按回车选 1]: ").strip()
    if not choice:
        choice = "1"
    return choice


def main():
    print_banner()

    # 1. 获取 URL
    clip_url = get_clipboard_url()
    if clip_url:
        print(f"\n检测到剪贴板链接: {clip_url}")
        user_input = input("直接按回车使用该链接，或输入新链接: ").strip()
        url = user_input if user_input else clip_url
    else:
        url = input("\n请粘贴视频链接 (YouTube / X / 抖音 / TikTok): ").strip()

    if not url:
        print("未输入有效链接，程序退出。")
        input("\n按回车键退出...")
        return

    # 2. 解析元数据
    print("\n正在获取视频信息，请稍候...")
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "未知标题")
            duration = info.get("duration", 0)
            uploader = info.get("uploader", "未知作者")
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

            print("\n" + "-" * 50)
            print(f"📌 视频标题: {title}")
            print(f"👤 作者/频道: {uploader}")
            print(f"⏱️ 视频时长: {dur_str}")
            print("-" * 50)

    except Exception as e:
        print(f"\n解析失败: {e}")
        input("\n按回车键退出...")
        return

    # 3. 让用户选择清晰度
    choice = select_format_menu(info.get("formats", []), title)

    # 4. 根据选择配置下载参数
    outtmpl = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    download_opts = {
        "outtmpl": outtmpl,
        "no_warnings": True,
    }

    if choice == "1":
        # 最佳画质 + 最佳音频合并
        download_opts["format"] = "bestvideo+bestaudio/best"
        download_opts["merge_output_format"] = "mp4"
    elif choice == "2":
        # 1080p + 最佳音频
        download_opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
        download_opts["merge_output_format"] = "mp4"
    elif choice == "3":
        # 720p + 最佳音频
        download_opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
        download_opts["merge_output_format"] = "mp4"
    elif choice == "4":
        # 纯音频 MP3
        download_opts["format"] = "bestaudio/best"
        download_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    elif choice == "5":
        # 纯音频 M4A
        download_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
        download_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }]
    elif choice == "6":
        # 下载字幕
        download_opts["skip_download"] = True
        download_opts["writesubtitles"] = True
        download_opts["writeautomaticsub"] = True
        download_opts["subtitleslangs"] = ["zh.*", "en.*"]
        download_opts["subtitlesformat"] = "srt"
    elif choice == "7":
        # 手动格式选择
        subprocess.run(["yt-dlp", "-F", url])
        f_id = input("\n请输入你要下载的 Format ID: ").strip()
        download_opts["format"] = f_id
    else:
        download_opts["format"] = "bestvideo+bestaudio/best"
        download_opts["merge_output_format"] = "mp4"

    # 5. 执行极速下载
    print("\n🚀 正在开始全速下载，请查看下方实时速度与进度条：\n")
    try:
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])

        print("\n" + "=" * 55)
        print("🎉 下载完成！")
        print(f"📁 保存位置: {DOWNLOAD_DIR}")
        print("=" * 55)

        # 自动打开下载文件夹
        os.system(f'explorer "{DOWNLOAD_DIR}"')

    except Exception as e:
        print(f"\n下载出错: {e}")

    input("\n按回车键退出程序...")


if __name__ == "__main__":
    main()
