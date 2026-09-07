import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],

    // 生产构建时支持子路径（GitHub Pages 需要 /Video-Snap/）
    base: env.VITE_BASE_PATH || '/',

    server: {
      port: 5173,
      proxy: {
        // 开发时把 /api 请求转发到本地后端
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
