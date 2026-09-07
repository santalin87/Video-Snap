from pydantic import BaseModel
from typing import Optional


class ParseRequest(BaseModel):
    url: str


class VideoFormat(BaseModel):
    quality: str          # 如 "720p", "480p"
    ext: str              # 如 "mp4", "webm"
    size_mb: Optional[float] = None
    url: str
    note: Optional[str] = None


class AudioFormat(BaseModel):
    quality: str          # 如 "高品质", "标准"
    ext: str              # 如 "m4a", "mp3"
    abr: Optional[int] = None   # 码率 kbps
    url: str


class SubtitleFormat(BaseModel):
    lang: str             # 如 "zh-Hans", "en"
    label: str            # 如 "中文（简体）", "English"
    ext: str              # 如 "srt", "vtt"
    url: str


class Formats(BaseModel):
    video: list[VideoFormat] = []
    audio: list[AudioFormat] = []
    subtitles: list[SubtitleFormat] = []


class ParseResponse(BaseModel):
    platform: str
    title: str
    author: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[int] = None   # 秒
    formats: Formats


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
