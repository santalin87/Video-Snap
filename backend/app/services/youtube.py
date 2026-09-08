"""
YouTube 解析服务 — NewPipe 模式
核心原则：只解析，不下载。返回直链给浏览器直接取。

筛选规则：
  - 视频格式：acodec != none AND vcodec != none AND height <= 720
    （保证是预合并的音视频文件，下载后直接有声音）
  - 音频格式：vcodec == none（纯音频流）
  - 字幕：自动生成字幕 + 手动字幕，支持 SRT/VTT
"""
import os
import yt_dlp

from ..models import AudioFormat, Formats, ParseResponse, SubtitleFormat, VideoFormat

# yt-dlp 通用配置（不下载，只读取信息）
_YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": False,
}

# 如果设置了代理则注入
_PROXY = os.getenv("YTDLP_PROXY")
if _PROXY:
    _YDL_OPTS["proxy"] = _PROXY


def _bytes_to_mb(filesize: int | None) -> float | None:
    if filesize:
        return round(filesize / (1024 * 1024), 1)
    return None


def _pick_video_formats(formats: list[dict]) -> list[VideoFormat]:
    """
    筛选所有可用真实视频文件（1080p/720p/480p/360p等），排除 m3u8 切片清单，优先 MP4。
    """
    # 过滤掉无法直接下载的 m3u8 / manifest 链接，只保留直链音视频文件
    valid_fmts = [
        f for f in formats
        if f.get("vcodec") != "none"
        and f.get("url")
        and "manifest.googlevideo.com" not in f.get("url", "")
        and not str(f.get("protocol", "")).startswith("m3u8")
    ]

    # 按分辨率降序排列，同分辨率优先 MP4，优先有音频的
    sorted_fmts = sorted(
        valid_fmts,
        key=lambda f: (
            f.get("height") or 0,
            1 if f.get("ext") == "mp4" else 0,
            1 if (f.get("acodec") and f.get("acodec") != "none") else 0,
            f.get("tbr") or 0,
        ),
        reverse=True,
    )

    seen = set()
    results = []

    for f in sorted_fmts:
        height = f.get("height")
        if not height:
            continue
        url = f.get("url")
        if not url:
            continue

        ext = f.get("ext", "mp4")
        key = (height, ext)
        if key in seen:
            continue
        seen.add(key)

        has_audio = bool(f.get("acodec") and f.get("acodec") != "none")
        note = "含音频" if has_audio else "视频流"

        filesize = f.get("filesize") or f.get("filesize_approx")

        results.append(
            VideoFormat(
                quality=f"{height}p",
                ext=ext,
                size_mb=_bytes_to_mb(filesize),
                url=url,
                note=note,
            )
        )

    # 再次去重：每个分辨率只保留最优的一个格式（优先 MP4）
    final_results = []
    seen_heights = set()
    for item in results:
        if item.quality not in seen_heights:
            seen_heights.add(item.quality)
            final_results.append(item)

    return final_results


def _pick_audio_formats(formats: list[dict]) -> list[AudioFormat]:
    """
    筛选纯音频流，优先 m4a（兼容性好），再给 webm/opus。排除 m3u8。
    """
    valid_fmts = [
        f for f in formats
        if f.get("vcodec") == "none"
        and f.get("url")
        and "manifest.googlevideo.com" not in f.get("url", "")
        and not str(f.get("protocol", "")).startswith("m3u8")
    ]

    results = []
    seen_exts = set()

    # 按码率降序
    sorted_fmts = sorted(
        valid_fmts,
        key=lambda f: f.get("abr") or f.get("tbr") or 0,
        reverse=True,
    )

    quality_labels = {0: "标准", 1: "高品质", 2: "极高品质"}
    idx = 0

    for f in sorted_fmts:
        if f.get("vcodec") != "none":
            continue
        url = f.get("url")
        if not url:
            continue
        ext = f.get("ext", "m4a")
        if ext in seen_exts:
            continue
        if ext not in ("m4a", "mp3", "webm", "opus"):
            continue
        seen_exts.add(ext)

        abr = int(f.get("abr") or f.get("tbr") or 0)
        label = quality_labels.get(idx, "其他")
        idx += 1

        results.append(
            AudioFormat(
                quality=label,
                ext=ext,
                abr=abr if abr else None,
                url=url,
            )
        )

    return results[:3]  # 最多返回3个音频选项


def _pick_subtitles(
    subtitles: dict, auto_captions: dict
) -> list[SubtitleFormat]:
    """
    合并手动字幕与自动字幕，优先 SRT，再 VTT。
    """
    results = []

    # 合并两个来源（手动字幕优先）
    all_subs: dict[str, list] = {}
    for lang, entries in (auto_captions or {}).items():
        all_subs[lang] = entries
    for lang, entries in (subtitles or {}).items():
        all_subs[lang] = entries  # 手动字幕覆盖自动

    PREFERRED_EXTS = ["srt", "vtt", "json3"]

    for lang, entries in all_subs.items():
        # 找最优格式
        chosen = None
        for preferred in PREFERRED_EXTS:
            for entry in entries:
                if entry.get("ext") == preferred and entry.get("url"):
                    chosen = entry
                    break
            if chosen:
                break

        if not chosen:
            continue

        # 生成友好标签
        label = _lang_label(lang)
        results.append(
            SubtitleFormat(
                lang=lang,
                label=label,
                ext=chosen["ext"],
                url=chosen["url"],
            )
        )

    # 中文优先排列
    results.sort(key=lambda s: (0 if "zh" in s.lang else 1, s.lang))
    return results


def _lang_label(lang: str) -> str:
    """将语言代码转为友好标签。"""
    mapping = {
        "zh-Hans": "中文（简体）",
        "zh-Hant": "中文（繁体）",
        "zh": "中文",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español",
        "pt": "Português",
        "ru": "Русский",
        "ar": "العربية",
    }
    return mapping.get(lang, lang)


def parse(url: str) -> ParseResponse:
    """
    解析 YouTube URL，返回视频信息和可用下载格式。
    不下载任何文件，仅返回 CDN 直链。
    """
    with yt_dlp.YoutubeDL(_YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError("无法获取视频信息，请检查 URL 是否有效")

    raw_formats = info.get("formats", [])

    formats = Formats(
        video=_pick_video_formats(raw_formats),
        audio=_pick_audio_formats(raw_formats),
        subtitles=_pick_subtitles(
            info.get("subtitles", {}),
            info.get("automatic_captions", {}),
        ),
    )

    return ParseResponse(
        platform="youtube",
        title=info.get("title", "未知标题"),
        author=info.get("uploader") or info.get("channel"),
        thumbnail=info.get("thumbnail"),
        duration=int(info.get("duration") or 0) or None,
        formats=formats,
    )
