// Agregador del feed: junta todos los canales CONECTADOS (read-only).
// Un canal que falle no tumba a los demás. El resto sigue en mock en el frontend.
import { obtenerFeedML } from './ml-feed.mjs'
import { obtenerFeedWeb } from './web-feed.mjs'
import { obtenerFeedFalabella } from './falabella-feed.mjs'

const FUENTES = { mercadolibre: obtenerFeedML, web: obtenerFeedWeb, falabella: obtenerFeedFalabella }

export async function obtenerFeed() {
  const nombres = Object.keys(FUENTES)
  const res = await Promise.allSettled(nombres.map((n) => FUENTES[n]()))
  const out = []
  res.forEach((r, i) => {
    if (r.status === 'fulfilled') out.push(...r.value)
    else console.error('[feed] falló', nombres[i], r.reason?.message)
  })
  return out
}
