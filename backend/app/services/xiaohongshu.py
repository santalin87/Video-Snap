"""
小红书解析服务 — 专属解析，不走 yt-dlp 通用提取器

原因：实测 yt-dlp 自带的 XiaoHongShu 提取器对分享短链解析出的笔记
会报“No video formats found”（2026.08.19 版），而笔记页本身是视频笔记，
HTML 里就有带签名的 MP4 直链。所以直接按小红书自己的页面结构取：

- 短链（xhslink.cn / xhslink.com）用移动端 UA 跟随跳转到 discovery/item；
- 笔记页用移动端 UA 抓取（桌面 UA 会被超时/拦截，移动端 UA 实测可达）；
- 从页面 __INITIAL_STATE__ 里的 stream.h264/h265 条目取 master_url，
  每条自带 width / height / size / duration，http 转 https 后即为可下载直链；
- 签名是按次生成的、短时间过期：解析出来请马上下载，过期后重新解析一次即可。

只做视频笔记：没有视频流的笔记（纯图文）返回明确错误，不假装成功。
"""

import os
import re

import httpx

from ..models import Formats, ParseResponse, VideoFormat

MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)


def _last_int(segment: str, key: str):
    m = re.findall(r'"%s":(\d+)' % key, segment)
    return int(m[-1]) if m else None


def _last_str(segment: str, key: str):
    m = re.findall(r'"%s":"([^"]+)"' % key, segment)
    return m[-1] if m else None


def _bytes_to_mb(size):
    return round(size / (1024 * 1024), 1) if size else None


def parse(url: str) -> ParseResponse:
    """解析小红书笔记链接（含 xhslink 短链），返回视频直链列表。"""
    headers = {"User-Agent": MOBILE_UA, "Referer": "https://www.xiaohongshu.com/"}
    try:
        # 代理只显式取 https_proxy/http_proxy 一个值，不走 trust_env：
        # 某些环境的 no_proxy 含方括号 IPv6 写法，httpx 按环境变量建代理表时会直接
        # 抛 InvalidURL；显式传单个代理则没有这个问题，没有代理变量时直连。
        proxy = (
            os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
            or os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
        )
        with httpx.Client(follow_redirects=True, timeout=30.0, headers=headers,
                          trust_env=False, proxy=proxy) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as e:
        raise ValueError(f"小红书页面抓取失败：{e}")

    # 页面里的 JSON 用 \u002F 转义斜杠、用 \" 转义引号，先还原再用正则取流信息
    text = resp.text.replace("\\u002F", "/").replace('\\"', '"')

    formats = []
    seen = set()
    for m in re.finditer(r'master_url":"(https?://[^"]+)"', text):
        raw_url = m.group(1)
        # 下载代理只接受 https，http 直链统一转 https（实测 https 可用）
        direct = raw_url.replace("http://", "https://", 1)
        if direct in seen:
            continue
        seen.add(direct)
        seg = text[max(0, m.start() - 1500):m.start()]
        width = _last_int(seg, "width")
        height = _last_int(seg, "height")
        size = _last_int(seg, "size")
        duration_ms = _last_int(seg, "duration")
        codec = _last_str(seg, "video_codec")
        formats.append({
            "url": direct,
            "height": height,
            "width": width,
            "size": size,
            "duration_ms": duration_ms,
            "codec": codec,
        })

    if not formats:
        raise ValueError("该小红书笔记没有视频（可能是纯图文笔记），或需要登录才能查看")

    # 同分辨率可能有多档（不同编码/码率），按文件大小降序，大的在前
    formats.sort(key=lambda f: (-(f["height"] or 0), -(f["size"] or 0)))

    video_formats = []
    for f in formats:
        video_formats.append(VideoFormat(
            quality=f"{f['height']}p" if f["height"] else "标准",
            ext="mp4",
            size_mb=_bytes_to_mb(f["size"]),
            url=f["url"],
            note=f["codec"].upper() if f["codec"] else None,
        ))

    # 标题/封面优先用 <meta og:*>（稳定）；作者用 JSON-LD 的 author.name。
    # 注意：页面正文里第一个 "nickname" 是评论区用户，不是作者，不能直接取。
    title = None
    title_m = re.search(r'<meta[^>]+(?:property|name)="og:title"[^>]+content="([^"]+)"', resp.text)
    if not title_m:
        title_m = re.search(r'<title>([^<]+)</title>', resp.text)
    if title_m:
        title = title_m.group(1).replace(" - 小红书", "").strip()
    if not title:
        t2 = re.search(r'"title":"([^"]+)"', text)
        title = t2.group(1) if t2 else "小红书视频"
    author_m = re.search(
        r'"author":\s*\{\s*"@type":\s*"Person",\s*"name":\s*"([^"]+)"', text)
    thumb_m = re.search(r'<meta[^>]+(?:property|name)="og:image"[^>]+content="([^"]+)"', resp.text)
    duration = None
    for f in formats:
        if f["duration_ms"]:
            duration = int(f["duration_ms"] / 1000) or None
            break

    return ParseResponse(
        platform="xiaohongshu",
        title=title,
        author=author_m.group(1) if author_m else None,
        thumbnail=thumb_m.group(1) if thumb_m else None,
        duration=duration,
        formats=Formats(video=video_formats, audio=[], subtitles=[]),
    )
