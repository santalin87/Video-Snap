<template>
  <div class="video-card">
    <!-- 封面 + 基本信息 -->
    <div class="card-header">
      <div class="thumbnail-wrap">
        <img
          v-if="info.thumbnail"
          :src="info.thumbnail"
          :alt="info.title"
          class="thumbnail"
          @error="thumbError = true"
        />
        <div v-else class="thumbnail-placeholder">
          <span class="platform-icon">{{ platformIcon }}</span>
        </div>
        <span v-if="info.duration" class="duration-badge">
          {{ formatDuration(info.duration) }}
        </span>
      </div>

      <div class="meta">
        <span class="platform-label" :class="`platform-${info.platform}`">
          {{ platformLabel }}
        </span>
        <h2 class="title">{{ info.title }}</h2>
        <p v-if="info.author" class="author">{{ info.author }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  info: {
    type: Object,
    required: true,
  },
})

const thumbError = ref(false)

const platformMap = {
  youtube:  { label: 'YouTube',    icon: '▶' },
  twitter:  { label: 'Twitter / X', icon: '𝕏' },
  douyin:   { label: '抖音',        icon: '🎵' },
  tiktok:   { label: 'TikTok',     icon: '♪' },
}

const platformLabel = computed(() => platformMap[props.info.platform]?.label ?? props.info.platform)
const platformIcon  = computed(() => platformMap[props.info.platform]?.icon ?? '🎬')

function formatDuration(sec) {
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}
</script>

<style scoped>
.video-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  gap: 16px;
  padding: 20px;
}

.thumbnail-wrap {
  position: relative;
  flex-shrink: 0;
  width: 180px;
  height: 101px;
  border-radius: 8px;
  overflow: hidden;
  background: #f3f4f6;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
}

.duration-badge {
  position: absolute;
  bottom: 6px;
  right: 6px;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.platform-label {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 8px;
  border-radius: 4px;
  align-self: flex-start;
}

.platform-youtube  { background: #fee2e2; color: #dc2626; }
.platform-twitter  { background: #dbeafe; color: #1d4ed8; }
.platform-douyin   { background: #fce7f3; color: #db2777; }
.platform-tiktok   { background: #f3e8ff; color: #7e22ce; }

.title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

.author {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 480px) {
  .thumbnail-wrap {
    width: 120px;
    height: 68px;
  }
}
</style>
