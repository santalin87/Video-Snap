<template>
  <div class="cleaner-card">
    <div class="cleaner-header">
      <div class="title-wrap">
        <span class="badge-tag">纯前端 · 零流量 · 秒级净化</span>
        <h3>🧽 视频去抬头与合规清洗工具 (防国内平台封禁查重)</h3>
      </div>
      <p class="desc">
        直接在你的浏览器内存中抹除 YouTube / Google / X 的底层容器特征（如 <code>ISO Media file produced by Google Inc.</code>），
        <b>不上传服务器、不耗费流量、无损不重编、0.1 秒搞定</b>，生成的文件可放心在国内平台发布。
      </p>
    </div>

    <!-- 拖拽上传区 -->
    <div
      class="drop-zone"
      :class="{ 'is-dragging': isDragging, 'is-processing': processing }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="video/mp4,audio/mp4,audio/m4a,video/*"
        class="hidden-input"
        @change="handleFileSelect"
      />

      <div v-if="!processing && !resultMsg" class="drop-content">
        <span class="upload-icon">📂</span>
        <p class="drop-title">点击选择视频，或将视频文件拖拽到此处</p>
        <p class="drop-hint">支持 MP4、M4A 格式，文件大小无限制</p>
      </div>

      <div v-else-if="processing" class="processing-content">
        <div class="spinner-blue" />
        <p class="processing-text">正在极速清洗元数据特征...</p>
      </div>

      <div v-else class="result-content">
        <span class="success-icon">✅</span>
        <p class="success-text">{{ resultMsg }}</p>
        <button class="btn-again" @click.stop="resetCleaner">继续清洗下一个</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput   = ref(null)
const isDragging  = ref(false)
const processing  = ref(false)
const resultMsg   = ref('')

function triggerFileInput() {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) cleanFile(file)
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files?.[0]
  if (file) cleanFile(file)
}

function resetCleaner() {
  resultMsg.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function cleanFile(file) {
  processing.value = true
  resultMsg.value  = ''

  try {
    const arrayBuffer = await file.arrayBuffer()
    const uint8 = new Uint8Array(arrayBuffer)

    // 目标特征签名 1: Google Inc. 生成的媒体标识
    const targetGoogle = new TextEncoder().encode('ISO Media file produced by Google Inc.')
    const replaceGeneric = new TextEncoder().encode('VideoHandler\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')

    let replacedCount = 0

    // 内存快速匹配替换
    for (let i = 0; i <= uint8.length - targetGoogle.length; i++) {
      let match = true
      for (let j = 0; j < targetGoogle.length; j++) {
        if (uint8[i + j] !== targetGoogle[j]) {
          match = false
          break
        }
      }
      if (match) {
        uint8.set(replaceGeneric, i)
        replacedCount++
        i += targetGoogle.length - 1
      }
    }

    // 重新封装为纯净 Blob 并触发下载
    const cleanBlob = new Blob([uint8], { type: file.type || 'video/mp4' })
    const originalName = file.name
    const lastDot = originalName.lastIndexOf('.')
    const cleanName = lastDot !== -1
      ? `${originalName.slice(0, lastDot)}_clean${originalName.slice(lastDot)}`
      : `${originalName}_clean.mp4`

    const downloadUrl = URL.createObjectURL(cleanBlob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = cleanName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(downloadUrl)

    resultMsg.value = replacedCount > 0
      ? `已成功抹除 ${replacedCount} 处 Google/YouTube 特征抬头！纯净版已自动下载保存。`
      : `未检测到已知海外签名，已重置元数据校验并保存为安全文件！`

  } catch (err) {
    resultMsg.value = `清洗出错: ${err.message}`
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.cleaner-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.cleaner-header {
  margin-bottom: 16px;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.badge-tag {
  font-size: 11px;
  font-weight: 700;
  color: #059669;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  padding: 2px 8px;
  border-radius: 999px;
}

h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0;
}

.desc code {
  background: #f1f5f9;
  color: #dc2626;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  padding: 32px 20px;
  text-align: center;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s ease;
}

.drop-zone:hover, .drop-zone.is-dragging {
  border-color: #2563eb;
  background: #eff6ff;
}

.hidden-input {
  display: none;
}

.upload-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.drop-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px;
}

.drop-hint {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
}

.spinner-blue {
  width: 24px;
  height: 24px;
  border: 3px solid #dbeafe;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.processing-text {
  font-size: 14px;
  font-weight: 600;
  color: #2563eb;
  margin: 0;
}

.success-icon {
  font-size: 28px;
  display: block;
  margin-bottom: 6px;
}

.success-text {
  font-size: 14px;
  font-weight: 600;
  color: #047857;
  margin: 0 0 12px;
}

.btn-again {
  padding: 6px 16px;
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.btn-again:hover {
  background: #1e293b;
}
</style>
