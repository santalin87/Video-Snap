"""
FastAPI 应用入口
"""
import os
import yt_dlp
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.parse import router as parse_router

load_dotenv()

app = FastAPI(
    title="downX API",
    description="自托管多平台视频解析服务（NewPipe 模式）",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS 配置
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# 注册路由
app.include_router(parse_router, prefix="/api")


@app.get("/api/health", tags=["系统"])
async def health():
    """健康检查，返回服务状态和 yt-dlp 版本。"""
    return {
        "status": "ok",
        "yt_dlp_version": yt_dlp.version.__version__,
    }
