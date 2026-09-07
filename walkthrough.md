# VidSnap (Video-Snap) 部署与使用指南

代码仓库：[https://github.com/santalin87/Video-Snap](https://github.com/santalin87/Video-Snap)

---

## 整体工作链路与架构

```
用户浏览器
    ↕ (1) 打开页面
GitHub Pages (https://santalin87.github.io/Video-Snap/)
    ↕ (2) 提交 URL 解析请求 (JSON, ~50KB)
Cloudflare (开启橙色云朵代理 HTTPS: https://api.yourdomain.com)
    ↕ (3) 转发到 VPS 80 端口
Google Cloud VPS (运行 FastAPI + yt-dlp，仅做元数据解析，零媒体流量中转)
    ↕ (4) 返回平台 CDN 直链 (包含画质、格式、音频、字幕)
用户浏览器 ────(5) 直连 YouTube/Twitter/抖音 CDN 下载视频────► 平台 CDN
```

---

## 三端配置 CheckList

### 1. GitHub 仓库配置（启用 Pages 自动构建）

1. 打开 [https://github.com/santalin87/Video-Snap](https://github.com/santalin87/Video-Snap)
2. **开启 GitHub Pages**：
   - 进入 `Settings` → `Pages`
   - 在 **Build and deployment** 下方的 **Source**，选择 **GitHub Actions**（不要选 Deploy from a branch）。
3. **配置后端 API 变量**：
   - 进入 `Settings` → `Secrets and variables` → `Actions`
   - 点击 **New repository secret**
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://api.yourdomain.com`（你在 Cloudflare 上绑定的后端域名，没有末尾斜杠）
4. **触发初次部署**：
   - 进入 `Actions` 标签页，在左侧选择 `部署到 GitHub Pages`，点击右侧的 **Run workflow** 手动触发一次构建。
   - 构建完成后，访问：`https://santalin87.github.io/Video-Snap/` 即可看到前端界面。

---

### 2. Cloudflare 配置（域名解析 + 免费 HTTPS + 隐藏 VPS 真实 IP）

1. 登录 Cloudflare 控制台，进入你的域名。
2. **添加 DNS A 记录**：
   - **Type**: `A`
   - **Name**: `api`（二级域名即 `api.yourdomain.com`）
   - **IPv4 address**: 你的 Google Cloud VPS 的公网 IP
   - **Proxy status**: **Proxied（已代理，橙色小云朵开启）** —— 这会让 Cloudflare 自动签发 SSL 证书，并防护 VPS。
3. **设置 SSL 加密模式**：
   - 进入 `SSL/TLS` 菜单。
   - 将加密模式设为 **Flexible（灵活）**。
   - *原理*：浏览器到 Cloudflare 走安全的 HTTPS，Cloudflare 到 VPS 走标准 HTTP 80 端口，VPS 内部无需繁琐配置 Nginx SSL 证书。

---

### 3. Google Cloud VPS 配置（运行轻量解析引擎）

登录你的 GCP VPS 终端（SSH）：

```bash
# 1. 确保安装了 Docker 和 Git
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# 2. 拉取仓库代码
git clone https://github.com/santalin87/Video-Snap.git
cd Video-Snap

# 3. 复制并调整环境变量
cp .env.example .env
nano .env
```

在 `.env` 中确认 `ALLOWED_ORIGINS` 包含你的 Pages 地址和 API 域名：
```env
ALLOWED_ORIGINS=https://santalin87.github.io,https://api.yourdomain.com
```

启动后端容器：
```bash
# 运行专为 VPS 设计的独立后端 compose 文件（映射 80 端口到容器 8000）
docker compose -f docker-compose.vps.yml up -d
```

验证后端是否正常运行：
```bash
curl http://localhost/api/health
# 正常应返回: {"status":"ok","yt_dlp_version":"..."}
```

---

## 验证与验收

1. 浏览器访问：`https://santalin87.github.io/Video-Snap/`
2. 粘贴任一 YouTube / Twitter(X) / 抖音链接，点击**解析**。
3. 弹出视频封面、标题、音频流与字幕列表，点击格式后面的下载图标即可直接通过浏览器拉取 CDN 媒体流。
