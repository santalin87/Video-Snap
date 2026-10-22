<template>
  <div class="cleaner-card">
    <div class="cleaner-header">
      <div class="title-wrap">
        <span class="badge-tag">纯前端 · 零上传 · 无损流拷贝</span>
        <h3>🧽 视频去抬头与合规清洗工具 (防国内平台封禁查重)</h3>
      </div>
      <p class="desc">
        深度清洗：在浏览器本地用 FFmpeg 对视频做<b>流拷贝重封装</b>，剥除 H.264 / HEVC 码流里的平台 SEI 标记，
        清空容器元数据与章节，重写编码器标识，并可伪装成 Premiere Pro / DaVinci Resolve / CapCut 的导出文件。
        <b>不上传服务器、不重编、画质零损失</b>，生成的文件可放心在国内平台发布。
      </p>
    </div>

    <!-- 拖拽上传区 -->
    <div
      class="drop-zone"
      :class="{ 'is-dragging': isDragging, 'is-processing': busy }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="video/mp4,video/quicktime,audio/mp4,audio/m4a,.mp4,.mov,.m4a"
        class="hidden-input"
        @change="handleFileSelect"
      />

      <div v-if="!selectedFile" class="drop-content">
        <span class="upload-icon">📂</span>
        <p class="drop-title">点击选择视频，或将视频文件拖拽到此处</p>
        <p class="drop-hint">支持 MP4、MOV、M4A，最大 500 MB · 首次使用需加载约 30MB 视频引擎（仅一次）</p>
      </div>

      <div v-else class="file-content" @click.stop>
        <span class="upload-icon">🎬</span>
        <p class="file-name">{{ selectedFile.name }}</p>
        <p class="drop-hint">{{ fmtSize(selectedFile.size) }} · 点击上方区域可重新选择</p>
      </div>
    </div>

    <!-- 预设与操作 -->
    <div v-if="selectedFile" class="controls" @click.stop>
      <label class="preset-label" for="presetSel">伪装导出预设</label>
      <select id="presetSel" v-model="presetKey" class="preset-select" :disabled="busy">
        <option v-for="(p, k) in PRESETS" :key="k" :value="k">{{ p.label }}</option>
      </select>

      <div v-if="busy" class="progress-wrap">
        <div class="progress-bar" :style="{ width: progressPct + '%' }" />
      </div>
      <p v-if="statusText" class="status-text" :class="{ 'is-error': isError }">{{ statusText }}</p>

      <div class="action-row">
        <button v-if="!downloadUrl" class="btn-clean" :disabled="busy" @click="runClean">
          {{ busy ? '清洗中…' : '开始深度清洗' }}
        </button>
        <a
          v-if="downloadUrl"
          class="btn-download"
          :href="downloadUrl"
          :download="downloadName"
        >⬇ 下载净化文件（{{ fmtSize(resultSize) }}）</a>
        <button v-if="downloadUrl || isError" class="btn-again" @click="resetCleaner">继续清洗下一个</button>
      </div>
      <p class="trust-line">处理全程在本机浏览器内存中完成，文件不会离开你的设备；流拷贝不重编，通常数秒完成。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FFmpeg } from '@ffmpeg/ffmpeg'
import { toBlobURL, fetchFile } from '@ffmpeg/util'
import {
  PRESETS, MAX_FILE, WARN_FILE,
  parseProbeLog, buildCleanArgs, patchEncoder, stripGoogleSignature, outputName,
} from '../utils/deepClean.js'

const CORE_BASE = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.6/dist/esm'

const fileInput   = ref(null)
const isDragging  = ref(false)
const selectedFile = ref(null)
const presetKey   = ref('davinci')
const busy        = ref(false)
const statusText  = ref('')
const isError     = ref(false)
const progressPct = ref(0)
const downloadUrl = ref('')
const downloadName = ref('')
const resultSize  = ref(0)

let ffmpeg = null
let engineLoaded = false
let probeLog = ''

const preset = computed(() => PRESETS[presetKey.value])

function fmtSize(b) {
  return b > 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.round(b / 1024) + ' KB'
}

function setStatus(t, err = false) {
  statusText.value = t
  isError.value = err
}

function triggerFileInput() {
  if (busy.value) return
  fileInput.value?.click()
}

function handleFileSelect(e) {
  const f = e.target.files?.[0]
  if (f) pick(f)
}

function handleDrop(e) {
  isDragging.value = false
  if (busy.value) return
  const f = e.dataTransfer.files?.[0]
  if (f) pick(f)
}

function pick(f) {
  clearResult()
  if (f.size > MAX_FILE) {
    selectedFile.value = null
    setStatus(`文件过大（${fmtSize(f.size)}），最大支持 500 MB。`, true)
    return
  }
  selectedFile.value = f
  setStatus(
    f.size > WARN_FILE
      ? '已选择大文件：手机内存有限时可能较慢，请耐心等待。'
      : ''
  )
}

