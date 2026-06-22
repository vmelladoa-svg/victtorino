// Scraper READ-ONLY de MercadoLibre (C1/C2/C3) -> formato Comanda del monitor.
// SOLO lee: orders/search/recent + questions/search. No responde, no escribe nada en ML.
// Único efecto local: si un token expiró, lo refresca por OAuth y reescribe su JSON.
// ponytail: corre como middleware de Vite (dev). Para producción, mover a un server propio.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
export const ML = 'https://api.mercadolibre.com'

// Carpeta de secretos (tokens + .env). Autocontenida: busca primero secrets/ del proyecto
// (despliegue en el PC de bodega), luego la raíz del repo (desarrollo en el notebook).
function dirSecretos() {
  const cands = [process.env.MONITOR_SECRETS, path.join(HERE, '..', 'secrets'), path.resolve(HERE, '..', '..')].filter(Boolean)
  for (const d of cands) { try { if (fs.existsSync(path.join(d, 'tokens_cuenta3.json'))) return d } catch { /* */ } }
  return cands[cands.length - 1]
}
const SECRETS = dirSecretos()

// Credenciales OAuth (para refrescar) desde env o desde SECRETS/.env.
function envSecreto(key, def = '') {
  if (process.env[key]) return process.env[key]
  try {
    const txt = fs.readFileSync(path.join(SECRETS, '.env'), 'utf8')
    const m = txt.match(new RegExp('^' + key + '=(.*)$', 'm'))
    return m ? m[1].trim() : def
  } catch { return def }
}
const CLIENT_ID = envSecreto('ML_CLIENT_ID', '3959231945649654')
const CLIENT_SECRET = envSecreto('ML_CLIENT_SECRET')

export const CUENTAS = [
  { nombre: 'C1 · PREMIUMGRIFERIAS1', file: 'tokens_cuenta1.json' },
  { nombre: 'C2 · VICTTORINOFICIAL2', file: 'tokens_cuenta2.json' },
  { nombre: 'C3 · NOVAGRIFERIAS3',    file: 'tokens_cuenta3.json' },
]

const VENTANA_MS = 24 * 3600 * 1000 // solo lo de las últimas 24 h

export function cargarTok(file) {
  return JSON.parse(fs.readFileSync(path.join(SECRETS, file), 'utf8'))
}

export async function refrescar(tok, file) {
  const r = await fetch(`${ML}/oauth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      refresh_token: tok.refresh_token,
    }),
  })
  if (!r.ok) throw new Error('refresh ' + r.status)
  const nuevo = { ...tok, ...(await r.json()) }
  fs.writeFileSync(path.join(SECRETS, file), JSON.stringify(nuevo, null, 2))
  return nuevo
}

// GET autenticado con auto-refresh ante 401.
export async function get(url, ctx) {
  let r = await fetch(url, { headers: { Authorization: 'Bearer ' + ctx.tok.access_token } })
  if (r.status === 401) {
    ctx.tok = await refrescar(ctx.tok, ctx.file)
    r = await fetch(url, { headers: { Authorization: 'Bearer ' + ctx.tok.access_token } })
  }
  if (!r.ok) throw new Error(url.split('?')[0] + ' -> ' + r.status)
  return r.json()
}

// Detalle de ítems (título, precio, foto) en lote — máx 20 ids por llamada.
async function items(ids, ctx) {
  const out = {}
  const u = [...new Set(ids)].filter(Boolean)
  for (let i = 0; i < u.length; i += 20) {
    const lote = u.slice(i, i + 20).join(',')
    const arr = await get(`${ML}/items?ids=${lote}&attributes=id,title,price,secure_thumbnail,thumbnail`, ctx)
    for (const x of arr) {
      if (x.code === 200 && x.body) {
        out[x.body.id] = {
          producto: x.body.title || '',
          precio: x.body.price || 0,
          foto: (x.body.secure_thumbnail || x.body.thumbnail || '').replace('http://', 'https://'),
        }
      }
    }
  }
  return out
}

async function deCuenta(cuenta) {
  const ctx = { file: cuenta.file, tok: cargarTok(cuenta.file) }
  const uid = ctx.tok.user_id
  const desde = Date.now() - VENTANA_MS

  // Ventas
  const ord = await get(`${ML}/orders/search/recent?seller=${uid}&sort=date_desc&limit=25`, ctx)
  const ventas = (ord.results || []).filter((o) => Date.parse(o.date_created) >= desde)

  // Preguntas sin responder
  const pre = await get(`${ML}/questions/search?seller_id=${uid}&status=UNANSWERED&limit=25&api_version=4`, ctx)
  const preguntas = (pre.questions || []).filter((q) => Date.parse(q.date_created) >= desde)

  // Detalle de ítems (para foto/precio de preguntas y foto de ventas)
  const ids = [
    ...ventas.map((o) => o.order_items?.[0]?.item?.id),
    ...preguntas.map((q) => q.item_id),
  ]
  const det = await items(ids, ctx)

  const comandas = []

  for (const o of ventas) {
    const it = o.order_items?.[0]?.item || {}
    const id = it.id
    const d = det[id] || {}
    const c = {
      id: 'o' + o.id,
      tipo: 'venta',
      canal: 'mercadolibre',
      cuenta: cuenta.nombre,
      producto: it.title || d.producto || '(sin título)',
      sku: it.seller_sku || id || '',
      monto: o.total_amount || 0,
      precio: o.total_amount || d.precio || 0,
      foto: d.foto || '',
      ingreso: Date.parse(o.date_created),
      validadoDefontana: false, // Defontana aún no conectado
    }
    // Envío + fecha de despacho desde el shipment (best-effort).
    const sid = o.shipping?.id
    if (sid) {
      try {
        const s = await get(`${ML}/shipments/${sid}`, ctx)
        c.envio = s.logistic_type === 'self_service' ? 'flex' : 'normal'
        const pend = !['shipped', 'delivered', 'not_delivered'].includes(s.status)
        const limite = s.shipping_option?.estimated_schedule_limit?.date
        if (pend && limite) c.despacharAntes = Date.parse(limite)
      } catch { /* sin detalle de envío */ }
    }
    comandas.push(c)
  }

  for (const q of preguntas) {
    const d = det[q.item_id] || {}
    comandas.push({
      id: 'q' + q.id,
      tipo: 'pregunta',
      canal: 'mercadolibre',
      cuenta: cuenta.nombre,
      producto: d.producto || q.item_id,
      sku: q.item_id || '',
      precio: d.precio || 0,
      foto: d.foto || '',
      pregunta: q.text || '',
      ingreso: Date.parse(q.date_created),
    })
  }

  return comandas
}

// Devuelve el feed unificado de las 3 cuentas. Una cuenta que falle no tumba al resto.
export async function obtenerFeedML() {
  const lotes = await Promise.allSettled(CUENTAS.map(deCuenta))
  const out = []
  lotes.forEach((l, i) => {
    if (l.status === 'fulfilled') out.push(...l.value)
    else console.error('[feed] falló', CUENTAS[i].nombre, l.reason?.message)
  })
  return out
}
