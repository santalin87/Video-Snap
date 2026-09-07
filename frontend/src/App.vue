<template>
  <div id="app">
    <header class="app-header">
      <div class="logo">
        <span class="logo-icon">⬇</span>
        <span class="logo-text">downX</span>
      </div>
      <p class="logo-subtitle">自托管多平台视频解析工具</p>
    </header>

    <main class="main">
      <!-- URL 输入区 -->
      <UrlInput
        ref="urlInputRef"
        :loading="loading"
        :error="parseError"
        @submit="handleParse"
      />

      <!-- 结果区 -->
      <Transition name="slide-up">
        <div v-if="result" class="result-area">
          <VideoCard :info="result" />
          <FormatList :formats="result.formats" :title="result.title" />
        </div>
      </Transition>

      <!-- 空态提示 -->
      <div v-if="!result && !loading" class="empty-state">
        <div class="empty-icons">
          <span>▶</span><span>𝕏</span><span>🎵</span><span>♪</span>
        </div>
        <p>粘贴任意平台的视频链接，即可解析下载</p>
        <p class="empty-sub">视频直接从平台 CDN 下载，不占用服务器流量</p>
      </div>
    </main>

    <footer class="app-footer">
      <p>
        仅供个人学习使用 ·
        <a href="https://github.com/YOUR_USERNAME/downX" target="_blank" rel="noopener">
          GitHub
        </a>
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { parseUrl } from './api/index.js'
import FormatList from './components/FormatList.vue'
import UrlInput from './components/UrlInput.vue'
import VideoCard from './components/VideoCard.vue'

const urlInputRef = ref(null)
const loading     = ref(false)
const parseError  = ref('')
const result      = ref(null)

async function handleParse(url) {
  loading.value    = true
  parseError.value = ''
  result.value     = null

  try {
    result.value = await parseUrl(url)
  } catch (err) {
    const msg =
      err.response?.data?.detail ||
      err.message ||
      '解析失败，请检查链接是否有效'
    parseError.value = msg
  } finally {
    loading.value = false
  }
}
</script>

<style>
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: #f8fafc;
  color: #1f2937;
  min-height: 100vh;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>

<style scoped>
.app-header {
  text-align: center;
  padding: 48px 20px 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 6px;
}

.logo-icon {
  font-size: 28px;
  background: #6366f1;
  color: #fff;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 28px;
  font-weight: 800;
  color: #1f2937;
  letter-spacing: -0.5px;
}

.logo-subtitle {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

.main {
  flex: 1;
  max-width: 720px;
  margin: 0 auto;
  padding: 0 20px 60px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: #9ca3af;
}

.empty-icons {
  font-size: 28px;
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-state p {
  margin: 0 0 6px;
  font-size: 15px;
}

.empty-sub {
  font-size: 12px !important;
  color: #d1d5db !important;
}

.app-footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: #d1d5db;
  border-top: 1px solid #f3f4f6;
}

.app-footer a {
  color: #6366f1;
  text-decoration: none;
}

/* 动画 */
.slide-up-enter-active {
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
