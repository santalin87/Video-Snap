<template>
  <div class="video-card">
    <div class="card-body">
      <div class="thumbnail-wrap">
        <img
          v-if="info.thumbnail && !thumbError"
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
        <div class="tag-row">
          <span class="platform-badge" :class="`badge-${info.platform}`">
            {{ platformLabel }}
          </span>
          <span v-if="info.author" class="author-tag">
            UP主 / 作者：{{ info.author }}
          </span>
        </div>
        <h2 class="title" :title="info.title">{{ info.title }}</h2>
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
  youtube: { label: 'YouTube', icon: '▶' },
  twitter: { label: 'Twitter / X', icon: '𝕏' },
  douyin:  { label: '抖音', icon: '🎵' },
  tiktok:  { label: 'TikTok', icon: '♪' },
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
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.card-body {
  display: flex;
  gap: 16px;
  padding: 16px;
}

.thumbnail-wrap {
  position: relative;
  flex-shrink: 0;
  width: 170px;
  height: 96px;
  border-radius: 8px;
  overflow: hidden;
  background: #0f172a;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e293b;
  color: #94a3b8;
  font-size: 28px;
}

.duration-badge {
  position: absolute;
  bottom: 6px;
  right: 6px;
  background: rgba(15, 23, 42, 0.85);
  color: #ffffff;
  font-size: 11px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  font-variant-numeric: tabular-nums;
}

.meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.platform-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 2px 7px;
  border-radius: 4px;
}

.badge-youtube { background: #fee2e2; color: #dc2626; }
.badge-twitter { background: #f1f5f9; color: #0f172a; }
.badge-douyin  { background: #fdf2f8; color: #db2777; }
.badge-tiktok  { background: #f1f5f9; color: #0f172a; }

.author-tag {
  font-size: 12px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 520px) {
  .card-body {
    flex-direction: column;
  }
  .thumbnail-wrap {
    width: 100%;
    height: 180px;
  }
}
</style>
