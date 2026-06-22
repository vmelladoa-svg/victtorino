# ERP Fase 2 — Ingesta de ventas (Web + ML) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un trabajo en la PC de bodega que lee ventas confirmadas de WooCommerce + Mercado Libre ×3 y las manda al núcleo del ERP como movimientos negativos, una sola vez, posteriores a la última toma.

**Architecture:** Todo en `monitor-ventas/server/`. Una función pura (`erp-build.mjs`: normalizadores + `construirVentas`) hace la lógica contable y se testea sola. Fetchers delgados (`erp-ml.mjs`, `erp-web.mjs`) reusan el OAuth de ML y el cliente Woo del Monitor. Un orquestador (`erp-ingesta.mjs`) lee el cursor, consulta los códigos del núcleo, arma y postea los movimientos, y avanza la marca de agua. Una tarea de Windows lo corre cada ~10-15 min.

**Tech Stack:** Node ESM (`.mjs` plano), `node --test` (sin tsx), `fetch` nativo. El núcleo (Fase 0) NO se modifica.

## Global Constraints

- **Directorio de trabajo:** `C:\Users\dell\victtorino\monitor-ventas` (repo victtorino; el código va en `monitor-ventas/server/`).
- JS plano ESM `.mjs`. Tests con `node --test server/erp-build.test.mjs` (sin TypeScript, sin tsx).
- Movimiento al núcleo: `{ codigo, tipo: "venta", cantidad: -qty, canal, ref: String(orderId) }`. `canal ∈ {"web","ml1","ml2","ml3"}`. Idempotente por `(canal, ref, codigo)` (lo garantiza el núcleo).
- Marca de agua por canal en `server/erp-cursor.json` (`{web,ml1,ml2,ml3}` en ms epoch). Solo se procesan órdenes con `fecha > cursorTs`. El cursor avanza a `maxTs` **solo si el POST al núcleo fue OK**.
- Filtro de seguridad: la ingesta lee `GET /api/productos` del núcleo y **solo manda movimientos de códigos que existen**; los demás van a `saltados[]` (log), nunca al POST (un código desconocido aborta el lote en el núcleo).
- Solo ventas **confirmadas**: ML `o.status === 'paid'`; Web se filtra por query `status=processing,completed`.
- Núcleo vía `process.env.ERP_NUCLEO_URL` (def `https://erp-nucleo.vercel.app`) y `ERP_NUCLEO_KEY`; header `x-erp-key`.
- Reusar la plomería del Monitor (no duplicar OAuth ni creds): exportar helpers de `ml-feed.mjs` y `web-feed.mjs` (cambios solo aditivos: agregar `export`, sin tocar comportamiento).
- El Monitor (su `/feed`) debe seguir funcionando igual.

---

### Task 1: Lógica pura — `erp-build.mjs` (normalizadores + construirVentas) + tests

**Files:**
- Create: `monitor-ventas/server/erp-build.mjs`
- Test: `monitor-ventas/server/erp-build.test.mjs`

**Interfaces:**
- Produces:
  ```
  normalizarWeb(rawOrders) -> Orden[]
  normalizarML(rawOrders)  -> Orden[]
  // Orden = { orderId: string, fecha: number(ms), confirmada: boolean, lineas: {sku:string, qty:number}[] }
  construirVentas({ ordenes: Orden[], canal: string, codigosConocidos: Set<string>, cursorTs: number })
    -> { movimientos: {codigo,tipo:"venta",cantidad,canal,ref}[], saltados: {canal,orderId,sku,qty}[], maxTs: number }
  ```

- [ ] **Step 1: Escribir el test `server/erp-build.test.mjs`**

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { normalizarWeb, normalizarML, construirVentas } from "./erp-build.mjs";

test("normalizarWeb extrae todas las líneas con sku y cantidad", () => {
  const out = normalizarWeb([{
    id: 12, date_created_gmt: "2026-06-20T10:00:00",
    line_items: [{ sku: "A1", quantity: 2 }, { sku: "B2", quantity: 1 }],
  }]);
  assert.equal(out.length, 1);
  assert.equal(out[0].orderId, "12");
  assert.equal(out[0].confirmada, true);
  assert.deepEqual(out[0].lineas, [{ sku: "A1", qty: 2 }, { sku: "B2", qty: 1 }]);
  assert.ok(out[0].fecha > 0);
});

