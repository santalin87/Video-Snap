"""
/api/parse 路由

接收 URL → 识别平台 → 分发到对应解析服务 → 返回格式列表
"""
import yt_dlp
from fastapi import APIRouter, HTTPException

from ..models import ErrorResponse, ParseRequest, ParseResponse
from ..services import douyin, twitter, youtube
from ..services.detector import Platform, detect_platform

router = APIRouter()


@router.post(
    "/parse",
    response_model=ParseResponse,
    responses={
        400: {"model": ErrorResponse, "description": "URL 无效或平台不支持"},
        422: {"model": ErrorResponse, "description": "解析失败"},
    },
    summary="解析视频 URL",
    description="输入视频链接，返回可用的视频/音频/字幕直链列表，不经过服务器下载。",
)
async def parse_url(body: ParseRequest):
    url = body.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL 不能为空")

    platform = detect_platform(url)

    if platform == Platform.UNKNOWN:
        raise HTTPException(
            status_code=400,
            detail="不支持的平台，目前支持：YouTube、Twitter/X、抖音、TikTok",
        )

    try:
        if platform == Platform.YOUTUBE:
            result = youtube.parse(url)
        elif platform == Platform.TWITTER:
            result = twitter.parse(url)
        elif platform == Platform.DOUYIN:
            result = douyin.parse(url, platform="douyin")
        elif platform == Platform.TIKTOK:
            result = douyin.parse(url, platform="tiktok")
        else:
            raise HTTPException(status_code=400, detail="未知平台")

    except yt_dlp.utils.DownloadError as e:
        # yt-dlp 的错误通常包含详细原因
        msg = str(e)
        if "Private video" in msg:
            detail = "该视频为私密视频，无法解析"
        elif "This video is not available" in msg:
            detail = "该视频不可用（可能已删除或地区限制）"
        elif "Sign in" in msg or "login" in msg.lower():
            detail = "该内容需要登录才能访问"
        else:
            detail = f"解析失败：{msg[:200]}"
        raise HTTPException(status_code=422, detail=detail)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{str(e)[:200]}")

    # 检查是否解析到了有效格式
    has_content = (
        result.formats.video
        or result.formats.audio
        or result.formats.subtitles
    )
    if not has_content:
        raise HTTPException(
            status_code=422,
            detail="未能解析到可下载的格式，该视频可能受版权保护或需要登录",
        )

    return result
