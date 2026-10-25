"""
通用解析服务 — 不设平台白名单

已知平台（YouTube / X / 抖音 / TikTok）仍走各自的专属解析；
除此之外的任何链接都走到这里，直接交给 yt-dlp 的提取器处理。
yt-dlp 自带上千个站点的提取器（微博、B站、小红书、Instagram 等），
没必要在我们这一层再维护一份“允许的平台”名单去挡它。

格式筛选复用 youtube.py 的规则：只保留可直接下载的文件直链，
排除 m3u8 清单（浏览器拿清单当不成 mp4 下，返回了反而是坏结果）。
因此纯 HLS 的站点会走到“未能解析到可下载格式”，而不是静默给错文件。
"""

import os

import yt_dlp

from ..models import Formats, ParseResponse
from .youtube import _pick_audio_formats, _pick_subtitles, _pick_video_formats

_YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": False,
}

_PROXY = os.getenv("YTDLP_PROXY")
if _PROXY:
    _YDL_OPTS["proxy"] = _PROXY


def parse(url: str) -> ParseResponse:
    """用 yt-dlp 通用提取器解析任意平台的视频 URL。"""
    with yt_dlp.YoutubeDL(_YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError("无法获取视频信息，请检查 URL 是否有效")

    # 频道 / 合集页会返回 entries：取第一条带格式的条目
    if info.get("entries"):
        entries = [e for e in info["entries"] if isinstance(e, dict)]
        if entries:
            info = next(
                (e for e in entries if e.get("formats") or e.get("url")),
                entries[0],
            )

    raw_formats = info.get("formats", [])
    # 只有单条直链、没有 formats 列表的提取器（如某些短链）
    if not raw_formats and info.get("url"):
        raw_formats = [{"url": info["url"], "ext": info.get("ext", "mp4")}]

    platform = (info.get("extractor_key") or info.get("extractor") or "video").lower()

    formats = Formats(
        video=_pick_video_formats(raw_formats),
        audio=_pick_audio_formats(raw_formats),
        subtitles=_pick_subtitles(
            info.get("subtitles", {}),
            info.get("automatic_captions", {}),
        ),
    )

    return ParseResponse(
        platform=platform,
        title=info.get("title") or info.get("description") or "视频",
        author=info.get("uploader") or info.get("uploader_id") or info.get("creator"),
        thumbnail=info.get("thumbnail"),
        duration=int(info.get("duration") or 0) or None,
        formats=formats,
    )