test("normalizarML marca confirmada solo si status==='paid'", () => {
  const raw = [
    { id: 1, status: "paid", date_created: "2026-06-20T10:00:00.000-04:00", order_items: [{ item: { seller_sku: "A1" }, quantity: 3 }] },
    { id: 2, status: "cancelled", date_created: "2026-06-20T11:00:00.000-04:00", order_items: [{ item: { seller_sku: "C3" }, quantity: 1 }] },
  ];
  const out = normalizarML(raw);
  assert.equal(out[0].confirmada, true);
  assert.equal(out[0].lineas[0].sku, "A1");
  assert.equal(out[0].lineas[0].qty, 3);
  assert.equal(out[1].confirmada, false);
});

const ordenWeb = (orderId, fecha, lineas, confirmada = true) => ({ orderId: String(orderId), fecha, confirmada, lineas });

test("construirVentas: multi-línea genera un movimiento por línea", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(12, 2000, [{ sku: "A1", qty: 2 }, { sku: "B2", qty: 1 }, { sku: "C3", qty: 4 }])],
    canal: "web", codigosConocidos: new Set(["A1", "B2", "C3"]), cursorTs: 1000,
  });
  assert.equal(r.movimientos.length, 3);
  assert.deepEqual(r.movimientos[0], { codigo: "A1", tipo: "venta", cantidad: -2, canal: "web", ref: "12" });
  assert.equal(r.movimientos[2].cantidad, -4);
});

test("construirVentas: no confirmada no genera movimiento", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(1, 2000, [{ sku: "A1", qty: 1 }], false)],
    canal: "web", codigosConocidos: new Set(["A1"]), cursorTs: 1000,
  });
  assert.equal(r.movimientos.length, 0);
});

test("construirVentas: orden anterior o igual al cursor no entra", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(1, 1000, [{ sku: "A1", qty: 1 }]), ordenWeb(2, 999, [{ sku: "A1", qty: 1 }])],
    canal: "web", codigosConocidos: new Set(["A1"]), cursorTs: 1000,
  });
  assert.equal(r.movimientos.length, 0); // 1000 no es > 1000; 999 < 1000
});

test("construirVentas: SKU desconocido va a saltados, no a movimientos", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(7, 2000, [{ sku: "A1", qty: 1 }, { sku: "ZZZ", qty: 9 }])],
    canal: "ml1", codigosConocidos: new Set(["A1"]), cursorTs: 0,
  });
  assert.deepEqual(r.movimientos.map((m) => m.codigo), ["A1"]);
  assert.equal(r.saltados.length, 1);
  assert.equal(r.saltados[0].sku, "ZZZ");
});

test("construirVentas: maxTs es la mayor fecha procesada (avanza el cursor)", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(1, 2000, [{ sku: "A1", qty: 1 }]), ordenWeb(2, 5000, [{ sku: "A1", qty: 1 }])],
    canal: "web", codigosConocidos: new Set(["A1"]), cursorTs: 1000,
  });
  assert.equal(r.maxTs, 5000);
});

test("construirVentas: dos líneas de la misma orden comparten ref", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(99, 2000, [{ sku: "A1", qty: 1 }, { sku: "B2", qty: 1 }])],
    canal: "web", codigosConocidos: new Set(["A1", "B2"]), cursorTs: 0,
  });
  assert.equal(r.movimientos[0].ref, "99");
  assert.equal(r.movimientos[1].ref, "99");
});

test("construirVentas: sin órdenes nuevas, maxTs queda en el cursor", () => {
  const r = construirVentas({ ordenes: [], canal: "web", codigosConocidos: new Set(), cursorTs: 1234 });
  assert.equal(r.maxTs, 1234);
  assert.equal(r.movimientos.length, 0);
});
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `cd "C:/Users/dell/victtorino/monitor-ventas" && node --test server/erp-build.test.mjs`
Expected: FAIL (`Cannot find module './erp-build.mjs'`).

