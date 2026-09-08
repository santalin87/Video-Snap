<template>
  <div class="download-panel">
    <!-- 视频下载卡片 -->
    <div v-if="formats.video?.length" class="download-row">
      <div class="row-header">
        <div class="badge badge-video">
          <span class="icon">🎬</span>
          <span class="title">视频下载</span>
        </div>
        <span class="hint-tag">⚡ 直连官方 CDN · 0 服务器流量</span>
      </div>

      <div class="row-controls">
        <div class="select-wrap">
          <select v-model="selectedVideoUrl" class="custom-select">
            <option
              v-for="f in formats.video"
              :key="f.url"
              :value="f.url"
            >
              {{ f.quality }} · {{ f.ext.toUpperCase() }}
              {{ f.note ? ` (${f.note})` : '' }}
              {{ f.size_mb ? ` · ${f.size_mb} MB` : '' }}
            </option>
          </select>
        </div>

        <div class="actions">
          <!-- 核心推荐：直连 CDN 下载，零耗费 VPS 流量 -->
          <a
            :href="selectedVideoUrl"
            :download="suggestFilename(currentVideo, 'video')"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-blue"
            title="直连官方 CDN 下载，完全不消耗你的 VPS 流量"
          >
            <span class="arrow">↓</span> 直链下载
          </a>

          <!-- 复制链接按钮，极度方便放进下载工具或浏览器直接下 -->
          <button
            type="button"
            class="btn-secondary"
            @click="copyUrl(selectedVideoUrl, 'video')"
          >
            {{ copiedType === 'video' ? '✓ 已复制' : '复制直链' }}
          </button>
        </div>
      </div>

      <div class="tip-bar">
        💡 <b>0 流量下载技巧</b>：右键「直链下载」选择 <b>“链接另存为...”</b> 即可直接保存；若在新标签播放，点击播放器右下角 <b>⋮ ➔「下载」</b>。
      </div>
    </div>

    <!-- 音频下载卡片 -->
    <div v-if="formats.audio?.length" class="download-row">
      <div class="row-header">
        <div class="badge badge-audio">
          <span class="icon">🎵</span>
          <span class="title">音频提取</span>
        </div>
        <span class="hint-tag">⚡ 直连官方 CDN · 0 服务器流量</span>
      </div>

      <div class="row-controls">
        <div class="select-wrap">
          <select v-model="selectedAudioUrl" class="custom-select">
            <option
              v-for="a in formats.audio"
              :key="a.url"
              :value="a.url"
            >
              {{ a.quality }} · {{ a.ext.toUpperCase() }}
              {{ a.abr ? ` · ${a.abr}kbps` : '' }}
            </option>
          </select>
        </div>

        <div class="actions">
          <a
            :href="selectedAudioUrl"
            :download="suggestFilename(currentAudio, 'audio')"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-green"
            title="直连官方 CDN 下载，完全不消耗你的 VPS 流量"
          >
            <span class="arrow">↓</span> 直链下载
          </a>

          <button
            type="button"
            class="btn-secondary"
            @click="copyUrl(selectedAudioUrl, 'audio')"
          >
            {{ copiedType === 'audio' ? '✓ 已复制' : '复制直链' }}
          </button>
        </div>
      </div>

      <div class="tip-bar">
        💡 <b>0 流量下载技巧</b>：右键「直链下载」选择 <b>“链接另存为...”</b> 保存为纯音频文件。
      </div>
    </div>

    <!-- 字幕下载卡片 -->
    <div v-if="formats.subtitles?.length" class="download-row">
      <div class="row-header">
        <div class="badge badge-sub">
          <span class="icon">📄</span>
          <span class="title">字幕文件</span>
        </div>
        <span class="hint-tag">共 {{ formats.subtitles.length }} 种语言可用</span>
      </div>

      <div class="row-controls">
        <div class="select-wrap">
          <select v-model="selectedSubUrl" class="custom-select">
            <option
              v-for="s in formats.subtitles"
              :key="s.url"
              :value="s.url"
            >
              {{ s.label }} ({{ s.lang }}) · {{ s.ext.toUpperCase() }}
            </option>
          </select>
        </div>

        <div class="actions">
          <a
            :href="selectedSubUrl"
            :download="currentSubFilename"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-dark"
          >
            <span class="arrow">↓</span> 下载字幕
          </a>

          <button
            type="button"
            class="btn-secondary"
            @click="copyUrl(selectedSubUrl, 'sub')"
          >
            {{ copiedType === 'sub' ? '✓ 已复制' : '复制链接' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 底部保障说明 -->
    <div class="footer-note">
      <span class="dot" />
      <b>NewPipe 原生直链架构</b>：视频和音频直接从官方 CDN 传到你的浏览器，不经过 VPS 中转，<b>完全不消耗你的 VPS 免费流量额度</b>。
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  formats: {
    type: Object,
    required: true,
  },
  title: {
    type: String,
    default: 'video',
  },
})

