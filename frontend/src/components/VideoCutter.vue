<template>
  <div class="cutter-card">
    <div class="cutter-header">
      <div class="title-wrap">
        <span class="badge-tag">纯前端 · 零上传 · 无损流拷贝</span>
        <h3>✂️ 视频截取（多段拼成一个）</h3>
      </div>
      <p class="desc">
        先在下载页把整条视频下载下来，再拿到这里截取：在时间轴上拖出要保留的段，
        点“+ 添加一段”可以多选几段，导出时自动拼成一个视频。
        <b>流拷贝、不重编、画质零损失</b>，文件不会离开你的设备。
        无损切只能落在关键帧上，切点误差约 ±1–3 秒。
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
        accept="video/*,.mp4,.mov,.webm,.mkv,.avi"
        class="hidden-input"
        @change="handleFileSelect"
      />
      <div v-if="!selectedFile" class="drop-content">
        <span class="upload-icon">📂</span>
        <p class="drop-title">点击选择视频，或将视频文件拖拽到此处</p>
        <p class="drop-hint">支持 MP4 / MOV / WebM 等常见视频，最大 500 MB · 首次使用需加载约 30MB 视频引擎（仅一次）</p>
      </div>
      <div v-else class="file-content" @click.stop>
        <span class="upload-icon">🎬</span>
        <p class="file-name">{{ selectedFile.name }}</p>
        <p class="drop-hint">{{ fmtSize(selectedFile.size) }} · 点击上方区域可重新选择</p>
      </div>
    </div>

    <!-- 预览 + 时间轴 -->
    <div v-if="selectedFile" class="cut-area" @click.stop>
      <video
        ref="previewRef"
        class="preview"
        controls
        playsinline
        :src="previewUrl"
        @loadedmetadata="onLoadedMetadata"
        @timeupdate="onTimeUpdate"
      />
      <p v-if="duration > 0" class="dur-line">视频时长 {{ duration.toFixed(1) }} 秒 · 在时间轴上拖动选段，点一段可只播那一段</p>

      <div
        v-if="duration > 0"
        ref="timelineRef"
        class="timeline"
        @pointerdown="onTimelineDown"
        @pointermove="onTimelineMove"
        @pointerup="onTimelineUp"
        @pointercancel="onTimelineUp"
      >
        <div class="playhead" :style="{ left: playheadPct + '%' }" />
        <div
          v-for="s in sortedSegs"
          :key="s.id"
          class="seg"
          :class="{ sel: s.id === selectedId }"
          :data-id="s.id"
          :style="{ left: (s.start / duration * 100) + '%', width: Math.max(0.4, (s.end - s.start) / duration * 100) + '%', background: SEG_COLORS[s.ci % SEG_COLORS.length] }"
        >
          <div class="hb l" />
          <div class="hb r" />
          <div class="lb">{{ fmtT(s.start) }} – {{ fmtT(s.end) }}</div>
        </div>
      </div>

      <div v-if="duration > 0" class="segbar">
        <button type="button" class="btn-secondary" :disabled="busy" @click="addSegment">+ 添加一段</button>
        <button type="button" class="btn-secondary" :disabled="busy || !selectedSeg" @click="deleteSegment">删除选中段</button>
        <span class="seg-hint">拖边缘改长短 · 拖整块移动 · 点一下只播那段</span>
        <span class="seg-total">{{ totalText }}</span>
      </div>

      <div v-if="duration > 0 && selectedSeg" class="tuner">
        <label>开始 <input v-model="tunerStart" type="number" step="0.1" min="0" :disabled="busy" @change="tunerChanged" /> 秒</label>
        <label>结束 <input v-model="tunerEnd" type="number" step="0.1" min="0" :disabled="busy" @change="tunerChanged" /> 秒</label>
      </div>
    </div>

    <!-- 操作区 -->
    <div v-if="selectedFile" class="controls" @click.stop>
      <div v-if="busy" class="progress-wrap">
        <div class="progress-bar" :style="{ width: progressPct + '%' }" />
      </div>
      <p v-if="statusText" class="status-text" :class="{ 'is-error': isError }">{{ statusText }}</p>
      <div class="action-row">
        <button v-if="!downloadUrl" class="btn-cut" :disabled="busy || !segments.length" @click="runCut">
          {{ busy ? '截取中…' : '开始截取并拼接' }}
        </button>
        <a
          v-if="downloadUrl"
          class="btn-download"
          :href="downloadUrl"
          :download="downloadName"
        >⬇ 下载截取文件（{{ fmtSize(resultSize) }}）</a>
        <button v-if="downloadUrl || isError" class="btn-again" @click="resetCutter">继续截取下一个</button>
      </div>
      <p class="trust-line">处理全程在本机浏览器内存中完成，文件不会离开你的设备；流拷贝不重编，通常数秒完成。超过 200MB 的片子在手机上可能较慢。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MAX_FILE, WARN_FILE, cutVideoFile } from '../utils/cutVideo.js'