function clearResult() {
  if (downloadUrl.value) URL.revokeObjectURL(downloadUrl.value)
  downloadUrl.value = ''
  downloadName.value = ''
  resultSize.value = 0
  progressPct.value = 0
}

function resetCleaner() {
  selectedFile.value = null
  clearResult()
  setStatus('')
  if (fileInput.value) fileInput.value.value = ''
}

async function ensureEngine() {
  if (engineLoaded) return
  if (!ffmpeg) {
    ffmpeg = new FFmpeg()
    ffmpeg.on('log', ({ message }) => { probeLog += message + '\n' })
    ffmpeg.on('progress', ({ progress }) => {
      const pct = Math.max(0, Math.min(100, Math.round((progress || 0) * 100)))
      // 清洗阶段进度映射到 30%~85% 区间
      progressPct.value = Math.max(progressPct.value, 30 + Math.round(pct * 0.55))
    })
  }
  setStatus('正在加载视频引擎（约 30MB，仅首次）…')
  await ffmpeg.load({
    coreURL: await toBlobURL(`${CORE_BASE}/ffmpeg-core.js`, 'text/javascript'),
    wasmURL: await toBlobURL(`${CORE_BASE}/ffmpeg-core.wasm`, 'application/wasm'),
  })
  engineLoaded = true
}

async function runClean() {
  const file = selectedFile.value
  if (!file || busy.value) return
  busy.value = true
  clearResult()
  progressPct.value = 5

  const inName = 'in_' + file.name.replace(/[^a-zA-Z0-9.]/g, '_')
  const { outFile, download } = outputName(file.name, preset.value)

  try {
    await ensureEngine()

    await ffmpeg.writeFile(inName, await fetchFile(file))

    // 1) 探测流构成：无音轨不强写音频流参数
    setStatus('正在探测媒体流…')
    progressPct.value = 20
    probeLog = ''
    await ffmpeg.exec(['-i', inName]).catch(() => 1)
    const streams = parseProbeLog(probeLog)

    // 2) 流拷贝重封装 + 清元数据/章节 + 剥 SEI
    setStatus('正在深度清洗（重封装 + 剥除平台标记）…')
    progressPct.value = 30
    const args = buildCleanArgs({
      inName, outName: outFile, preset: preset.value,
      hasVideo: streams.hasVideo, hasAudio: streams.hasAudio,
    })
    const code = await ffmpeg.exec(args)
    if (code !== 0) throw new Error('FFmpeg 处理失败（退出码 ' + code + '），文件可能不受支持')

    // 3) 等长补丁重写编码器标识 + Google 签名安全网
    setStatus('正在重写编码器标识…')
    progressPct.value = 90
    let data = await ffmpeg.readFile(outFile)
    if (typeof data === 'string') throw new Error('读取处理结果失败')
    data = patchEncoder(data, preset.value.tool)
    stripGoogleSignature(data)

    const blob = new Blob([data.buffer], { type: 'video/mp4' })
    downloadUrl.value = URL.createObjectURL(blob)
    downloadName.value = download
    resultSize.value = blob.size
    progressPct.value = 100
    setStatus(`✅ 清洗完成！已伪装为 ${preset.value.label} 导出文件，元数据与平台标记已清净。`)
  } catch (err) {
    console.error(err)
    setStatus('清洗出错: ' + (err?.message || err), true)
  } finally {
    if (ffmpeg && engineLoaded) {
      await ffmpeg.deleteFile(inName).catch(() => {})
      await ffmpeg.deleteFile(outFile).catch(() => {})
    }
    busy.value = false
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

.desc b {
  color: #334155;
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

.drop-zone.is-processing {
  cursor: default;
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

.file-content {
  cursor: default;
}

.file-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px;
  word-break: break-all;
}

.controls {
  margin-top: 16px;
  text-align: left;
}

.preset-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}

.preset-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  color: #0f172a;
}

.progress-wrap {
  margin-top: 14px;
  background: #eef2ff;
  border-radius: 8px;
  overflow: hidden;
  height: 10px;
}

.progress-bar {
  height: 100%;
  background: #2563eb;
  transition: width 0.2s;
}

.status-text {
  margin-top: 12px;
  font-size: 13px;
  color: #475569;
  min-height: 18px;
}

.status-text.is-error {
  color: #dc2626;
}

.action-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.btn-clean {
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 11px 26px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-clean:hover { background: #1d4ed8; }
.btn-clean:disabled { opacity: 0.45; cursor: default; }

.btn-download {
  display: inline-block;
  background: #059669;
  color: #fff;
  border-radius: 8px;
  padding: 11px 22px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}
.btn-download:hover { background: #047857; }

.btn-again {
  padding: 11px 18px;
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.btn-again:hover { background: #1e293b; }

.trust-line {
  font-size: 12px;
  color: #94a3b8;
  margin: 12px 0 0;
}
</style>
