// 深度清洗编排：浏览器本地 FFmpeg 流拷贝重封装 + 剥 SEI + 重写编码器标识。
// 核心算法在 deepClean.js（与 dearhua 版一致）；这里只做“加载引擎 → 探测 → 清洗 → 补丁”
// 的编排，并被两处共用：净化页（用户选文件）和下载页（解析后一键下载净化版）。
// 引擎在模块级单例：两处共用一次加载，第二次清洗不用再下 30MB。

import { FFmpeg } from '@ffmpeg/ffmpeg'
import { toBlobURL, fetchFile } from '@ffmpeg/util'
import {
  PRESETS,
  parseProbeLog, buildCleanArgs, patchEncoder, stripGoogleSignature, outputName,
} from './deepClean.js'

const CORE_BASE = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.6/dist/esm'

let ffmpeg = null
let engineLoaded = false
let probeLog = ''
let lastPct = 0

function emitProgress(onProgress, pct) {
  // 进度条只进不退（探测阶段的 progress 事件也按清洗区间映射，不回跳）
  lastPct = Math.max(lastPct, pct)
  onProgress(lastPct)
}

async function ensureEngine(onStatus) {
  if (engineLoaded) return
  if (!ffmpeg) {
    ffmpeg = new FFmpeg()
    ffmpeg.on('log', ({ message }) => { probeLog += message + '\n' })
    ffmpeg.on('progress', ({ progress }) => {
      const pct = Math.max(0, Math.min(100, Math.round((progress || 0) * 100)))
      // 清洗阶段进度映射到 30%~85% 区间（与原净化页一致）
      if (typeof ensureEngine._onProgress === 'function') {
        emitProgress(ensureEngine._onProgress, 30 + Math.round(pct * 0.55))
      }
    })
  }
  onStatus('正在加载视频引擎（约 30MB，仅首次）…')
  await ffmpeg.load({
    coreURL: await toBlobURL(`${CORE_BASE}/ffmpeg-core.js`, 'text/javascript'),
    wasmURL: await toBlobURL(`${CORE_BASE}/ffmpeg-core.wasm`, 'application/wasm'),
  })
  engineLoaded = true
}

/**
 * 清洗一个视频文件（File / Blob + 文件名）。
 * @returns { blob, filename, presetLabel, size }
 */
export async function cleanVideoFile({ file, presetKey = 'davinci', onStatus = () => {}, onProgress = () => {} }) {
  const preset = PRESETS[presetKey] || PRESETS.davinci
  ensureEngine._onProgress = onProgress
  lastPct = 0
  onProgress(5)

  const inName = 'in_' + file.name.replace(/[^a-zA-Z0-9.]/g, '_')
  const { outFile, download } = outputName(file.name, preset)

  try {
    await ensureEngine(onStatus)

    await ffmpeg.writeFile(inName, await fetchFile(file))

    // 1) 探测流构成：无音轨不强写音频流参数
    onStatus('正在探测媒体流…')
    emitProgress(onProgress, 20)
    probeLog = ''
    await ffmpeg.exec(['-i', inName]).catch(() => 1)
    const streams = parseProbeLog(probeLog)

    // 2) 流拷贝重封装 + 清元数据/章节 + 剥 SEI
    onStatus('正在深度清洗（重封装 + 剥除平台标记）…')
    emitProgress(onProgress, 30)
    const args = buildCleanArgs({
      inName, outName: outFile, preset,
      hasVideo: streams.hasVideo, hasAudio: streams.hasAudio,
    })
    const code = await ffmpeg.exec(args)
    if (code !== 0) throw new Error('FFmpeg 处理失败（退出码 ' + code + '），文件可能不受支持')

    // 3) 等长补丁重写编码器标识 + Google 签名安全网
    onStatus('正在重写编码器标识…')
    emitProgress(onProgress, 90)
    let data = await ffmpeg.readFile(outFile)
    if (typeof data === 'string') throw new Error('读取处理结果失败')
    data = patchEncoder(data, preset.tool)
    stripGoogleSignature(data)

    const blob = new Blob([data.buffer], { type: 'video/mp4' })
    emitProgress(onProgress, 100)
    return { blob, filename: download, presetLabel: preset.label, size: blob.size }
  } finally {
    if (ffmpeg && engineLoaded) {
      await ffmpeg.deleteFile(inName).catch(() => {})
      await ffmpeg.deleteFile(outFile).catch(() => {})
    }
  }
}

/** 触发浏览器保存一个 Blob（用于一键流程：清洗完直接存文件，不经过下载链接展示）。 */
export function triggerBlobDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 5000)
}