const SEG_COLORS = ['#1a73e8', '#16a34a', '#f59e0b', '#8b5cf6', '#ec4899', '#0891b2']
const MINLEN = 0.5
const MAXSEGS = 20

const fileInput = ref(null)
const previewRef = ref(null)
const timelineRef = ref(null)
const isDragging = ref(false)
const selectedFile = ref(null)
const duration = ref(0)
const previewUrl = ref('')
const segments = ref([])
const selectedId = ref(null)
const segSeq = ref(0)
const previewSegId = ref(null)
const playheadPct = ref(0)
const tunerStart = ref('0.0')
const tunerEnd = ref('0.0')
const busy = ref(false)
const statusText = ref('')
const isError = ref(false)
const progressPct = ref(0)
const downloadUrl = ref('')
const downloadName = ref('')
const resultSize = ref(0)

const sortedSegs = computed(() => segments.value.slice().sort((a, b) => a.start - b.start))
const selectedSeg = computed(() => segments.value.find((s) => s.id === selectedId.value) || null)
const totalText = computed(() => {
  if (!segments.value.length) return ''
  const t = segments.value.reduce((acc, s) => acc + Math.max(0, s.end - s.start), 0)
  return `共保留 ${fmtT(t)}`
})

function r1(v) { return Math.round(v * 10) / 10 }
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)) }
function fmtT(s) {
  s = Math.max(0, s || 0)
  const m = Math.floor(s / 60)
  const r = s - m * 60
  return m + ':' + (r < 10 ? '0' : '') + r.toFixed(1)
}
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
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  selectedFile.value = f
  duration.value = 0
  segments.value = []
  selectedId.value = null
  previewSegId.value = null
  playheadPct.value = 0
  previewUrl.value = URL.createObjectURL(f)
  setStatus(
    '正在读取时长…' +
    (f.size > WARN_FILE ? '（大文件：手机内存有限时可能较慢，请耐心等待。）' : '')
  )
}

function onLoadedMetadata() {
  const v = previewRef.value
  if (!v) return
  duration.value = v.duration || 0
  if (duration.value > 0) {
    segments.value = [{ id: ++segSeq.value, start: 0, end: r1(duration.value), ci: 0 }]
    selectedId.value = segments.value[0].id
    syncTuner()
    setStatus(`就绪：${selectedFile.value.name}（${fmtSize(selectedFile.value.size)}），拖时间轴选段后点截取。`)
  } else {
    setStatus('读不到视频时长，时间轴不可用。', true)
  }
}

function onTimeUpdate() {
  const v = previewRef.value
  if (!v || duration.value <= 0) return
  playheadPct.value = clamp((v.currentTime / duration.value) * 100, 0, 100)
  if (previewSegId.value !== null) {
    const s = segments.value.find((x) => x.id === previewSegId.value)
    if (s && v.currentTime >= s.end - 0.03) {
      v.pause()
      previewSegId.value = null
    }
  }
}

function neighbors(s) {
  const o = sortedSegs.value
  const i = o.indexOf(s)
  return { prev: o[i - 1] || null, next: o[i + 1] || null }
}
function syncTuner() {
  const s = selectedSeg.value
  if (s) {
    tunerStart.value = s.start.toFixed(1)
    tunerEnd.value = s.end.toFixed(1)
  }
}