// 默认选中项
const selectedVideoUrl = ref('')
const selectedAudioUrl = ref('')
const selectedSubUrl   = ref('')
const copiedType       = ref('')

watch(
  () => props.formats,
  (newVal) => {
    if (newVal.video?.length)     selectedVideoUrl.value = newVal.video[0].url
    if (newVal.audio?.length)     selectedAudioUrl.value = newVal.audio[0].url
    if (newVal.subtitles?.length) selectedSubUrl.value   = newVal.subtitles[0].url
  },
  { immediate: true }
)

const currentVideo = computed(() =>
  props.formats.video?.find((f) => f.url === selectedVideoUrl.value) || props.formats.video?.[0]
)

const currentAudio = computed(() =>
  props.formats.audio?.find((a) => a.url === selectedAudioUrl.value) || props.formats.audio?.[0]
)

const currentSub = computed(() =>
  props.formats.subtitles?.find((s) => s.url === selectedSubUrl.value) || props.formats.subtitles?.[0]
)

function sanitize(str) {
  return (str || 'video').replace(/[\\/:*?"<>|]/g, '_').slice(0, 60)
}

function suggestFilename(item, type) {
  if (!item) return 'download'
  const base = sanitize(props.title)
  if (type === 'audio') return `${base}_audio.${item.ext}`
  return `${base}_${item.quality}.${item.ext}`
}

const currentSubFilename = computed(() => {
  const s = currentSub.value
  if (!s) return 'subtitle.srt'
  const base = sanitize(props.title)
  return `${base}_${s.lang}.${s.ext}`
})

function copyUrl(url, type) {
  if (!url) return
  navigator.clipboard.writeText(url).then(() => {
    copiedType.value = type
    setTimeout(() => {
      copiedType.value = ''
    }, 2000)
  })
}
</script>

<style scoped>
.download-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.download-row {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
  transition: border-color 0.15s ease;
}

.download-row:hover {
  border-color: #cbd5e1;
}

.row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 6px;
}

.badge-video {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #dbeafe;
}

.badge-audio {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.badge-sub {
  background: #f8fafc;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.hint-tag {
  font-size: 11px;
  font-weight: 600;
  color: #059669;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  padding: 2px 8px;
  border-radius: 999px;
}

.row-controls {
  display: flex;
  gap: 10px;
}

@media (max-width: 600px) {
  .row-controls {
    flex-direction: column;
  }
}

.select-wrap {
  flex: 1;
  position: relative;
}

.custom-select {
  width: 100%;
  appearance: none;
  background-color: #f8fafc;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  background-size: 16px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 10px 40px 10px 14px;
  font-size: 14px;
  font-weight: 500;
  color: #0f172a;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease;
}

.custom-select:focus {
  background-color: #ffffff;
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.12);
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.arrow {
  font-size: 15px;
  font-weight: bold;
}

/* 纯蓝按钮 */
.btn-blue {
  background: #2563eb;
  color: #ffffff;
  border: 1px solid #1d4ed8;
}
.btn-blue:hover {
  background: #1d4ed8;
}

/* 纯绿按钮 */
.btn-green {
  background: #059669;
  color: #ffffff;
  border: 1px solid #047857;
}
.btn-green:hover {
  background: #047857;
}

/* 深灰/黑底按钮 */
.btn-dark {
  background: #1e293b;
  color: #ffffff;
  border: 1px solid #0f172a;
}
.btn-dark:hover {
  background: #0f172a;
}

.tip-bar {
  margin-top: 10px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #f1f5f9;
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}

.tip-bar b {
  color: #334155;
}

.footer-note {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #047857;
  background: #ecfdf5;
  border: 1px solid #d1fae5;
  padding: 10px 16px;
  border-radius: 8px;
  line-height: 1.5;
}

.footer-note b {
  font-weight: 700;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #059669;
  display: inline-block;
  flex-shrink: 0;
}
</style>
