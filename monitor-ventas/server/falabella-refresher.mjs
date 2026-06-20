// Refrescador de Falabella: mantiene server/falabella_raw.json al día (read-only).
// Abre Chrome con un perfil dedicado y logueado, deja que la PROPIA app del Seller Center
// pida las órdenes (el WAF solo acepta ese request) y CAPTURA la respuesta de la red.
// No escribe nada en Falabella; solo lee.
//
// Uso:
//   1ª vez (login):  HEADED=1 node server/falabella-refresher.mjs   -> abre ventana, inicia sesión como Trade Global
//   Luego (vivo):    node server/falabella-refresher.mjs            -> headless, refresca cada INTERVAL_MIN
// Variables: HEADED=1 (ventana visible), INTERVAL_MIN (def 5), ONCE=1 (una sola pasada).

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const PROFILE = process.env.FALA_PROFILE || path.join(HERE, '.fala-profile')
const OUT = path.join(HERE, 'falabella_raw.json')
const ORDER_URL = 'https://sellercenter.falabella.com/order'
const LISTING = '/manage-orders/v2/listing'
const TABS_PENDIENTES = [/Env[ií]os de hoy/i, /Pr[óo]ximos env[íi]os/i] // grupos que necesitan despacho

const ARGV = process.argv.slice(2)
const HEADED = !!process.env.HEADED || ARGV.includes('--headed')
const ONCE = !!process.env.ONCE || ARGV.includes('--once')
const INTERVAL_MIN = Number(process.env.INTERVAL_MIN || 5)

const log = (...a) => console.log(new Date().toLocaleTimeString('es-CL'), '[fala]', ...a)

async function estaLogueado(page) {
  // Logueado si aparece el tablist de órdenes; si no, está en login/SSO.
  try {
    await page.waitForSelector('[role="tab"]', { timeout: 8000 })
    return true
  } catch { return false }
}

// Una pasada: navega, dispara las pestañas pendientes y captura las órdenes de la red.
async function capturar(page) {
  const ordenes = new Map()
  const onResp = async (resp) => {
    if (resp.url().includes(LISTING) && resp.status() === 200) {
      try { (((await resp.json()) || {}).data || []).forEach((o) => ordenes.set(o.orderId, o)) } catch { /* ignore */ }
    }
  }
  page.on('response', onResp)
  try {
    await page.goto(ORDER_URL, { waitUntil: 'domcontentloaded' })
    if (!(await estaLogueado(page))) { page.off('response', onResp); return null } // necesita login
    await page.waitForTimeout(2500) // deja que cargue el grupo por defecto
    for (const re of TABS_PENDIENTES) {
      const tab = page.getByRole('tab', { name: re })
      if (await tab.count()) { await tab.first().click().catch(() => {}); await page.waitForTimeout(2500) }
    }
  } finally {
    page.off('response', onResp)
  }
  return [...ordenes.values()]
}

function guardar(orders) {
  fs.writeFileSync(OUT, JSON.stringify({ capturadoEl: new Date().toISOString(), orders }, null, 1))
  log(`guardado falabella_raw.json (${orders.length} órdenes pendientes)`)
}

async function main() {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    headless: !HEADED,
    viewport: { width: 1280, height: 900 },
  })
  const page = ctx.pages()[0] || (await ctx.newPage())

  const pasada = async () => {
    const orders = await capturar(page)
    if (orders === null) {
      if (HEADED) {
        log('Falta iniciar sesión. Inicia sesión como Trade Global en la ventana abierta…')
        // espera hasta 5 min a que el login llegue a la pantalla de órdenes
        for (let i = 0; i < 60; i++) {
          await page.waitForTimeout(5000)
          if (await estaLogueado(page)) { const o = await capturar(page); if (o) guardar(o); return }
        }
        log('No se completó el login a tiempo.')
      } else {
        log('NO logueado. Corré una vez con  HEADED=1 node server/falabella-refresher.mjs  para iniciar sesión.')
      }
      return
    }
    guardar(orders)
  }

  await pasada()
  if (ONCE) { await ctx.close(); return }

  log(`refrescando cada ${INTERVAL_MIN} min (Ctrl+C para detener)`)
  setInterval(pasada, INTERVAL_MIN * 60_000)
}

main().catch((e) => { console.error('[fala] error fatal', e); process.exit(1) })
