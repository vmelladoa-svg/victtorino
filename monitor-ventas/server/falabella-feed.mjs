// Falabella (Seller Center, Trade Global SCD3F8C) — bridge READ-ONLY por CAPTURA.
// El endpoint manage-orders está tras WAF: solo responde a la propia app en el navegador.
// Por eso NO se llama desde el server; un refrescador (Playwright con el perfil logueado)
// vuelca las órdenes a server/falabella_raw.json y acá solo las mapeamos a Comanda.
// ponytail: si el archivo no existe o está viejo, devolvemos []; nada de inventar datos.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const RAW = path.join(HERE, 'falabella_raw.json')
const MESES = { ene: 0, feb: 1, mar: 2, abr: 3, may: 4, jun: 5, jul: 6, ago: 7, sep: 8, oct: 9, nov: 10, dic: 11 }

// "jun 22, 2026 12:00" -> epoch ms (hora local Chile). Devuelve null si no parsea.
function parseFecha(s) {
  if (!s) return null
  const m = String(s).match(/([a-zñ]{3})\s+(\d{1,2}),?\s+(\d{4})\s+(\d{1,2}):(\d{2})/i)
  if (!m) return null
  const mes = MESES[m[1].toLowerCase()]
  if (mes == null) return null
  return new Date(+m[3], mes, +m[2], +m[4], +m[5]).getTime()
}

const esFlex = (o) =>
  /flex|colecta|vendedor|seller/i.test((o.serviceLevel || '') + ' ' + (o.modality?.carrierGroup || ''))

export async function obtenerFeedFalabella() {
  let raw
  try { raw = JSON.parse(fs.readFileSync(RAW, 'utf8')) } catch { return [] }
  const orders = raw.orders || []
  return orders.map((o) => ({
    id: 'f' + (o.orderId || o.orderNumber),
    tipo: 'venta',
    canal: 'falabella',
    cuenta: 'Trade Global',
    producto: `Orden ${o.orderNumber} · ${o.noOfItems || 1} art. · ${o.serviceLevel || o.modality?.carrierGroup || ''}`.trim(),
    sku: o.orderNumber || o.deliveryOrderNumber || '',
    monto: parseInt(String(o.price || '').replace(/[^0-9]/g, ''), 10) || 0,
    precio: parseInt(String(o.price || '').replace(/[^0-9]/g, ''), 10) || 0,
    foto: '', // el listado no trae imagen; el detalle por orden queda pendiente
    ingreso: Date.parse(o.utcOrderDate) || parseFecha(o.orderDate) || Date.now(),
    envio: esFlex(o) ? 'flex' : 'normal',
    despacharAntes: parseFecha(o.promisedShippingDate) || undefined,
    validadoDefontana: false,
  }))
}
