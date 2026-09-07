import re
from enum import Enum


class Platform(str, Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    DOUYIN = "douyin"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"


# 平台匹配规则
_PATTERNS = {
    Platform.YOUTUBE: [
        r"youtube\.com/watch",
        r"youtube\.com/shorts/",
        r"youtu\.be/",
        r"youtube\.com/live/",
    ],
    Platform.TWITTER: [
        r"twitter\.com/.+/status/",
        r"x\.com/.+/status/",
    ],
    Platform.DOUYIN: [
        r"douyin\.com/",
        r"iesdouyin\.com/",
        r"v\.douyin\.com/",
    ],
    Platform.TIKTOK: [
        r"tiktok\.com/",
        r"vm\.tiktok\.com/",
    ],
}


def detect_platform(url: str) -> Platform:
    """根据 URL 识别平台。"""
    for platform, patterns in _PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return platform
    return Platform.UNKNOWN


def is_supported(url: str) -> bool:
    return detect_platform(url) != Platform.UNKNOWN