- [ ] **Step 3: Crear `server/erp-build.mjs`**

```js
// erp-build.mjs — Lógica pura de la ingesta de ventas al núcleo. Sin I/O.
// Forma común "Orden": { orderId, fecha(ms), confirmada, lineas: [{sku, qty}] }.

// WooCommerce crudo -> Orden[]. El query ya filtra a confirmadas, así que confirmada=true.
export function normalizarWeb(rawOrders) {
  return (rawOrders || []).map((o) => ({
    orderId: String(o.id),
    fecha: Date.parse((o.date_created_gmt ? o.date_created_gmt + "Z" : o.date_created)) || 0,
    confirmada: true,
    lineas: (o.line_items || []).map((li) => ({ sku: String(li.sku || ""), qty: Number(li.quantity || 0) })),
  }));
}

// Mercado Libre crudo -> Orden[]. confirmada solo si status==='paid'.
export function normalizarML(rawOrders) {
  return (rawOrders || []).map((o) => ({
    orderId: String(o.id),
    fecha: Date.parse(o.date_created) || 0,
    confirmada: o.status === "paid",
    lineas: (o.order_items || []).map((oi) => ({ sku: String(oi.item?.seller_sku || ""), qty: Number(oi.quantity || 0) })),
  }));
}

// Arma los movimientos de venta para el núcleo. Solo órdenes confirmadas y con
// fecha > cursorTs. Cada línea con SKU conocido -> movimiento; si no -> saltados.
export function construirVentas({ ordenes, canal, codigosConocidos, cursorTs }) {
  const movimientos = [];
  const saltados = [];
  let maxTs = cursorTs;
  for (const o of ordenes || []) {
    if (!o.confirmada) continue;
    if (!(o.fecha > cursorTs)) continue;
    if (o.fecha > maxTs) maxTs = o.fecha;
    for (const l of o.lineas || []) {
      if (!(l.qty > 0)) continue;
      if (l.sku && codigosConocidos.has(l.sku)) {
        movimientos.push({ codigo: l.sku, tipo: "venta", cantidad: -l.qty, canal, ref: o.orderId });
      } else {
        saltados.push({ canal, orderId: o.orderId, sku: l.sku, qty: l.qty });
      }
    }
  }
  return { movimientos, saltados, maxTs };
}
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `cd "C:/Users/dell/victtorino/monitor-ventas" && node --test server/erp-build.test.mjs`
Expected: 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/dell/victtorino"
git add monitor-ventas/server/erp-build.mjs monitor-ventas/server/erp-build.test.mjs
git commit -m "feat(erp-ingesta): lógica pura construirVentas + normalizadores (Fase 2 task 1)"
```

---

### Task 2: Fetchers — reuso de plomería + `erp-ml.mjs` + `erp-web.mjs`

**Files:**
- Modify: `monitor-ventas/server/ml-feed.mjs` (agregar `export` a helpers, sin cambiar lógica)
- Modify: `monitor-ventas/server/web-feed.mjs` (agregar `export` a `getOrders` y `WC_BASE`)
- Create: `monitor-ventas/server/erp-ml.mjs`
- Create: `monitor-ventas/server/erp-web.mjs`

**Interfaces:**
- Consumes: `normalizarML`, `normalizarWeb` (de `erp-build.mjs`).
- Produces: `ventasWeb() -> Promise<Orden[]>`; `ventasML() -> Promise<{ml1:Orden[]|null, ml2:..., ml3:...}>` (null = esa cuenta falló).

- [ ] **Step 1: Exportar helpers en `server/ml-feed.mjs`**

Agregar la palabra `export` (sin cambiar nada más) a estas declaraciones existentes:
- `const ML = 'https://api.mercadolibre.com'` → `export const ML = ...`
- `const CUENTAS = [...]` → `export const CUENTAS = [...]`
- `function cargarTok(file)` → `export function cargarTok(file)`
- `async function refrescar(tok, file)` → `export async function refrescar(tok, file)`
- `async function get(url, ctx)` → `export async function get(url, ctx)`

