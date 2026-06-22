// erp-ingesta.mjs — Lee ventas confirmadas (Web + ML×3) y las manda al núcleo como
// movimientos negativos. Idempotente; respeta la marca de agua por canal (erp-cursor.json).
// Uso: node server/erp-ingesta.mjs [--once] [--dry]   (--dry: arma pero NO postea)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { construirVentas } from "./erp-build.mjs";
import { ventasWeb } from "./erp-web.mjs";
import { ventasML } from "./erp-ml.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CURSOR_FILE = path.join(HERE, "erp-cursor.json");
const NUCLEO_URL = process.env.ERP_NUCLEO_URL || "https://erp-nucleo.vercel.app";
const NUCLEO_KEY = process.env.ERP_NUCLEO_KEY || "";
const DRY = process.argv.includes("--dry");
const OVERLAP_MS = 36 * 3600 * 1000; // re-escanea 36h: atrapa ventas que se confirman tarde (idempotencia dedupe)

const log = (...a) => console.log(new Date().toLocaleTimeString("es-CL"), "[erp-ingesta]", ...a);

function leerCursor() { try { return JSON.parse(fs.readFileSync(CURSOR_FILE, "utf8")); } catch { return {}; } }
function guardarCursor(c) { fs.writeFileSync(CURSOR_FILE, JSON.stringify(c, null, 2)); }

async function nucleo(metodo, ruta, body) {
  const r = await fetch(NUCLEO_URL + ruta, {
    method: metodo,
    headers: { "x-erp-key": NUCLEO_KEY, ...(body ? { "content-type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(ruta + " -> " + r.status);
  return r.json();
}

async function main() {
  if (!NUCLEO_KEY) { console.error("Falta ERP_NUCLEO_KEY"); process.exit(1); }
  const cursor = leerCursor();
  const productos = await nucleo("GET", "/api/productos");
  const codigosConocidos = new Set(productos.map((p) => p.codigo));
  log("códigos conocidos en el núcleo:", codigosConocidos.size, DRY ? "(DRY)" : "");
  if (codigosConocidos.size < 50) { console.error("[erp-ingesta] catálogo del núcleo sospechosamente chico (" + codigosConocidos.size + ") — abortando para no mandar todo a saltados"); process.exit(1); }

  const canales = {};
  try { canales.web = await ventasWeb(); } catch (e) { canales.web = null; log("Web falló:", e.message); }
  try { Object.assign(canales, await ventasML()); } catch (e) { log("ventasML falló:", e.message); }

  let totMov = 0, totSalt = 0;
  for (const [canal, ordenes] of Object.entries(canales)) {
    if (!ordenes) continue; // ese canal falló esta corrida
    if (cursor[canal] == null) { log(canal, "sin marca de agua sembrada — se omite (sembrar erp-cursor.json)"); continue; }
    const base = cursor[canal];
    const cursorTs = base - OVERLAP_MS; // C1: ventana solapada
    const { movimientos, saltados, maxTs } = construirVentas({ ordenes, canal, codigosConocidos, cursorTs });
    if (saltados.length) { totSalt += saltados.length; log(canal, "saltados (SKU sin mapear):", saltados.length, "→", saltados.slice(0, 5).map((s) => s.sku).join(", ")); }
    if (!movimientos.length) { log(canal, "sin ventas nuevas"); continue; }
    if (DRY) { log(canal, "DRY — mandaría", movimientos.length, "movimientos"); totMov += movimientos.length; continue; }
    try {
      const r = await nucleo("POST", "/api/movimientos", movimientos);
      cursor[canal] = Math.max(base, maxTs); // avanza solo hacia adelante (nunca retrocede por el solape)
      guardarCursor(cursor);
      totMov += movimientos.length;
      log(canal, "enviado:", JSON.stringify(r), "cursor→", new Date(maxTs).toISOString());
    } catch (e) {
      log(canal, "POST falló (se reintenta al próximo ciclo):", e.message);
    }
  }
  log("listo. movimientos:", totMov, "saltados:", totSalt);
  process.exit(0);
}
main().catch((e) => { console.error("[erp-ingesta] error fatal:", e.message); process.exit(1); });
