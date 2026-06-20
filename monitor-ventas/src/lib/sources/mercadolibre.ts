import type { Comanda } from '../types'

// GET /feed = feed unificado de TODOS los canales conectados (read-only), servido por
// server/feed.mjs (hoy: MercadoLibre C1/C2/C3 + Web WooCommerce). El frontend hace un solo poll.
// Los scrapers viven en server/*-feed.mjs. Cada canal nuevo se suma ahí, sin tocar el frontend.
export async function obtenerNuevas(): Promise<Comanda[]> {
  const r = await fetch('/feed')
  if (!r.ok) throw new Error('feed ' + r.status)
  return r.json()
}
