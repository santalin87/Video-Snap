<template>
  <div class="url-input-wrapper">
    <div class="input-group" :class="{ 'has-error': error }">
      <input
        v-model="inputUrl"
        type="url"
        class="url-field"
        placeholder="粘贴视频链接 — YouTube / Twitter·X / 抖音 / TikTok"
        :disabled="loading"
        @keydown.enter="handleSubmit"
        @paste="handlePaste"
      />
      <button
        class="parse-btn"
        :disabled="loading || !inputUrl.trim()"
        @click="handleSubmit"
      >
        <span v-if="loading" class="spinner" />
        <span v-else>解析</span>
      </button>
    </div>

    <p v-if="error" class="error-msg">{{ error }}</p>

    <!-- 平台图标提示 -->
    <div class="platform-hints">
      <span v-for="p in platforms" :key="p.name" class="platform-tag">
        {{ p.icon }} {{ p.name }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: Boolean,
  error: String,
})

const emit = defineEmits(['submit'])

const inputUrl = ref('')

const platforms = [
  { icon: '▶', name: 'YouTube' },
  { icon: '𝕏', name: 'Twitter / X' },
  { icon: '🎵', name: '抖音' },
  { icon: '♪', name: 'TikTok' },
]

function handleSubmit() {
  const url = inputUrl.value.trim()
  if (url) emit('submit', url)
}

function handlePaste(e) {
  // 粘贴后自动触发解析（延迟一帧等 input 更新）
  setTimeout(() => {
    const url = inputUrl.value.trim()
    if (url) emit('submit', url)
  }, 100)
}

defineExpose({ clear: () => { inputUrl.value = '' } })
</script>

<style scoped>
.url-input-wrapper {
  width: 100%;
}

.input-group {
  display: flex;
  gap: 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 2px solid #e5e7eb;
  transition: border-color 0.2s;
}

.input-group:focus-within {
  border-color: #6366f1;
}

.input-group.has-error {
  border-color: #ef4444;
}

.url-field {
  flex: 1;
  padding: 14px 18px;
  font-size: 15px;
  border: none;
  outline: none;
  background: #fff;
  color: #1f2937;
  min-width: 0;
}

.url-field::placeholder {
  color: #9ca3af;
}

.url-field:disabled {
  background: #f9fafb;
  cursor: not-allowed;
}

.parse-btn {
  padding: 14px 28px;
  background: #6366f1;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}

.parse-btn:hover:not(:disabled) {
  background: #4f46e5;
}

.parse-btn:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  margin-top: 8px;
  color: #ef4444;
  font-size: 13px;
  padding-left: 4px;
}

.platform-hints {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.platform-tag {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 3px 10px;
  border-radius: 999px;
}
</style>
