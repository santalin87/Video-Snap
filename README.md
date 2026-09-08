# 🎬 VidSnap (Video-Snap)

> 自托管多平台音视频极速解析与下载神器 —— 支持 **网页在线版** 与 **全平台原生桌面端**（Windows / macOS / Linux）

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Web%20App-在线体验-2563eb)](https://santalin87.github.io/Video-Snap/)
[![GitHub Releases](https://img.shields.io/badge/Desktop%20App-v1.0.0-059669)](https://github.com/santalin87/Video-Snap/releases)

---

## 📥 全端下载与在线访问

| 版本类型 | 运行平台 | 下载 / 访问地址 | 说明 |
|---|---|---|---|
| **🌐 网页在线版** | 手机 / 平板 / 任何电脑浏览器 | [santalin87.github.io/Video-Snap](https://santalin87.github.io/Video-Snap/) | 免安装，随开随用，零服务器流量直连 |
| **🪟 Windows 桌面端** | Windows 10 / 11 (64位) | [VidSnap_x64-setup.exe](https://github.com/santalin87/Video-Snap/releases/latest) | 原生 .exe 安装包与便携版，支持 4K/1080p 满速 |
| **🍏 macOS 桌面端** | macOS (Apple Silicon M系列 & Intel) | [VidSnap_universal.dmg](https://github.com/santalin87/Video-Snap/releases/latest) | 通用架构 .dmg，双击直接拖入 Applications |
| **🐧 Linux 桌面端** | Ubuntu / Debian / Arch 等主流发行版 | [VidSnap_amd64.AppImage](https://github.com/santalin87/Video-Snap/releases/latest) | 双击即跑的单文件 AppImage 与 .deb 包 |

---

## ⚖️ 网页端 vs 桌面端：功能对比与适用场景

VidSnap 针对不同使用场景做了双端分工，你可根据实际需求灵活选择：

| 功能特性 | 🌐 网页在线版 (Web) | 💻 桌面原生客户端 (Desktop) |
|---|:---:|:---:|
| **安装要求** | ❌ 无需安装，打开浏览器即用 | ✅ 绿色单文件安装包（仅 5~10 MB） |
| **支持设备** | 手机 (iOS/Android)、平板、电脑 | PC 电脑端 (Windows / macOS / Linux) |
| **抖音 / TikTok / X (无水印)** | ⭐⭐⭐⭐⭐ 满速直链下载 | ⭐⭐⭐⭐⭐ 本地满速下载 |
| **YouTube 纯音频提取 (MP3/M4A)** | ⭐⭐⭐⭐⭐ 一键提取直连 | ⭐⭐⭐⭐⭐ 一键提取转换 |
| **YouTube 1080p / 4K 高清视频** | ⚠️ 官方 CDN 跨 IP 限制约 20KB/s | 🚀 **100% 跑满本地宽带 (11Mbps+)** |
| **音画自动合并 (FFmpeg)** | 浏览器原生不支持合并 | ⚡ 内置/调用 FFmpeg 自动合成单文件 MP4 |
| **VPS 流量开销** | 🟢 仅耗极小文本 (零媒体流量) | 🟢 **完全不走 VPS，0 流量消耗** |
| **插件热升级 (yt-dlp/FFmpeg)** | 需更新 VPS 后端容器 | 🔄 **界面右上角一键热更新插件** |

---

## 🌟 核心亮点

### 1. 现代化极简黑白灰蓝交互设计
* 摈弃沉闷浮夸色彩，采用**极简白灰底色 + 纯正科技蓝/翡翠绿**的高级质感配色。
* **三行独立下拉面板**：
  * 🎬 **视频下载**：下拉挑选 4K / 1080p / 720p / 480p 等不同画质。
  * 🎵 **音频提取**：下拉挑选高品质 M4A、MP3 格式。
  * 📄 **字幕提取**：下拉挑选中文简体、中文繁体、英文等各类语言字幕。

### 2. 插件解耦与“一键热升级”控制中心（桌面端专属）
* 众所周知，视频平台（尤其是 YouTube）的反爬协议几乎每周都在更新。
* VidSnap 桌面端首创**插件与主程序解耦设计**：
  * 主界面右上角常驻 **`⚙️ 组件与引擎管理`** 按钮。
  * 核心解析引擎 (`yt-dlp`) 附带 **【🔄 一键升级】**：点击后后台自动拉取官方最新二进制补丁，**无需重新下载或安装整个桌面客户端**，永不过时！
  * 音视频合并引擎 (`FFmpeg`) 状态自检。

---

## 🚀 部署与使用指南

### 一、使用桌面端（最推荐）

1. 从 [Releases 页面](https://github.com/santalin87/Video-Snap/releases/latest) 下载对应操作系统的安装包。
2. 双击打开 `VidSnap`。
3. 复制视频链接，软件会自动识别剪贴板。
4. 下拉选择目标清晰度，点击下载，自动保存在 `此电脑 / 下载 / VidSnap` 文件夹中。

---

### 二、自建网页端（GitHub Pages + 免费 VPS）

如果你想自己搭建一套全天候在线的网页版：

#### 架构原理
```
用户浏览器 (https://santalin87.github.io/Video-Snap/)
   ↕ 发送解析请求 (约 50KB 文本)
Cloudflare (免费 SSL 加密 + 防火墙)
   ↕ HTTP:80 转发
Google Cloud 免费 VPS (仅跑 FastAPI 轻量解析引擎，不中转视频)
   ↕ 返回直链
用户浏览器 ◄──── 直连 YouTube / 抖音 / X 官方 CDN 下载 ────► 平台 CDN
```

#### 1. VPS 后端部署（只需 1 分钟）
```bash
# 登录 VPS 后拉取代码
git clone https://github.com/santalin87/Video-Snap.git
cd Video-Snap

# 准备环境变量并启动
cp .env.example .env
docker compose -f docker-compose.vps.yml up -d
```

#### 2. Cloudflare 配置
1. 添加 DNS `A` 记录：主机名 `api`，目标为你的 VPS 外部 IP，开启已代理（橙色云朵 ☁️）。
2. 在 **SSL/TLS** 中将加密模式设为 **灵活 (Flexible)** 或开启 **自动 SSL/TLS**。

#### 3. GitHub Pages 配置
1. 仓库 **Settings** ➔ **Pages** ➔ Source 选 **GitHub Actions**。
2. 仓库 **Settings** ➔ **Secrets and variables** ➔ **Actions** 添加一个密钥：
   * **Name**: `VITE_API_BASE_URL`
   * **Value**: `https://api.yourdomain.com`
3. Push 代码后 GitHub Actions 会全自动编译发布前端。

---

## 🛠️ 技术栈架构

* **前端 (Web & Desktop UI)**：Vue 3 + Vite + 原生 CSS (极简无依赖)
* **桌面跨平台框架 (Desktop Core)**：Rust + Tauri v2 (体积仅 5MB，内存仅 30MB)
* **后端解析引擎 (Backend API)**：Python 3.11 + FastAPI + 最新版 yt-dlp
* **流媒体处理**：FFmpeg (用于桌面端无损音画混流)
* **CI/CD 全自动化**：GitHub Actions 全平台矩阵构建 (Windows / macOS / Linux)

---

## ⚖️ 免责声明 (Disclaimer)

本项目仅供个人学习、网络技术研究以及备份自己拥有版权的内容使用。请严格遵守各流媒体平台的服务条款与版权政策，严禁用于任何商业牟利或侵权行为。

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 许可协议开源。
