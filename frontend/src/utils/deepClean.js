// 深度清洗核心逻辑（移植自 dearhua 版 remove-video-metadata，已线上验证）：
// 流拷贝重封装 + 清容器元数据/章节 + 剥 H.264/HEVC SEI + 等长补丁重写 Lavf 编码器标识。
// 本模块不依赖 Vue / ffmpeg.wasm 实例，可被组件与本地验证脚本共用。

export const PRESETS = {
  pr:      { label: 'Adobe Premiere Pro 2024', comment: 'Exported with Adobe Premiere Pro 2024', tool: 'Adobe Premiere Pro 2024', suffix: 'pr-edition' },
  davinci: { label: 'DaVinci Resolve 19',      comment: 'Exported with DaVinci Resolve 19',      tool: 'DaVinci Resolve 19',      suffix: 'davinci-edition' },
  capcut:  { label: 'CapCut',                   comment: 'Exported with CapCut',                   tool: 'CapCut',                   suffix: 'capcut-edition' },
}

export const MAX_FILE = 500 * 1024 * 1024
export const WARN_FILE = 200 * 1024 * 1024

// 解析 ffmpeg -i 的日志输出，探测流构成（无音轨时不强写音频流参数）
export function parseProbeLog(logText) {
  const info = { hasVideo: false, hasAudio: false, videoCodec: '' }
  const lines = String(logText || '').split('\n')
  for (const line of lines) {
    if (!/Stream #/.test(line)) continue
    const v = line.match(/:\s*Video:\s*([a-z0-9_]+)/i)
    if (v) { info.hasVideo = true; info.videoCodec = v[1].toLowerCase() }
    if (/:\s*Audio:/i.test(line)) info.hasAudio = true
  }
  return info
}

// 组装与捐赠版完全一致的 ffmpeg 参数（仅音频/视频 handler 按探测结果条件化）
export function buildCleanArgs({ inName, outName, preset, hasVideo = true, hasAudio = true }) {
  const args = ['-i', inName, '-c', 'copy']
  if (hasVideo) {
    // H.264 SEI type 6 + HEVC SEI type 39|40 一并剥除（对另一编码即无操作）
    args.push('-bsf:v', 'filter_units=remove_types=6,filter_units=remove_types=39|40')
  }
  args.push('-map_metadata', '-1', '-map_chapters', '-1')
  args.push('-metadata', 'comment=' + preset.comment)
  if (hasVideo) args.push('-metadata:s:v:0', 'handler_name=VideoHandler')
  if (hasAudio) args.push('-metadata:s:a:0', 'handler_name=SoundHandler')
  args.push('-movflags', '+faststart', outName)
  return args
}

// 等长二进制补丁：把 Lavf 编码器串换成预设工具串（长度不变，容器偏移不受影响）
export function patchEncoder(data, toolStr) {
  const CH = 8192
  let s = ''
  for (let i = 0; i < data.length; i += CH) {
    s += String.fromCharCode.apply(null, data.subarray(i, Math.min(i + CH, data.length)))
  }
  const out = s.replace(/Lavf\d+\.\d+\.\d+/g, (m) => (toolStr + ' '.repeat(m.length)).slice(0, m.length))
  if (out === s) return data
  const res = new Uint8Array(data.length)
  for (let j = 0; j < out.length; j++) res[j] = out.charCodeAt(j) & 255
  return res
}

// 安全网：等长抹掉旧版专门处理的 Google 容器签名（重封装 + -map_metadata -1
// 本应已清掉它；若个别文件把它藏在非元数据盒里，这里保证与旧版同等效果）
const GOOGLE_SIGNATURE = 'ISO Media file produced by Google Inc.'
export function stripGoogleSignature(data) {
  const enc = new TextEncoder()
  const target = enc.encode(GOOGLE_SIGNATURE)
  const replacement = enc.encode('VideoHandler')
  let count = 0
  outer:
  for (let i = 0; i + target.length <= data.length; i++) {
    for (let j = 0; j < target.length; j++) {
      if (data[i + j] !== target[j]) continue outer
    }
    data.set(replacement, i)
    for (let j = replacement.length; j < target.length; j++) data[i + j] = 0
    count++
    i += target.length - 1
  }
  return count
}

export function outputName(fileName, preset) {
  const m = fileName.match(/\.[^.]+$/)
  let ext = m ? m[0].toLowerCase() : '.mp4'
  if (ext !== '.mp4' && ext !== '.mov') ext = '.mp4'
  const base = fileName.replace(/\.[^.]+$/, '')
  return { outFile: 'out' + ext, download: `${base}_${preset.suffix}${ext}`, ext }
}
