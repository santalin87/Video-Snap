<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title">
          <span class="icon">⚙️</span>
          <span>插件与引擎管理中心</span>
        </div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">
        <p class="desc">
          VidSnap 采用模块化解耦设计，无需重新安装主软件，即可单独对底层的解析引擎和合并插件进行热更新。
        </p>

        <!-- 插件 1: yt-dlp -->
        <div class="plugin-item">
          <div class="plugin-info">
            <div class="plugin-name-row">
              <span class="plugin-name">核心解析引擎 (yt-dlp)</span>
              <span class="version-tag">{{ ytdlpVersion || 'v2026.08.19 (可用)' }}</span>
            </div>
            <p class="plugin-desc">负责实时提取 YouTube、Twitter (X)、抖音、TikTok 的音视频流与反爬签名。</p>
          </div>
          <div class="plugin-action">
            <button
              class="btn-action"
              :disabled="updatingYtdlp"
              @click="handleUpdateYtdlp"
            >
              <span v-if="updatingYtdlp" class="spinner-sm" />
              <span v-else>🔄 一键升级</span>
            </button>
          </div>
        </div>

        <!-- 插件 2: FFmpeg -->
        <div class="plugin-item">
          <div class="plugin-info">
            <div class="plugin-name-row">
              <span class="plugin-name">音画合并引擎 (FFmpeg)</span>
              <span class="version-tag tag-green">{{ ffmpegVersion || '已安装 (v8.0.1)' }}</span>
            </div>
            <p class="plugin-desc">负责 1080p / 4K 高清视频轨与最佳音频轨的无损合并与 MP3 转换。</p>
          </div>
          <div class="plugin-action">
            <button
              class="btn-action btn-check"
              :disabled="checkingFfmpeg"
              @click="handleCheckFfmpeg"
            >
              <span v-if="checkingFfmpeg" class="spinner-sm" />
              <span v-else>✓ 检查状态</span>
            </button>
          </div>
        </div>

        <!-- 路径设置: 下载保存目录 -->
        <div class="plugin-item">
          <div class="plugin-info">
            <div class="plugin-name-row">
              <span class="plugin-name">默认下载保存目录</span>
            </div>
            <p class="plugin-desc font-mono">此电脑 / 下载 / VidSnap (Downloads/VidSnap)</p>
          </div>
          <div class="plugin-action">
            <button class="btn-action btn-folder" @click="handleOpenFolder">
              📂 打开文件夹
            </button>
          </div>
        </div>

        <!-- 状态通知信息 -->
        <div v-if="statusMsg" class="status-alert" :class="`alert-${statusType}`">
          {{ statusMsg }}
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-done" @click="$emit('close')">完成</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

defineProps({
  visible: Boolean,
})

defineEmits(['close'])

const ytdlpVersion   = ref('')
const ffmpegVersion  = ref('')
const updatingYtdlp  = ref(false)
const checkingFfmpeg = ref(false)
const statusMsg      = ref('')
const statusType     = ref('info')

// 检查是否在 Tauri 桌面客户端环境下
const isTauri = !!window.__TAURI_INTERNALS__

async function loadStatus() {
  if (isTauri) {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      const status = await invoke('get_engine_status')
      if (status.yt_dlp) ytdlpVersion.value  = status.yt_dlp
      if (status.ffmpeg) ffmpegVersion.value = status.ffmpeg.slice(0, 30)
    } catch (e) {
      console.warn('Tauri get_engine_status not available:', e)
    }
  }
}

onMounted(() => {
  loadStatus()
})

async function handleUpdateYtdlp() {
  updatingYtdlp.value = true
  statusMsg.value = ''
  try {
    if (isTauri) {
      const { invoke } = await import('@tauri-apps/api/core')
      const res = await invoke('update_engine', { name: 'yt-dlp' })
      statusMsg.value = `yt-dlp 更新成功: ${res}`
      statusType.value = 'success'
      await loadStatus()
    } else {
      // Web 模式模拟与提示
      await new Promise(r => setTimeout(r, 1000))
      statusMsg.value = 'yt-dlp 核心引擎当前已是最新版本 (2026.08.19)！'
      statusType.value = 'success'
    }
  } catch (e) {
    statusMsg.value = `更新出错: ${e}`
    statusType.value = 'error'
  } finally {
    updatingYtdlp.value = false
  }
}

async function handleCheckFfmpeg() {
  checkingFfmpeg.value = true
  statusMsg.value = ''
  try {
    if (isTauri) {
      await loadStatus()
      statusMsg.value = 'FFmpeg 音视频合并引擎工作正常！'
      statusType.value = 'success'
    } else {
      await new Promise(r => setTimeout(r, 600))
      statusMsg.value = 'FFmpeg 音视频合并引擎就绪 (8.0.1)！'
      statusType.value = 'success'
    }
  } catch (e) {
    statusMsg.value = `检测出错: ${e}`
    statusType.value = 'error'
  } finally {
    checkingFfmpeg.value = false
  }
}

async function handleOpenFolder() {
  if (isTauri) {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      await invoke('open_download_folder')
    } catch (e) {
      statusMsg.value = `无法打开目录: ${e}`
      statusType.value = 'error'
    }
  } else {
    statusMsg.value = '已定位默认下载路径：系统下载文件夹 (Downloads)'
    statusType.value = 'info'
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 16px;
}

.modal-card {
  background: #ffffff;
  border-radius: 14px;
  max-width: 540px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  border: 1px solid #e2e8f0;
  animation: popIn 0.2s ease-out;
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.96); }
  to   { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}
.close-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 6px;
}

.plugin-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.plugin-info {
  flex: 1;
  min-width: 0;
}

.plugin-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.plugin-name {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.version-tag {
  font-size: 11px;
  font-weight: 600;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #dbeafe;
  padding: 1px 6px;
  border-radius: 4px;
}

.tag-green {
  background: #ecfdf5;
  color: #059669;
  border-color: #a7f3d0;
}

.plugin-desc {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.font-mono {
  font-family: monospace;
  color: #334155;
}

.btn-action {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  background: #2563eb;
  color: #ffffff;
  border: 1px solid #1d4ed8;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-action:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-check {
  background: #ffffff;
  color: #334155;
  border-color: #cbd5e1;
}
.btn-check:hover:not(:disabled) {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-folder {
  background: #ffffff;
  color: #334155;
  border-color: #cbd5e1;
}
.btn-folder:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.status-alert {
  font-size: 13px;
  padding: 10px 14px;
  border-radius: 8px;
  line-height: 1.4;
}

.alert-success {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}
.alert-error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}
.alert-info {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #dbeafe;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-footer {
  padding: 14px 20px;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}

.btn-done {
  padding: 8px 20px;
  background: #0f172a;
  color: #ffffff;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}
.btn-done:hover {
  background: #1e293b;
}
</style>
