<template>
  <div id="app">
    <!-- 头部导航 -->
    <header class="app-header">
      <div class="logo">
        <span class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
        </span>
        <span class="logo-text">VidSnap</span>
      </div>
      <p class="logo-subtitle">自托管多平台音视频高速解析 · 零中转 · 直连下载</p>
    </header>

    <!-- 主体区域 -->
    <main class="main">
      <!-- 链接输入框 -->
      <UrlInput
        ref="urlInputRef"
        :loading="loading"
        :error="parseError"
        @submit="handleParse"
      />

      <!-- 解析结果展示区 -->
      <Transition name="fade">
        <div v-if="result" class="result-area">
          <VideoCard :info="result" />
          <FormatList :formats="result.formats" :title="result.title" />
        </div>
      </Transition>

      <!-- 空态引导提示 -->
      <div v-if="!result && !loading" class="empty-state">
        <div class="empty-guide-card">
          <div class="guide-title">使用方法</div>
          <div class="steps">
            <div class="step-item">
              <span class="step-num">1</span>
              <span>复制平台视频链接</span>
            </div>
            <div class="step-item">
              <span class="step-num">2</span>
              <span>粘贴到上方输入框点击「解析」</span>
            </div>
            <div class="step-item">
              <span class="step-num">3</span>
              <span>下拉选择清晰度/音频并下载</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="app-footer">
      <p>
        VidSnap · 个人学习与测试工具 ·
        <a href="https://github.com/santalin87/Video-Snap" target="_blank" rel="noopener">
          GitHub 仓库
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
    Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background-color: #f8fafc;
  color: #0f172a;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
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
  padding: 44px 20px 24px;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.logo-icon {
  background: #2563eb;
  color: #ffffff;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
}

.logo-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.main {
  flex: 1;
  max-width: 680px;
  margin: 0 auto;
  padding: 0 16px 48px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-area {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.empty-state {
  margin-top: 12px;
}

.empty-guide-card {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  padding: 20px;
  text-align: left;
}

.guide-title {
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #64748b;
}

.step-num {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #334155;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.app-footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: #94a3b8;
  border-top: 1px solid #e2e8f0;
}

.app-footer a {
  color: #2563eb;
  text-decoration: none;
}
.app-footer a:hover {
  text-decoration: underline;
}

/* 动效 */
.fade-enter-active {
  transition: all 0.25s ease-out;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
</style>
