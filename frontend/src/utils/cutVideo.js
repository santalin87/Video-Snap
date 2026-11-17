// 视频截取编排：浏览器本地 FFmpeg 流拷贝切段 + concat 拼接，移植自 dearhua video-cutter。
// 与 cleanVideo.js 的清洗共用同一套引擎加载方式（jsdelivr @ffmpeg/core@0.12.6），
// 但用独立的模块级单例：截取页不碰清洗页的进度映射与探测日志，互不干扰。
// 切法：每段 `-ss 起点 -i 输入 -t 长度 -c copy`（流拷贝、不重编、画质零损失），
// 多段用 concat demuxer 拼成一个文件。无损切只能落在关键帧上，切点误差 ±1–3 秒。
import { FFmpeg } from '@ffmpeg/ffmpeg'
import { toBlobURL, fetchFile } from '@ffmpeg/util'
import { MAX_FILE, WARN_FILE } from './deepClean.js'

const CORE_BASE = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.6/dist/esm'

let ffmpeg = null
let engineLoaded = false
let phaseStart = 0
let phaseEnd = 100

function setPhase(start, end, onProgress) {
  phaseStart = start
  phaseEnd = end
  onProgress(start)
}

async function ensureEngine(onStatus, onProgress) {
  if (engineLoaded) return
  if (!ffmpeg) {
    ffmpeg = new FFmpeg()
    ffmpeg.on('log', () => {})
    ffmpeg.on('progress', ({ progress }) => {
      const pct = Math.max(0, Math.min(100, Math.round((progress || 0) * 100)))
      onProgress(phaseStart + Math.round(((phaseEnd - phaseStart) * pct) / 100))
    })
  }
  onStatus('正在加载视频引擎（约 30MB，仅首次）…')
  setPhase(0, 15, onProgress)
  await ffmpeg.load({
    coreURL: await toBlobURL(`${CORE_BASE}/ffmpeg-core.js`, 'text/javascript'),
    wasmURL: await toBlobURL(`${CORE_BASE}/ffmpeg-core.wasm`, 'application/wasm'),
  })
  engineLoaded = true
}

/**
 * 按 segments 切段并拼成一个视频。
 * @param {File|Blob} file - 原视频（建议 MP4/MOV）
 * @param {{start:number,end:number}[]} segments - 秒，需按开始时间排好序，每段 ≥0.2 秒
 * @returns {{ blob, filename, size, totalKept }}
 */
export async function cutVideoFile({ file, segments, onStatus = () => {}, onProgress = () => {} }) {
  const list = (segments || [])
    .map((s) => ({ start: +s.start || 0, end: +s.end || 0 }))
    .filter((s) => s.end - s.start >= 0.2)
    .sort((a, b) => a.start - b.start)
  if (!list.length) throw new Error('请先在时间轴上选至少一段（每段至少 0.2 秒）')
  if (file.size > MAX_FILE) throw new Error('文件过大，最大支持 500 MB')

  const inName = 'in_' + (file.name || 'video.mp4').replace(/[^a-zA-Z0-9.]/g, '_')
  const baseName = (file.name || 'video.mp4').replace(/\.[^.]+$/, '') || 'video'
  const outName = 'out_cut.mp4'
  const segNames = list.map((_, i) => `seg${i}.mp4`)
  const totalKept = list.reduce((t, s) => t + (s.end - s.start), 0)

  onProgress(0)
  try {
    await ensureEngine(onStatus, onProgress)

    onStatus('正在读入原片…')
    setPhase(15, 20, onProgress)
    await ffmpeg.writeFile(inName, await fetchFile(file))

    // 逐段流拷贝切出
    for (let i = 0; i < list.length; i++) {
      const s = list[i]
      const dur = Math.max(0.2, s.end - s.start)
      onStatus(`正在切第 ${i + 1}/${list.length} 段（${s.start.toFixed(1)}–${s.end.toFixed(1)} 秒）…`)
      setPhase(20 + Math.round((60 * i) / list.length), 20 + Math.round((60 * (i + 1)) / list.length), onProgress)
      const code = await ffmpeg.exec([
        '-ss', s.start.toFixed(2), '-i', inName,
        '-t', dur.toFixed(2), '-c', 'copy', '-movflags', '+faststart', segNames[i],
      ])
      if (code !== 0) throw new Error(`第 ${i + 1} 段切取失败（退出码 ${code}），文件可能不受支持`)
    }

    // 单段直接就是成品；多段用 concat 拼成一个
    let data
    if (list.length === 1) {
      data = await ffmpeg.readFile(segNames[0])
    } else {
      onStatus('正在把多段拼成一个视频…')
      setPhase(80, 90, onProgress)
      const txt = segNames.map((n) => `file '${n}'\n`).join('')
      await ffmpeg.writeFile('list.txt', new TextEncoder().encode(txt))
      const code = await ffmpeg.exec([
        '-f', 'concat', '-safe', '0', '-i', 'list.txt',
        '-c', 'copy', '-movflags', '+faststart', outName,
      ])
      if (code !== 0) throw new Error('拼接失败（退出码 ' + code + '）')
      data = await ffmpeg.readFile(outName)
    }
    if (typeof data === 'string') throw new Error('读取处理结果失败')

    setPhase(90, 100, onProgress)
    const blob = new Blob([data.buffer], { type: 'video/mp4' })
    onProgress(100)
    return {
      blob,
      filename: `${baseName}_cut.mp4`,
      size: blob.size,
      totalKept,
    }
  } finally {
    if (ffmpeg && engineLoaded) {
      for (const n of [inName, outName, 'list.txt', ...segNames]) {
        await ffmpeg.deleteFile(n).catch(() => {})
      }
    }
  }
}

export { MAX_FILE, WARN_FILE }
