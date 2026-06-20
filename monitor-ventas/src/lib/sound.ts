// "Din-don" de alerta con Web Audio API: sin archivos de audio, sin dependencias.
// ponytail: dos osciladores secuenciales bastan; si se quiere un sonido de marca, reemplazar por un <audio src>.

let ctx: AudioContext | null = null

function tono(freq: number, inicio: number, dur: number) {
  if (!ctx) return
  const osc = ctx.createOscillator()
  const gain = ctx.createGain()
  osc.type = 'sine'
  osc.frequency.value = freq
  gain.gain.setValueAtTime(0, inicio)
  gain.gain.linearRampToValueAtTime(0.35, inicio + 0.02)
  gain.gain.exponentialRampToValueAtTime(0.001, inicio + dur)
  osc.connect(gain).connect(ctx.destination)
  osc.start(inicio)
  osc.stop(inicio + dur)
}

export function dinDon() {
  // El AudioContext debe crearse/reanudarse tras un gesto del usuario (políticas del navegador).
  if (!ctx) ctx = new AudioContext()
  if (ctx.state === 'suspended') ctx.resume()
  const t = ctx.currentTime
  tono(880, t, 0.18)        // din
  tono(659, t + 0.16, 0.3)  // don
}
