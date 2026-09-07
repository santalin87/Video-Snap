<template>
  <div class="format-list">

    <!-- 视频格式 -->
    <section v-if="formats.video?.length" class="section">
      <h3 class="section-title">🎬 视频（含音频）</h3>
      <div class="items">
        <a
          v-for="f in formats.video"
          :key="f.url"
          :href="f.url"
          :download="suggestFilename(f, 'video')"
          class="format-item"
          target="_blank"
          rel="noopener noreferrer"
          @click="onDownload(f, 'video')"
        >
          <div class="item-left">
            <span class="quality-badge quality-video">{{ f.quality }}</span>
            <span class="ext-tag">{{ f.ext.toUpperCase() }}</span>
            <span v-if="f.note" class="note-tag">{{ f.note }}</span>
          </div>
          <div class="item-right">
            <span v-if="f.size_mb" class="size-label">{{ f.size_mb }} MB</span>
            <span class="download-icon">⬇</span>
          </div>
        </a>
      </div>
    </section>

    <!-- 音频格式 -->
    <section v-if="formats.audio?.length" class="section">
      <h3 class="section-title">🎵 纯音频</h3>
      <div class="items">
        <a
          v-for="f in formats.audio"
          :key="f.url"
          :href="f.url"
          :download="suggestFilename(f, 'audio')"
          class="format-item"
          target="_blank"
          rel="noopener noreferrer"
          @click="onDownload(f, 'audio')"
        >
          <div class="item-left">
            <span class="quality-badge quality-audio">{{ f.quality }}</span>
            <span class="ext-tag">{{ f.ext.toUpperCase() }}</span>
            <span v-if="f.abr" class="abr-label">{{ f.abr }}kbps</span>
          </div>
          <div class="item-right">
            <span class="download-icon">⬇</span>
          </div>
        </a>
      </div>
    </section>

    <!-- 字幕 -->
    <section v-if="formats.subtitles?.length" class="section">
      <h3 class="section-title">📄 字幕</h3>
      <div class="items subtitle-items">
        <a
          v-for="s in formats.subtitles"
          :key="s.url"
          :href="s.url"
          :download="`subtitle_${s.lang}.${s.ext}`"
          class="format-item"
          target="_blank"
          rel="noopener noreferrer"
        >
          <div class="item-left">
            <span class="quality-badge quality-sub">{{ s.label }}</span>
            <span class="ext-tag">{{ s.ext.toUpperCase() }}</span>
          </div>
          <div class="item-right">
            <span class="download-icon">⬇</span>
          </div>
        </a>
      </div>
    </section>

    <!-- 有效期提示 -->
    <p class="expiry-notice">
      ⚠️ 直链有时效性（通常 6 小时内有效），请尽快下载
    </p>
  </div>
</template>

<script setup>
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

function sanitize(str) {
  return (str || 'video').replace(/[\\/:*?"<>|]/g, '_').slice(0, 60)
}

function suggestFilename(f, type) {
  const base = sanitize(props.title)
  if (type === 'audio') return `${base}_audio.${f.ext}`
  return `${base}_${f.quality}.${f.ext}`
}

function onDownload(f, type) {
  // 可在此埋点统计（可选）
  console.log(`[downX] 下载 ${type} ${f.quality} ${f.ext}`)
}
</script>

<style scoped>
.format-list {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.section {
  border-top: 1px solid #f3f4f6;
  padding: 16px 20px;
}

.section:first-child {
  border-top: none;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 12px;
}

.items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subtitle-items {
  flex-direction: row;
  flex-wrap: wrap;
}

.format-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1.5px solid #e5e7eb;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.15s;
}

.format-item:hover {
  border-color: #6366f1;
  background: #f5f3ff;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quality-badge {
  font-size: 13px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.quality-video { background: #dbeafe; color: #1d4ed8; }
.quality-audio { background: #d1fae5; color: #065f46; }
.quality-sub   { background: #fef3c7; color: #92400e; }

.ext-tag {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 600;
}

.note-tag {
  font-size: 11px;
  color: #059669;
  background: #d1fae5;
  padding: 1px 6px;
  border-radius: 4px;
}

.abr-label {
  font-size: 12px;
  color: #6b7280;
}

.size-label {
  font-size: 12px;
  color: #9ca3af;
}

.download-icon {
  font-size: 16px;
  color: #6366f1;
}

.expiry-notice {
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
  padding: 12px 20px 16px;
  margin: 0;
  border-top: 1px solid #f3f4f6;
}
</style>