(No tocar el resto del archivo; `obtenerFeedML` y el Monitor siguen igual.)

- [ ] **Step 2: Exportar helpers en `server/web-feed.mjs`**

Agregar `export` (sin cambiar lógica) a:
- `const WC_BASE = process.env.WC_STORE_URL || 'https://tradeglobalchile.cl'` → `export const WC_BASE = ...`
- `async function getOrders(url)` → `export async function getOrders(url)`

- [ ] **Step 3: Crear `server/erp-ml.mjs`**

```js
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
```

- [ ] **Step 4: Crear `server/erp-web.mjs`**

```js
// erp-web.mjs — Trae ventas confirmadas de WooCommerce y las normaliza.
// Reusa el cliente Woo del Monitor (web-feed.mjs). Read-only.
import { getOrders, WC_BASE } from "./web-feed.mjs";
import { normalizarWeb } from "./erp-build.mjs";

export async function ventasWeb() {
  const url = `${WC_BASE}/wp-json/wc/v3/orders?per_page=50&orderby=date&order=desc&status=processing,completed`;
  const raw = await getOrders(url);
  return normalizarWeb(raw);
}
```

- [ ] **Step 5: Verificar que los módulos cargan (imports OK)**

Run: `cd "C:/Users/dell/victtorino/monitor-ventas" && node -e "Promise.all([import('./server/erp-ml.mjs'),import('./server/erp-web.mjs')]).then(()=>console.log('ok'))"`
Expected: imprime `ok` (valida que los exports y los imports resuelven; no llama a las APIs).

- [ ] **Step 6: Confirmar que el suite sigue verde**

Run: `cd "C:/Users/dell/victtorino/monitor-ventas" && node --test server/erp-build.test.mjs`
Expected: 9 tests PASS (los exports añadidos no rompen nada).

- [ ] **Step 7: Commit**

```bash
cd "C:/Users/dell/victtorino"
git add monitor-ventas/server/ml-feed.mjs monitor-ventas/server/web-feed.mjs monitor-ventas/server/erp-ml.mjs monitor-ventas/server/erp-web.mjs
git commit -m "feat(erp-ingesta): fetchers ML+Web reusando plomería del Monitor (Fase 2 task 2)"
```

---

### Task 3: Orquestador `erp-ingesta.mjs` + tarea Windows

**Files:**
- Create: `monitor-ventas/server/erp-ingesta.mjs`
- Create: `monitor-ventas/server/erp_ingesta.cmd`
- Modify: `monitor-ventas/.gitignore` (ignorar `server/erp-cursor.json` y `server/erp_ingesta.log`)

**Interfaces:**
- Consumes: `construirVentas` (erp-build), `ventasWeb` (erp-web), `ventasML` (erp-ml).
- Produces: ejecutable `node server/erp-ingesta.mjs [--once] [--dry]`.

- [ ] **Step 1: Crear `server/erp-ingesta.mjs`**

```js
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

  const canales = {};
  try { canales.web = await ventasWeb(); } catch (e) { canales.web = null; log("Web falló:", e.message); }
  Object.assign(canales, await ventasML()); // ml1, ml2, ml3

  let totMov = 0, totSalt = 0;
  for (const [canal, ordenes] of Object.entries(canales)) {
    if (!ordenes) continue; // ese canal falló esta corrida
    const cursorTs = cursor[canal] || 0;
    const { movimientos, saltados, maxTs } = construirVentas({ ordenes, canal, codigosConocidos, cursorTs });
    if (saltados.length) { totSalt += saltados.length; log(canal, "saltados (SKU sin mapear):", saltados.length, "→", saltados.slice(0, 5).map((s) => s.sku).join(", ")); }
    if (!movimientos.length) { log(canal, "sin ventas nuevas"); continue; }
    if (DRY) { log(canal, "DRY — mandaría", movimientos.length, "movimientos"); totMov += movimientos.length; continue; }
    const r = await nucleo("POST", "/api/movimientos", movimientos);
    cursor[canal] = maxTs; guardarCursor(cursor); // avanza el cursor solo si el POST fue OK
    totMov += movimientos.length;
    log(canal, "enviado:", JSON.stringify(r), "cursor→", new Date(maxTs).toISOString());
  }
  log("listo. movimientos:", totMov, "saltados:", totSalt);
  process.exit(0);
}
main().catch((e) => { console.error("[erp-ingesta] error fatal:", e.message); process.exit(1); });
```

