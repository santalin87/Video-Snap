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
        placeholder="粘贴视频链接，带宣传语也没关系，会自动只取链接"
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
  { icon: '📕', name: '小红书' },
  { icon: '📺', name: 'B站' },
  { icon: '＋', name: 'yt-dlp 支持的更多平台' },
]

// 从一段带宣传语/话题/表情的分享文本里只取出链接。
// 例：“宋雨琦：我真求求你们了 https://xhslink.cn/o/A1sqJElUVUz 这段文字复制好，打开【小红书】…”
// → https://xhslink.cn/o/A1sqJElUVUz
// 规则：先找 http(s) 链接（中文、空格、括号、引号处截断）；没有带协议的，再找裸域名并补 https://。
// 找不到时返回 null，调用方保留原文本走老路（后端会再给一次明确报错），不静默丢掉用户输入。
function cleanUrlTail(u) {
  let url = u.replace(/[.,;:!?。，、；：！？》>】」』]+$/, '')
  // 末尾多余的右括号（如“（链接）”包住时）只去掉多出来的那几个
  while (url.endsWith(')') && (url.match(/\(/g) || []).length < (url.match(/\)/g) || []).length) {
    url = url.slice(0, -1)
  }
  return url
}

function extractUrl(text) {
  const t = String(text || '')
  // 链接字符集排除：空白、引号、括号、中文字符（\u4e00-\u9fa5）、
  // 中日韩标点（\u3000-\u303f）、全角字符（\uFF00-\uFFEF，含，。、！等），
  // 这样“链接，记得点赞”“链接。这段文字”都能在链接处干净截断。
  const m = t.match(/https?:\/\/[^\s<>"'【】（）()\[\]{}\u4e00-\u9fa5\u3000-\u303F\uFF00-\uFFEF]+/)
  if (m) return cleanUrlTail(m[0])
  const m2 = t.match(/(?:www\.|[a-z0-9-]+\.)+(?:com|cn|net|io|me|tv|cc|top|xyz)(?:\/[^\s<>"'【】（）()\[\]{}\u4e00-\u9fa5\u3000-\u303F\uFF00-\uFFEF]*)?/i)
  if (m2) return cleanUrlTail('https://' + m2[0])
  return null
}

function submitCleaned() {
  const raw = inputUrl.value.trim()
  if (!raw) return
  const url = extractUrl(raw)
  if (url) inputUrl.value = url
  emit('submit', url || raw)
}

function handleSubmit() {
  submitCleaned()
}

function handlePaste() {
  setTimeout(() => {
    submitCleaned()
  }, 100)
}

// 一键粘贴：先读剪贴板，从中只提取链接再填入（宣传语、话题等一并去掉）。
// 剪贴板里找不到链接时不清空旧输入、不提交，只提示；读不到剪贴板时保留旧链接并提示手动粘贴。
async function handlePasteClick() {
  pasteHint.value = ''
  try {
    if (!navigator.clipboard?.readText) throw new Error('clipboard unsupported')
    const text = (await navigator.clipboard.readText()).trim()
    if (!text) {
      pasteHint.value = '剪贴板是空的，没有可粘贴的链接'
      return
    }
    const url = extractUrl(text)
    if (!url) {
      pasteHint.value = '剪贴板里没找到链接，请检查复制的内容'
      return
    }
    inputUrl.value = url
    setTimeout(() => {
      const u = inputUrl.value.trim()
      if (u) emit('submit', u)
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
