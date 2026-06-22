// erp-ml.mjs — Trae ventas crudas de las 3 cuentas ML y las normaliza.
// Reusa el OAuth/refresh del Monitor (ml-feed.mjs). Read-only sobre ML.
import { CUENTAS, cargarTok, get, ML } from "./ml-feed.mjs";
import { normalizarML } from "./erp-build.mjs";

async function ordenesCuenta(cuenta) {
  const ctx = { file: cuenta.file, tok: cargarTok(cuenta.file) };
  const uid = ctx.tok.user_id;
  const r = await get(`${ML}/orders/search/recent?seller=${uid}&sort=date_desc&limit=50`, ctx);
  return r.results || [];
}

// { ml1: Orden[]|null, ml2: ..., ml3: ... }. Una cuenta que falla -> null, no tumba al resto.
export async function ventasML() {
  const out = {};
  for (let i = 0; i < CUENTAS.length; i++) {
    const canal = "ml" + (i + 1);
    try { out[canal] = normalizarML(await ordenesCuenta(CUENTAS[i])); }
    catch (e) { out[canal] = null; console.error("[erp-ingesta] ML", canal, "falló:", e.message); }
  }
  return out;
}