- [ ] **Step 2: Crear `server/erp_ingesta.cmd`** (lo dispara la tarea de Windows)

```bat
@echo off
REM Ingesta de ventas al núcleo, una pasada (lo dispara la tarea de Windows cada ~10-15 min).
REM Portable: usa su propia ubicación. Requiere ERP_NUCLEO_KEY en el entorno.
cd /d "%~dp0.."
node server\erp-ingesta.mjs --once >> "%~dp0erp_ingesta.log" 2>&1
```

- [ ] **Step 3: Ignorar el estado en `.gitignore`**

Agregar al final de `monitor-ventas/.gitignore`:
```
server/erp-cursor.json
server/erp_ingesta.log
```

- [ ] **Step 4: Verificar en seco (DRY) que el flujo corre**

Requiere los secretos de ML (`secrets/tokens_cuenta*.json`) presentes y `ERP_NUCLEO_KEY`. Si esta máquina NO tiene los tokens de ML, este paso se corre en la PC de bodega (Task 4). Donde estén:
```bash
cd "C:/Users/dell/victtorino/monitor-ventas"
ERP_NUCLEO_KEY=72e8e6f89dacd9333ea1bc7262ea0589bef834b0bfb49643 node server/erp-ingesta.mjs --dry
```
Expected: imprime "códigos conocidos en el núcleo: ~155", y por canal "sin ventas nuevas" o "DRY — mandaría N movimientos". NO postea nada. (Si un canal no tiene credenciales aquí, imprime que falló y sigue — aceptable en --dry.)

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/dell/victtorino"
git add monitor-ventas/server/erp-ingesta.mjs monitor-ventas/server/erp_ingesta.cmd monitor-ventas/.gitignore
git commit -m "feat(erp-ingesta): orquestador + tarea Windows + DRY (Fase 2 task 3)"
```

---

### Task 4: Activación en vivo (cursor inicial + primer push + tarea programada)

**Files:**
- Create: `monitor-ventas/server/erp-cursor.json` (estado local, gitignored)

**Interfaces:**
- Consumes: todo lo anterior. Produce: la ingesta corriendo en vivo en la PC de bodega.

> **Dónde se corre esta tarea:** en la **PC de bodega** (donde están `secrets/tokens_cuenta*.json` de ML y corre el Monitor). Si esta máquina es esa, se corre aquí; si no, Victor la corre allá. Las creds de Woo están hardcodeadas en `web-feed.mjs`, así que Web funciona en cualquier lado; ML necesita los tokens.

- [ ] **Step 1: Sembrar la marca de agua inicial**

Decisión operacional: el cursor inicial debe ser la fecha de la última toma física (las ventas anteriores ya están en el conteo). Recomendado: hacer una toma real y sembrar el cursor en ese momento. Para arrancar conservador (no restar doble), sembrar en "ahora" — solo se cuentan ventas desde la activación:
```bash
cd "C:/Users/dell/victtorino/monitor-ventas"
node -e "const fs=require('node:fs');const t=Date.now();fs.writeFileSync('server/erp-cursor.json',JSON.stringify({web:t,ml1:t,ml2:t,ml3:t},null,2));console.log('cursor sembrado en',new Date(t).toISOString())"
```
Expected: imprime la fecha del cursor. (Para sembrar en una toma específica, reemplazar `Date.now()` por `Date.parse('<ISO de la toma>')`.)

- [ ] **Step 2: Primera corrida real (`--once`)**

```bash
cd "C:/Users/dell/victtorino/monitor-ventas"
ERP_NUCLEO_KEY=72e8e6f89dacd9333ea1bc7262ea0589bef834b0bfb49643 node server/erp-ingesta.mjs --once
```
Expected: por canal "sin ventas nuevas" (si no hubo ventas desde el cursor) o "enviado: {...}" con los movimientos. `saltados` lista los SKU sin mapear. Sin errores fatales.

- [ ] **Step 3: Verificar en el núcleo (si hubo ventas)**

```bash
KEY="72e8e6f89dacd9333ea1bc7262ea0589bef834b0bfb49643"
curl -s -H "x-erp-key: $KEY" "https://erp-nucleo.vercel.app/api/stock" | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{const j=JSON.parse(d);console.log('SKU con stock<0 (sobreventa?):',j.filter(x=>x.stock<0).length,'| total SKU:',j.length)})"
```
Expected: el comando responde; si hubo ventas, el stock de esos SKU bajó. (Un stock negativo indica que el núcleo aún no tenía el saldo de ese SKU — se corrige en la próxima toma.)

- [ ] **Step 4: Verificar idempotencia (segunda corrida sin ventas nuevas)**

Run: `cd "C:/Users/dell/victtorino/monitor-ventas" && ERP_NUCLEO_KEY=72e8e6f89dacd9333ea1bc7262ea0589bef834b0bfb49643 node server/erp-ingesta.mjs --once`
Expected: "sin ventas nuevas" en todos los canales (el cursor ya avanzó). El stock del núcleo NO cambia.

- [ ] **Step 5: Registrar la tarea programada de Windows**

En la PC de bodega, crear una tarea que ejecute `server\erp_ingesta.cmd` cada 15 min, con `ERP_NUCLEO_KEY` en el entorno del sistema. Comando (PowerShell, requiere setear antes la variable de sistema `ERP_NUCLEO_KEY`):
```powershell
$cmd = "C:\Users\dell\victtorino\monitor-ventas\server\erp_ingesta.cmd"
schtasks /Create /TN "TradeErpIngesta" /TR "$cmd" /SC MINUTE /MO 15 /F
```
Expected: "SUCCESS: The scheduled task ... has successfully been created." (Setear `ERP_NUCLEO_KEY` como variable de sistema: `setx ERP_NUCLEO_KEY 72e8...` con permisos de admin, o incluirla dentro del `.cmd`.)

- [ ] **Step 6: Anotar el resultado**

Registrar en el ledger y la memoria que la Fase 2 quedó activa (canales Web+ML, cursor sembrado, tarea cada 15 min).

---

## Self-Review

**Cobertura del spec:**
- `construirVentas` + normalizadores (todas las líneas, cantidad, confirmadas, cursor, SKU desconocido→saltados, maxTs) → Task 1 (9 tests). Fetchers reusando plomería (ML OAuth, Woo) → Task 2. Orquestador (cursor, GET productos→codigosConocidos, POST movimientos idempotente, avance de cursor solo si POST OK, log de saltados) → Task 3. Marca de agua inicial desde la toma, primer push, idempotencia, tarea Windows → Task 4. ✔ Sin huecos.
- Fuera de alcance respetado: Falabella, reversa de cancelaciones, `canal_map`, propagación a canales — ninguno se implementa. ✔
- Núcleo no modificado: confirmado (solo se le hacen GET/POST). ✔

**Placeholders:** los valores "~155" / "N" en salidas esperadas son números reales dependientes del estado en vivo, no placeholders de lógica; cada paso de código está completo. ✔

**Consistencia de tipos:** `Orden` ({orderId,fecha,confirmada,lineas:{sku,qty}}) producida por normalizarWeb/normalizarML y consumida por construirVentas; movimiento `{codigo,tipo:"venta",cantidad,canal,ref}`; `ventasML()` devuelve `{ml1,ml2,ml3}`, `ventasWeb()` devuelve `Orden[]`; `canal ∈ {web,ml1,ml2,ml3}` — consistente entre Task 1/2/3. ✔

**Nota de seguridad:** el filtro `codigosConocidos` evita que un SKU sin mapear aborte el lote (el núcleo lanza 400 al primer código desconocido). El cursor avanza solo tras un POST OK, así un fallo de red se reintenta sin perder ventas (idempotencia cubre el solape).
