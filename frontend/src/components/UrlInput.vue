<template>
  <div class="url-input-wrapper">
    <div class="input-group" :class="{ 'has-error': error }">
      <button
        type="button"
        class="paste-btn"
        :disabled="loading"
        title="清空输入框并粘贴剪贴板里的链接"
        @click="handlePasteClick"
      >
        📋 粘贴
      </button>
      <input
        ref="urlField"
        v-model="inputUrl"
        type="url"
        class="url-field"
        placeholder="粘贴视频链接 — 微博 / B站 / YouTube / X / 抖音 / TikTok 等均可"
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
        <span v-else>解析链接</span>
      </button>
    </div>

    <p v-if="error" class="error-msg">{{ error }}</p>
    <p v-if="pasteHint" class="paste-hint">{{ pasteHint }}</p>

    <!-- 平台标签 -->
    <div class="platform-hints">
      <span v-for="p in platforms" :key="p.name" class="platform-tag">
        <span class="platform-icon">{{ p.icon }}</span> {{ p.name }}
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
const urlField = ref(null)
const pasteHint = ref('')

const platforms = [
  { icon: '▶', name: 'YouTube' },
  { icon: '𝕏', name: 'Twitter / X' },
  { icon: '🎵', name: '抖音 (无水印)' },
  { icon: '♪', name: 'TikTok' },
  { icon: '🎬', name: '微博' },
  { icon: '📺', name: 'B站' },
  { icon: '＋', name: 'yt-dlp 支持的更多平台' },
]

function handleSubmit() {
  const url = inputUrl.value.trim()
  if (url) emit('submit', url)
}

function handlePaste() {
  setTimeout(() => {
    const url = inputUrl.value.trim()
    if (url) emit('submit', url)
  }, 100)
}

// 一键粘贴：先读剪贴板，读到了才清空旧链接并填入（读不到时保留旧链接，
// 只提示手动粘贴，避免点一下把原来的链接弄丢）；填入后与手动粘贴一致，自动开始解析。
async function handlePasteClick() {
  pasteHint.value = ''
  try {
    if (!navigator.clipboard?.readText) throw new Error('clipboard unsupported')
    const text = (await navigator.clipboard.readText()).trim()
    if (!text) {
      pasteHint.value = '剪贴板是空的，没有可粘贴的链接'
      return
    }
    inputUrl.value = text
    setTimeout(() => {
      const url = inputUrl.value.trim()
      if (url) emit('submit', url)
    }, 100)
  } catch {
    pasteHint.value = '浏览器不允许直接读取剪贴板，请长按输入框手动粘贴'
    urlField.value?.focus()
  }
}

defineExpose({ clear: () => { inputUrl.value = '' } })
</script>

<style scoped>
.url-input-wrapper {
  width: 100%;
}

.input-group {
  display: flex;
  background: #ffffff;
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid #cbd5e1;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.input-group:focus-within {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.input-group.has-error {
  border-color: #dc2626;
}

.url-field {
  flex: 1;
  padding: 13px 16px;
  font-size: 14px;
  border: none;
  outline: none;
  background: transparent;
  color: #0f172a;
  min-width: 0;
}

.url-field::placeholder {
  color: #94a3b8;
}

.url-field:disabled {
  background: #f8fafc;
  cursor: not-allowed;
}

.paste-btn {
  padding: 0 12px;
  background: #f1f5f9;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-right: 1px solid #e2e8f0;
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}

.paste-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.paste-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.paste-hint {
  margin: 8px 0 0 4px;
  color: #b45309;
  font-size: 12px;
}

.parse-btn {
  padding: 0 24px;
  background: #2563eb;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.15s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.parse-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.parse-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  margin: 8px 0 0 4px;
  color: #dc2626;
  font-size: 13px;
  font-weight: 500;
}

.platform-hints {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.platform-tag {
  font-size: 12px;
  font-weight: 500;
  color: #475569;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 3px 10px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.platform-icon {
  font-size: 12px;
  color: #64748b;
}
</style>
