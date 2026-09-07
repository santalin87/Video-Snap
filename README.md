# downX

> 自托管多平台视频解析下载工具 — NewPipe 模式，VPS 零流量消耗

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 功能

- **一键解析**：粘贴链接自动识别平台，返回所有可用格式直链
- **NewPipe 模式**：视频直接从平台 CDN 下载到本地，**不经过 VPS 转发**
- **多格式支持**：
  - 🎬 视频（≤720p 含音频，下载后直接有声音）
  - 🎵 纯音频（M4A / MP3）
  - 📄 字幕（SRT / VTT，仅 YouTube）
- **多平台支持**：YouTube、Twitter/X、抖音、TikTok

## 支持平台

| 平台 | 视频 | 音频 | 字幕 | 最高画质 |
|------|:----:|:----:|:----:|---------|
| YouTube | ✅ | ✅ | ✅ | 720p（预合并） |
| Twitter / X | ✅ | — | — | 平台最高画质 |
| 抖音 | ✅（无水印）| — | — | 平台原始画质 |
| TikTok | ✅（无水印）| — | — | 平台原始画质 |

> **关于 YouTube 1080p+**：YouTube 的 1080p 以上使用 DASH 格式（视频和音频分离），需要 `ffmpeg` 合并，本项目暂不支持服务端合并。如需 1080p+，可手动下载视频流和音频流后使用 `ffmpeg -i video.mp4 -i audio.m4a -c copy output.mp4` 合并。

## 快速部署（Docker）

### 前提

- Docker + Docker Compose
- VPS 或本地机器

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/downX.git
cd downX

# 2. 创建环境变量文件
cp .env.example .env
# 编辑 .env，按需修改（通常默认值即可）

# 3. 一键启动
docker compose up -d

# 4. 访问
# 浏览器打开 http://YOUR_VPS_IP
```

### 更新

```bash
git pull
docker compose up -d --build
```

## 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端（新开终端）
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS 允许的来源 |
| `YTDLP_PROXY` | 空 | yt-dlp 代理地址（如 `socks5://...`） |
| `FRONTEND_PORT` | `80` | 前端暴露端口 |

## 技术栈

- **后端**：Python 3.11 + FastAPI + yt-dlp
- **前端**：Vue 3 + Vite + 原生 CSS
- **部署**：Docker Compose + Nginx

## 免责声明

本项目仅供个人学习和研究使用。请遵守各平台的服务条款，不得用于任何商业用途或侵犯版权的行为。

## License

MIT
