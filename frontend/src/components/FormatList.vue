<template>
  <div class="download-panel">
    <!-- 视频下载卡片 -->
    <div v-if="formats.video?.length" class="download-row">
      <div class="row-header">
        <div class="badge badge-video">
          <span class="icon">🎬</span>
          <span class="title">视频下载</span>
        </div>
        <span class="hint">直链高速下载</span>
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

        <a
          :href="selectedVideoUrl"
          :download="suggestFilename(currentVideo, 'video')"
          class="btn btn-blue"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span class="arrow">↓</span> 下载视频
        </a>
      </div>
    </div>

    <!-- 音频下载卡片 -->
    <div v-if="formats.audio?.length" class="download-row">
      <div class="row-header">
        <div class="badge badge-audio">
          <span class="icon">🎵</span>
          <span class="title">音频提取</span>
        </div>
        <span class="hint">纯音频格式 (无画面)</span>
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

        <a
          :href="selectedAudioUrl"
          :download="suggestFilename(currentAudio, 'audio')"
          class="btn btn-green"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span class="arrow">↓</span> 下载音频
        </a>
      </div>
    </div>

    <!-- 字幕下载卡片 -->
    <div v-if="formats.subtitles?.length" class="download-row">
      <div class="row-header">
        <div class="badge badge-sub">
          <span class="icon">📄</span>
          <span class="title">字幕文件</span>
        </div>
        <span class="hint">共 {{ formats.subtitles.length }} 种语言可用</span>
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

        <a
          :href="selectedSubUrl"
          :download="currentSubFilename"
          class="btn btn-dark"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span class="arrow">↓</span> 下载字幕
        </a>
      </div>
    </div>

    <!-- 底部提示说明 -->
    <div class="footer-note">
      <span class="dot" />
      直链由平台官方 CDN 直接返回，具有时效性，请在解析后尽快点击下载。
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

.hint {
  font-size: 12px;
  color: #94a3b8;
}

.row-controls {
  display: flex;
  gap: 12px;
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

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
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

.footer-note {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
  padding: 8px 4px 0;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #059669;
  display: inline-block;
}
</style>
