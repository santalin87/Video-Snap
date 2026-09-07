# VidSnap

> 自托管多平台视频解析下载工具 — NewPipe 模式，VPS 零流量消耗

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-blue)](https://santalin87.github.io/Video-Snap/)

**🌐 在线使用：** [santalin87.github.io/Video-Snap](https://santalin87.github.io/Video-Snap/)

---

## 功能

- **一键解析**：粘贴链接 → 自动识别平台 → 返回所有格式直链
- **NewPipe 模式**：视频直接从平台 CDN 下载，**不经过 VPS 转发**，月流量几乎为零
- **多格式支持**：
  - 🎬 视频（≤720p，含音频，下载即可播放）
  - 🎵 纯音频（M4A / MP3）
  - 📄 字幕（SRT / VTT，仅 YouTube）
- **多平台支持**：YouTube、Twitter/X、抖音、TikTok
- **自动部署**：Push 到 `main` 分支自动更新 GitHub Pages

## 支持平台

| 平台 | 视频 | 音频 | 字幕 | 备注 |
|------|:----:|:----:|:----:|------|
| YouTube | ✅ | ✅ | ✅ | ≤720p 音视频合并，720p+ 分离 |
| Twitter / X | ✅ | — | — | 含音频，平台原始画质 |
| 抖音 | ✅ | — | — | 无水印版 |
| TikTok | ✅ | — | — | 无水印版 |

## 架构

```
用户浏览器
    ↕ 访问页面
GitHub Pages (前端)
    ↕ API 请求（JSON，几 KB）
Cloudflare (DNS + SSL)
    ↕ HTTP 转发
GCP VPS (后端 FastAPI + yt-dlp)
    ↕ 返回直链
用户浏览器 ←──── Platform CDN（视频流，不经过 VPS）
```

---

## 部署指南

### 1. 前置准备

- 一个 GitHub 账号（已有）
- Google Cloud Free Tier VPS（e2-micro）
- 一个域名（任意注册商，转入 Cloudflare 管理）

### 2. VPS 设置

```bash
# SSH 进入 VPS
ssh user@your-vps-ip

# 安装 Docker（Ubuntu）
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# 克隆仓库
git clone https://github.com/santalin87/Video-Snap.git
cd Video-Snap

# 配置环境变量
cp .env.example .env
nano .env
# 修改 ALLOWED_ORIGINS，填入你的 GitHub Pages 地址和 API 域名

# 启动（仅后端）
docker compose -f docker-compose.vps.yml up -d

# 验证
curl http://localhost/api/health
# → {"status":"ok","yt_dlp_version":"..."}
```

### 3. Cloudflare 设置

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择你的域名 → **DNS** → **添加记录**：
   ```
   类型: A
   名称: api          （即 api.yourdomain.com）
   IPv4: 你的 VPS 外部 IP
   代理状态: 已代理（橙色云朵 ✅）
   ```
3. **SSL/TLS** → 加密模式选 **"灵活"**（Flexible）
   - Cloudflare ↔ 用户之间用 HTTPS
   - Cloudflare ↔ VPS 之间用 HTTP（VPS 无需配置证书）

### 4. GitHub 设置

**Step 1** — 开启 GitHub Pages：
- 仓库 → **Settings** → **Pages**
- Source 选 **GitHub Actions**

**Step 2** — 添加 Secret：
- 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
  ```
  Name:  VITE_API_BASE_URL
  Value: https://api.yourdomain.com
  ```

**Step 3** — 触发部署：
```bash
git commit --allow-empty -m "trigger: deploy to GitHub Pages"
git push
```

等 1-2 分钟后访问 `https://santalin87.github.io/Video-Snap/` 即可使用。

---

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

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11 + FastAPI + yt-dlp |
| 前端 | Vue 3 + Vite |
| 部署 | Docker Compose + GitHub Actions |
| CDN/SSL | Cloudflare |
| 托管 | Google Cloud Free VPS + GitHub Pages |

## 免责声明

本项目仅供个人学习和研究使用。请遵守各平台服务条款，不得用于侵犯版权或商业用途。

## License

MIT