// ---- 时间轴拖拽（移植自 dearhua video-cutter）----
let drag = null
function onTimelineDown(e) {
  if (duration.value <= 0) return
  const el = e.target && e.target.closest ? e.target.closest('.seg') : null
  if (!el) {
    // 点空白处：直接seek
    const r = timelineRef.value.getBoundingClientRect()
    const t = clamp(((e.clientX - r.left) / r.width) * duration.value, 0, duration.value)
    previewSegId.value = null
    if (previewRef.value) previewRef.value.currentTime = t
    return
  }
  const s = segments.value.find((x) => x.id === +el.getAttribute('data-id'))
  if (!s) return
  selectedId.value = s.id
  let mode = 'move'
  if (e.target.classList && e.target.classList.contains('hb')) {
    mode = e.target.classList.contains('l') ? 'l' : 'r'
  }
  drag = { id: s.id, mode, x0: e.clientX, s0: s.start, e0: s.end, moved: false }
  try { timelineRef.value.setPointerCapture(e.pointerId) } catch (_) {}
  syncTuner()
  e.preventDefault()
}
function onTimelineMove(e) {
  if (!drag) return
  const s = segments.value.find((x) => x.id === drag.id)
  if (!s || duration.value <= 0) return
  const r = timelineRef.value.getBoundingClientRect()
  const dt = ((e.clientX - drag.x0) / r.width) * duration.value
  if (Math.abs(e.clientX - drag.x0) > 4) drag.moved = true
  const nb = neighbors(s)
  const lo = nb.prev ? nb.prev.end : 0
  const hi = nb.next ? nb.next.start : duration.value
  let ns = drag.s0
  let ne = drag.e0
  if (drag.mode === 'l') ns = clamp(drag.s0 + dt, lo, drag.e0 - MINLEN)
  else if (drag.mode === 'r') ne = clamp(drag.e0 + dt, drag.s0 + MINLEN, hi)
  else {
    const len = drag.e0 - drag.s0
    ns = clamp(drag.s0 + dt, lo, hi - len)
    ne = ns + len
  }
  s.start = r1(ns)
  s.end = r1(ne)
  syncTuner()
}
function onTimelineUp() {
  if (drag && !drag.moved) {
    const s = segments.value.find((x) => x.id === drag.id)
    if (s && duration.value > 0 && previewRef.value) {
      previewSegId.value = s.id
      previewRef.value.currentTime = Math.min(s.start, Math.max(0, duration.value - 0.1))
      const pr = previewRef.value.play()
      if (pr && pr.catch) pr.catch(() => {})
    }
  }
  drag = null
}

function addSegment() {
  if (duration.value <= 0) return
  if (segments.value.length >= MAXSEGS) {
    setStatus('放不下新段了（最多 20 段）。', true)
    return
  }
  const o = sortedSegs.value
  const gaps = []
  let prevE = 0
  o.forEach((s) => { gaps.push([prevE, s.start]); prevE = s.end })
  gaps.push([prevE, duration.value])
  let best = null
  gaps.forEach((g) => {
    if (g[1] - g[0] >= 1 && (!best || g[1] - g[0] > best[1] - best[0])) best = g
  })
  if (!best) {
    setStatus('放不下新段了（没有空余位置）。', true)
    return
  }
  const len = Math.min(10, (best[1] - best[0]) / 2)
  const ns = best[0] + (best[1] - best[0] - len) / 2
  const s = { id: ++segSeq.value, start: r1(ns), end: r1(ns + len), ci: segSeq.value % SEG_COLORS.length }
  segments.value.push(s)
  selectedId.value = s.id
  syncTuner()
  previewSegId.value = s.id
  if (previewRef.value) previewRef.value.currentTime = s.start
}
function deleteSegment() {
  segments.value = segments.value.filter((s) => s.id !== selectedId.value)
  if (previewSegId.value === selectedId.value) previewSegId.value = null
  selectedId.value = null
  syncTuner()
}
function tunerChanged() {
  const s = selectedSeg.value
  if (!s || duration.value <= 0) return
  const ns = parseFloat(tunerStart.value)
  const ne = parseFloat(tunerEnd.value)
  if (Number.isNaN(ns) || Number.isNaN(ne)) return
  const nb = neighbors(s)
  const lo = nb.prev ? nb.prev.end : 0
  const hi = nb.next ? nb.next.start : duration.value
  s.start = r1(clamp(ns, lo, hi - MINLEN))
  s.end = r1(clamp(ne, s.start + MINLEN, hi))
  syncTuner()
}

function clearResult() {
  if (downloadUrl.value) URL.revokeObjectURL(downloadUrl.value)
  downloadUrl.value = ''
  downloadName.value = ''
  resultSize.value = 0
  progressPct.value = 0
}
function resetCutter() {
  selectedFile.value = null
  duration.value = 0
  segments.value = []
  selectedId.value = null
  previewSegId.value = null
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  clearResult()
  setStatus('')
  if (fileInput.value) fileInput.value.value = ''
}

