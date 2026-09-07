"""
抖音 / TikTok 解析服务 — NewPipe 模式

抖音去水印原理：
  yt-dlp 的抖音 extractor 会调用抖音 API 获取无水印视频直链。
  抖音视频通常只有一个清晰度，格式为 mp4（音视频合并）。

TikTok（国际版）同理，yt-dlp 支持无水印下载。

注意：
  - 抖音短链（v.douyin.com）会先 302 重定向到完整链接，yt-dlp 会自动处理
  - 部分地区可能需要代理才能访问 TikTok
"""
import os
import yt_dlp

from ..models import AudioFormat, Formats, ParseResponse, VideoFormat

_YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": False,
}

_PROXY = os.getenv("YTDLP_PROXY")
if _PROXY:
    _YDL_OPTS["proxy"] = _PROXY


def _pick_video_formats(formats: list[dict], platform: str) -> list[VideoFormat]:
    """
    抖音/TikTok 通常只有 1-2 个格式：
      - 无水印版（play_addr_h264 / download_addr）
      - 有水印版
    yt-dlp 会优先提供无水印版。
    """
    results = []
    seen_urls: set[str] = set()

    for f in formats:
        url = f.get("url")
        if not url or url in seen_urls:
            continue
        if f.get("vcodec") == "none":
            continue

        seen_urls.add(url)
        height = f.get("height")
        quality = f"{height}p" if height else f.get("format_note", "标准画质")
        ext = f.get("ext", "mp4")

        filesize = f.get("filesize") or f.get("filesize_approx")
        size_mb = round(filesize / (1024 * 1024), 1) if filesize else None

        note = "无水印" if "watermark" not in f.get("format_id", "").lower() else "含水印"

        results.append(
            VideoFormat(
                quality=quality,
                ext=ext,
                size_mb=size_mb,
                url=url,
                note=note,
            )
        )

    return results


def parse(url: str, platform: str = "douyin") -> ParseResponse:
    """解析抖音或 TikTok 视频 URL。"""
    with yt_dlp.YoutubeDL(_YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError("无法获取视频信息，请检查 URL 是否有效")

    raw_formats = info.get("formats", [])

    return ParseResponse(
        platform=platform,
        title=info.get("description") or info.get("title", "抖音视频"),
        author=info.get("uploader") or info.get("creator"),
        thumbnail=info.get("thumbnail"),
        duration=int(info.get("duration") or 0) or None,
        formats=Formats(
            video=_pick_video_formats(raw_formats, platform),
            audio=[],       # 抖音不提供独立音频
            subtitles=[],   # 抖音不提供字幕
        ),
    )
