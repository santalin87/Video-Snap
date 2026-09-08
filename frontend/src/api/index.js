import axios from 'axios'

// 生产环境：VITE_API_BASE_URL 指向 VPS 后端（通过 GitHub Secrets 注入）
// 开发环境：Vite proxy 会转发 /api 到本地 :8000，所以默认用 /api
const BASE_URL = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api`
  : '/api'

const http = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 解析可能需要几秒
})

/**
 * 解析视频 URL
 * @param {string} url - 视频链接
 * @returns {Promise} 包含格式列表的响应
 */
export async function parseUrl(url) {
  const response = await http.post('/parse', { url })
  return response.data
}

/**
 * 生成带 Content-Disposition 附件头的直接下载 URL
 * 触发浏览器原生下载管理器，而不是打开媒体播放器
 */
export function getDownloadUrl(targetUrl, filename) {
  const encodedUrl = encodeURIComponent(targetUrl)
  const encodedName = encodeURIComponent(filename)
  return `${BASE_URL}/download?url=${encodedUrl}&filename=${encodedName}`
}