async function runCut() {
  const file = selectedFile.value
  if (!file || busy.value) return
  if (!segments.value.length) {
    setStatus('请先在时间轴上选至少一段。', true)
    return
  }
  busy.value = true
  clearResult()
  try {
    const res = await cutVideoFile({
      file,
      segments: sortedSegs.value,
      onStatus: (t) => setStatus(t),
      onProgress: (p) => { progressPct.value = p },
    })
    downloadUrl.value = URL.createObjectURL(res.blob)
    downloadName.value = res.filename
    resultSize.value = res.size
    setStatus(`✅ 截取完成！共保留 ${fmtT(res.totalKept)}，已拼成一个视频，无损、画质零损失。`)
  } catch (err) {
    console.error(err)
    setStatus('截取出错：' + (err?.message || err), true)
  } finally {
    busy.value = false
  }
}

// 供下载页“取片去截取”直接把文件递进来（不用重新选文件）
function openWithFile(file) {
  if (!file) return
  pick(file)
}
defineExpose({ openWithFile })
</script>

<style scoped>
.cutter-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}
.cutter-header { margin-bottom: 16px; }
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
h3 { margin: 0; font-size: 15px; font-weight: 700; color: #0f172a; }
.desc { font-size: 13px; color: #64748b; line-height: 1.5; margin: 0; }
.desc b { color: #334155; }

.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  padding: 32px 20px;
  text-align: center;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s ease;
}
.drop-zone:hover, .drop-zone.is-dragging { border-color: #2563eb; background: #eff6ff; }
.drop-zone.is-processing { cursor: default; }
.hidden-input { display: none; }
.upload-icon { font-size: 32px; display: block; margin-bottom: 8px; }
.drop-title { font-size: 14px; font-weight: 600; color: #1e293b; margin: 0 0 4px; }
.drop-hint { font-size: 12px; color: #94a3b8; margin: 0; }
.file-content { cursor: default; }
.file-name { font-size: 14px; font-weight: 600; color: #1e293b; margin: 0 0 4px; word-break: break-all; }

.cut-area { margin-top: 16px; display: flex; flex-direction: column; gap: 10px; }
.preview { width: 100%; max-height: 320px; background: #000; border-radius: 8px; }
.dur-line { font-size: 12px; color: #64748b; margin: 0; }

.timeline {
  position: relative;
  height: 56px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  touch-action: none;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
}
.playhead {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #dc2626;
  z-index: 3;
  pointer-events: none;
}
.seg {
  position: absolute;
  top: 8px;
  bottom: 8px;
  border-radius: 6px;
  opacity: 0.9;
  cursor: grab;
  z-index: 1;
}
.seg.sel { outline: 2px solid #0f172a; outline-offset: 1px; z-index: 2; }
.seg .hb {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 12px;
  cursor: ew-resize;
}
.seg .hb.l { left: 0; }
.seg .hb.r { right: 0; }
.seg .lb {
  position: absolute;
  left: 14px;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  pointer-events: none;
}

.segbar { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.seg-hint { font-size: 12px; color: #94a3b8; }
.seg-total { font-size: 12px; font-weight: 700; color: #334155; margin-left: auto; }

.tuner { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; font-size: 13px; color: #334155; }
.tuner input {
  width: 90px;
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.controls { margin-top: 16px; text-align: left; }
.progress-wrap { background: #eef2ff; border-radius: 8px; overflow: hidden; height: 10px; }
.progress-bar { height: 100%; background: #2563eb; transition: width 0.2s; }
.status-text { margin-top: 12px; font-size: 13px; color: #475569; min-height: 18px; }
.status-text.is-error { color: #dc2626; }
.action-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
.btn-cut {
  background: #2563eb; color: #fff; border: none; border-radius: 8px;
  padding: 11px 26px; font-size: 14px; font-weight: 600; cursor: pointer;
}
.btn-cut:hover { background: #1d4ed8; }
.btn-cut:disabled { opacity: 0.45; cursor: default; }
.btn-download {
  display: inline-block; background: #059669; color: #fff; border-radius: 8px;
  padding: 11px 22px; font-size: 14px; font-weight: 600; text-decoration: none;
}
.btn-download:hover { background: #047857; }
.btn-again {
  padding: 11px 18px; background: #0f172a; color: #ffffff; border: none;
  border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-again:hover { background: #1e293b; }
.btn-secondary {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 500;
  color: #475569; background: #f1f5f9; border: 1px solid #e2e8f0; cursor: pointer;
}
.btn-secondary:hover:not(:disabled) { background: #e2e8f0; color: #0f172a; }
.btn-secondary:disabled { opacity: 0.45; cursor: default; }
.trust-line { font-size: 12px; color: #94a3b8; margin: 12px 0 0; }
</style>
