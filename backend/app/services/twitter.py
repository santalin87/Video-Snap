"""
Twitter/X 解析服务 — NewPipe 模式

X 平台的视频通常只有一个合并好的视频文件（mp4），
且有多个画质选项（最高可达 1080p/4K）。
所有格式均为音视频合并，可直接下载。

注意：X API 限流较严，需要 Cookie 才能稳定解析私有或高流量内容。
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


def _pick_video_formats(formats: list[dict]) -> list[VideoFormat]:
    """
    X 的视频格式通常都是音视频合并（mp4）。
    返回所有可用画质，从高到低排列。
    """
    results = []
    seen_heights = set()

    sorted_fmts = sorted(
        formats,
        key=lambda f: f.get("height") or 0,
        reverse=True,
    )

    for f in sorted_fmts:
        url = f.get("url")
        if not url:
            continue
        # X 的格式几乎都是音视频合并，跳过明确的纯音频
        if f.get("vcodec") == "none":
            continue

        height = f.get("height")
        if height and height in seen_heights:
            continue
        if height:
            seen_heights.add(height)

        quality = f"{height}p" if height else f.get("format_note", "标准")
        ext = f.get("ext", "mp4")

        filesize = f.get("filesize") or f.get("filesize_approx")
        size_mb = round(filesize / (1024 * 1024), 1) if filesize else None

        results.append(
            VideoFormat(
                quality=quality,
                ext=ext,
                size_mb=size_mb,
                url=url,
            )
        )

    return results


def parse(url: str) -> ParseResponse:
    """解析 Twitter/X 视频 URL。"""
    with yt_dlp.YoutubeDL(_YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError("无法获取推文信息，请检查 URL 是否有效或推文是否包含视频")

    raw_formats = info.get("formats", [])

    return ParseResponse(
        platform="twitter",
        title=info.get("description") or info.get("title", "X 视频"),
        author=info.get("uploader") or info.get("uploader_id"),
        thumbnail=info.get("thumbnail"),
        duration=int(info.get("duration") or 0) or None,
        formats=Formats(
            video=_pick_video_formats(raw_formats),
            audio=[],        # X 平台通常不提供独立音频流
            subtitles=[],    # X 不提供字幕
        ),
    )
