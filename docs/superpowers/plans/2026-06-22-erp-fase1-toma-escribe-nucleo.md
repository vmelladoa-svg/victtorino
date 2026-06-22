# ERP Fase 1 — La toma física escribe al núcleo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que Inventario On Line, al cerrar una toma, suba el catálogo al núcleo y cuadre el stock de cada SKU contado a lo contado (toma manda), con un botón de reenvío.

**Architecture:** Todo el código nuevo vive en la app **Inventario On Line** (`C:\Users\dell\Downloads\design_handoff_inventario\app`). Una función pura `construirEnvio` arma el payload (productos a upsert + movimientos de ajuste). Un endpoint serverless `api/nucleo.ts` lee KV, consulta el stock actual del núcleo, llama `construirEnvio`, y hace POST al núcleo (productos + movimientos). El frontend dispara el envío al cerrar la toma y ofrece "Reenviar al ERP".

**Tech Stack:** TypeScript ESM, funciones serverless Vercel (`api/*.ts`), React (Vite), Upstash KV (`@upstash/redis`), `node:test` con `tsx`. El núcleo (Fase 0) NO se modifica.

## Global Constraints

- **Directorio de trabajo:** `C:\Users\dell\Downloads\design_handoff_inventario\app` (NO el repo victtorino).
- TypeScript ESM. **Imports en runtime usan `.js`** (`from "./_lib.js"`), **imports en tests usan `.ts`** (`from "./model.ts"`) — convención existente del repo. No cambiarla.
- Test runner: `node --import tsx --test` (script `npm test`). Tests son `*.test.ts`.
- Núcleo vía env: `ERP_NUCLEO_URL` (= `https://erp-nucleo.vercel.app`) y `ERP_NUCLEO_KEY`. Header en cada llamada: `x-erp-key: <ERP_NUCLEO_KEY>`.
- Movimiento al núcleo: `{ codigo, tipo: "ajuste", cantidad: diff, canal: "inventario", ref: "toma-" + tomaId }`. `diff = contado − stockActual[codigo]`. Solo si `diff !== 0`.
- `contado = bodega (conteos) + exhibición` por SKU.
- Catálogo: **upsert completo** de articulos (no ocultos) + hallazgos válidos. Movimientos: **solo SKU contados** + hallazgos válidos.
- Excluir: hallazgos con `tipo === "duplicado"` y cualquier `codigo` con `ediciones[codigo].oculto === true`.
- Helpers KV existentes en `api/_lib.ts`: `kvGet<T>(key, fallback)`, `K` (`K.articulos`, `K.conteos`, `K.exhibicion`, `K.hallazgos`, `K.ediciones`), `json(res, status, body)`.
- El cierre local (`tomaCerrada` en meta) y el push al ERP son **independientes**: si el push falla, la toma queda cerrada igual.
- NO se modifica el servidor Express local (`server/index.ts`); Victor usa la versión Vercel. (El botón en dev local daría 404, aceptado.)

---

### Task 1: Función pura `construirEnvio` + tests

**Files:**
- Create: `api/_nucleo.ts`
- Test: `api/_nucleo.test.ts`

**Interfaces:**
- Produces:
  ```ts
  interface ProductoOut { codigo: string; descripcion: string; costo: number }
  interface MovimientoOut { codigo: string; tipo: "ajuste"; cantidad: number; canal: "inventario"; ref: string }
  function construirEnvio(input: {
    articulos: { codigo: string; descripcion: string; costoVigente: number }[];
    conteos: Record<string, { qty: number; ts: number }>;
    exhibicion: Record<string, { qty: number; ts: number }>;
    hallazgos: { codigo: string; descripcion: string; cantidad: number; tipo: string }[];
    ediciones: Record<string, { oculto: boolean }>;
    stockActual: Record<string, number>;
    tomaId: string;
  }): { productos: ProductoOut[]; movimientos: MovimientoOut[]; sinCambio: number }
  ```

- [ ] **Step 1: Escribir el test `api/_nucleo.test.ts`**

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { construirEnvio } from "./_nucleo.ts";

const art = (codigo: string, descripcion = codigo, costoVigente = 1000) => ({ codigo, descripcion, costoVigente });

test("primera toma: ajuste = contado (stock núcleo vacío)", () => {
  const out = construirEnvio({
    articulos: [art("A1")], conteos: { A1: { qty: 5, ts: 1 } }, exhibicion: {},
    hallazgos: [], ediciones: {}, stockActual: {}, tomaId: "2026-06-22T00:00:00Z",
  });
  assert.deepEqual(out.productos, [{ codigo: "A1", descripcion: "A1", costo: 1000 }]);
  assert.deepEqual(out.movimientos, [{ codigo: "A1", tipo: "ajuste", cantidad: 5, canal: "inventario", ref: "toma-2026-06-22T00:00:00Z" }]);
  assert.equal(out.sinCambio, 0);
});

test("contado = bodega + exhibición", () => {
  const out = construirEnvio({
    articulos: [art("A1")], conteos: { A1: { qty: 4, ts: 1 } }, exhibicion: { A1: { qty: 3, ts: 1 } },
    hallazgos: [], ediciones: {}, stockActual: {}, tomaId: "t",
  });
  assert.equal(out.movimientos[0].cantidad, 7);
});

test("re-toma: cuadra al contado y cuenta sinCambio", () => {
  const out = construirEnvio({
    articulos: [art("A1"), art("A2")],
    conteos: { A1: { qty: 10, ts: 1 }, A2: { qty: 4, ts: 1 } }, exhibicion: {},
    hallazgos: [], ediciones: {}, stockActual: { A1: 3, A2: 4 }, tomaId: "t",
  });
  const m = out.movimientos.find((x) => x.codigo === "A1")!;
  assert.equal(m.cantidad, 7); // 10 - 3
  assert.equal(out.movimientos.find((x) => x.codigo === "A2"), undefined); // 4 - 4 = 0
  assert.equal(out.sinCambio, 1);
});

test("hallazgo nuevo: producto costo 0 + su ajuste", () => {
  const out = construirEnvio({
    articulos: [], conteos: {}, exhibicion: {},
    hallazgos: [{ codigo: "TIENDA-x", descripcion: "Lámpara", cantidad: 2, tipo: "solo_tienda" }],
    ediciones: {}, stockActual: {}, tomaId: "t",
  });
  assert.deepEqual(out.productos, [{ codigo: "TIENDA-x", descripcion: "Lámpara", costo: 0 }]);
  assert.equal(out.movimientos[0].cantidad, 2);
});

test("excluye duplicados y ocultos", () => {
  const out = construirEnvio({
    articulos: [art("A1"), art("B2")],
    conteos: { A1: { qty: 5, ts: 1 }, B2: { qty: 9, ts: 1 } }, exhibicion: {},
    hallazgos: [{ codigo: "DUP-1", descripcion: "dup", cantidad: 1, tipo: "duplicado" }],
    ediciones: { B2: { oculto: true } }, stockActual: {}, tomaId: "t",
  });
  const cods = out.productos.map((p) => p.codigo);
  assert.deepEqual(cods, ["A1"]); // B2 oculto fuera, DUP-1 duplicado fuera
  assert.deepEqual(out.movimientos.map((m) => m.codigo), ["A1"]);
});

test("catálogo se sube completo aunque no esté contado, pero sin movimiento", () => {
  const out = construirEnvio({
    articulos: [art("A1"), art("Z9")], // Z9 no contado
    conteos: { A1: { qty: 5, ts: 1 } }, exhibicion: {},
    hallazgos: [], ediciones: {}, stockActual: {}, tomaId: "t",
  });
  assert.deepEqual(out.productos.map((p) => p.codigo).sort(), ["A1", "Z9"]); // catálogo completo
  assert.deepEqual(out.movimientos.map((m) => m.codigo), ["A1"]); // solo el contado
});
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `cd "C:/Users/dell/Downloads/design_handoff_inventario/app" && node --import tsx --test api/_nucleo.test.ts`
Expected: FAIL (`Cannot find module './_nucleo.ts'`).

- [ ] **Step 3: Crear `api/_nucleo.ts`**

```ts
// _nucleo.ts — Lógica pura para armar el envío de la toma al núcleo del ERP.
// Sin I/O: recibe todo por parámetro y devuelve qué productos upsertear y qué
// movimientos de ajuste escribir. La toma MANDA: ajuste = contado − stockActual.

export interface ProductoOut { codigo: string; descripcion: string; costo: number }
export interface MovimientoOut { codigo: string; tipo: "ajuste"; cantidad: number; canal: "inventario"; ref: string }

interface ArticuloLite { codigo: string; descripcion: string; costoVigente: number }
interface Conteo { qty: number; ts: number }
interface HallazgoLite { codigo: string; descripcion: string; cantidad: number; tipo: string }

export function construirEnvio(input: {
  articulos: ArticuloLite[];
  conteos: Record<string, Conteo>;
  exhibicion: Record<string, Conteo>;
  hallazgos: HallazgoLite[];
  ediciones: Record<string, { oculto: boolean }>;
  stockActual: Record<string, number>;
  tomaId: string;
}): { productos: ProductoOut[]; movimientos: MovimientoOut[]; sinCambio: number } {
  const { articulos, conteos, exhibicion, hallazgos, ediciones, stockActual, tomaId } = input;
  const ref = "toma-" + tomaId;
  const oculto = (c: string) => !!ediciones[c]?.oculto;
  const contadoCat = (c: string) => (conteos[c]?.qty || 0) + (exhibicion[c]?.qty || 0);
  const fueContado = (c: string) => conteos[c] != null || exhibicion[c] != null;

  const productos: ProductoOut[] = [];
  const movimientos: MovimientoOut[] = [];
  let sinCambio = 0;

  const ajuste = (codigo: string, contado: number) => {
    const diff = contado - (stockActual[codigo] ?? 0);
    if (diff !== 0) movimientos.push({ codigo, tipo: "ajuste", cantidad: diff, canal: "inventario", ref });
    else sinCambio++;
  };

  // Catálogo completo (no ocultos) → upsert. Movimiento solo si fue contado.
  for (const a of articulos) {
    if (oculto(a.codigo)) continue;
    productos.push({ codigo: a.codigo, descripcion: a.descripcion, costo: Math.round(a.costoVigente || 0) });
    if (fueContado(a.codigo)) ajuste(a.codigo, contadoCat(a.codigo));
  }

  // Hallazgos válidos (nuevos productos): upsert costo 0 + su ajuste.
  for (const h of hallazgos) {
    if (!h.codigo || h.tipo === "duplicado" || oculto(h.codigo)) continue;
    productos.push({ codigo: h.codigo, descripcion: h.descripcion || h.codigo, costo: 0 });
    ajuste(h.codigo, h.cantidad || 0);
  }

  return { productos, movimientos, sinCambio };
}
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `cd "C:/Users/dell/Downloads/design_handoff_inventario/app" && node --import tsx --test api/_nucleo.test.ts`
Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/dell/Downloads/design_handoff_inventario/app"
git add api/_nucleo.ts api/_nucleo.test.ts
git commit -m "feat(nucleo): construirEnvio — arma productos + ajustes de la toma (Fase 1 task 1)"
```

---

### Task 2: Endpoint orquestador `api/nucleo.ts` + cliente `pushNucleo`

**Files:**
- Create: `api/nucleo.ts`
- Modify: `src/api.ts` (agregar export `pushNucleo`)

**Interfaces:**
- Consumes: `construirEnvio` (de `api/_nucleo.js`), `kvGet`/`K`/`json` (de `api/_lib.js`).
- Produces: `pushNucleo(tomaId: string): Promise<any>` en `src/api.ts` (POST a `/api/nucleo`).
- Endpoint `POST /api/nucleo` body `{ tomaId }` → responde `{ productos, ajustes, sinCambio, insertados?, duplicados?, errores: string[] }`.

- [ ] **Step 1: Crear `api/nucleo.ts`**

```ts
// nucleo.ts — Al cerrar la toma: sube catálogo al núcleo y cuadra el stock.
import { kvGet, K, json } from "./_lib.js";
import { construirEnvio } from "./_nucleo.js";

const NUCLEO_URL = process.env.ERP_NUCLEO_URL || "";
const NUCLEO_KEY = process.env.ERP_NUCLEO_KEY || "";

export default async function handler(req: any, res: any) {
  if (req.method !== "POST") return json(res, 405, { error: "Method not allowed" });
  if (!NUCLEO_URL || !NUCLEO_KEY) return json(res, 500, { error: "Falta ERP_NUCLEO_URL/ERP_NUCLEO_KEY" });

  let body: any = {};
  try { body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {}); } catch {}
  const tomaId = String(body.tomaId || "").trim();
  if (!tomaId) return json(res, 400, { error: "Falta tomaId" });

  const [articulos, conteos, exhibicion, hallazgos, ediciones] = await Promise.all([
    kvGet<any[]>(K.articulos, []), kvGet<any>(K.conteos, {}), kvGet<any>(K.exhibicion, {}),
    kvGet<any[]>(K.hallazgos, []), kvGet<any>(K.ediciones, {}),
  ]);

  const headers = { "x-erp-key": NUCLEO_KEY, "content-type": "application/json" };
  const errores: string[] = [];

  // 1. Stock actual del núcleo.
  const stockActual: Record<string, number> = {};
  try {
    const r = await fetch(`${NUCLEO_URL}/api/stock`, { headers: { "x-erp-key": NUCLEO_KEY } });
    if (!r.ok) throw new Error("stock HTTP " + r.status);
    const filas = (await r.json()) as any[];
    for (const f of filas) stockActual[f.codigo] = f.stock;
  } catch (e: any) {
    return json(res, 502, { error: "No se pudo leer el núcleo: " + (e?.message || e) });
  }

  // 2. Armar el envío.
  const { productos, movimientos, sinCambio } = construirEnvio({ articulos, conteos, exhibicion, hallazgos, ediciones, stockActual, tomaId });

  // 3. Upsert catálogo (primero, para que los movimientos no fallen por SKU inexistente).
  try {
    const r = await fetch(`${NUCLEO_URL}/api/productos`, { method: "POST", headers, body: JSON.stringify(productos) });
    if (!r.ok) errores.push("productos HTTP " + r.status);
  } catch (e: any) { errores.push("productos: " + (e?.message || e)); }

  // 4. Movimientos de ajuste.
  let mov: any = {};
  try {
    const r = await fetch(`${NUCLEO_URL}/api/movimientos`, { method: "POST", headers, body: JSON.stringify(movimientos) });
    mov = await r.json().catch(() => ({}));
    if (!r.ok) errores.push("movimientos HTTP " + r.status);
  } catch (e: any) { errores.push("movimientos: " + (e?.message || e)); }

  return json(res, errores.length ? 207 : 200, {
    productos: productos.length, ajustes: movimientos.length, sinCambio,
    insertados: mov.insertados, duplicados: mov.duplicados, errores,
  });
}
```

- [ ] **Step 2: Verificar que el módulo carga sin errores (sintaxis/imports)**

Run: `cd "C:/Users/dell/Downloads/design_handoff_inventario/app" && node --import tsx -e "import('./api/nucleo.ts').then(()=>console.log('ok'))"`
Expected: imprime `ok` (sin throw). (No ejecuta el handler; solo valida import/parse.)

- [ ] **Step 3: Agregar `pushNucleo` a `src/api.ts`**

Al final de `src/api.ts`, agregar:

```ts
export async function pushNucleo(tomaId: string): Promise<any> {
  const r = await fetch("/api/nucleo", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tomaId }),
  });
  return r.json();
}
```

- [ ] **Step 4: Confirmar que el suite existente sigue verde**

Run: `cd "C:/Users/dell/Downloads/design_handoff_inventario/app" && npm test`
Expected: PASS (incluye los 6 tests de `_nucleo.test.ts` de la Task 1 + los existentes de `model.test.ts`/`db.test.ts`).

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/dell/Downloads/design_handoff_inventario/app"
git add api/nucleo.ts src/api.ts
git commit -m "feat(nucleo): endpoint /api/nucleo + cliente pushNucleo (Fase 1 task 2)"
```

---

### Task 3: Gancho en el cierre de toma (frontend)

**Files:**
- Modify: `src/App.tsx` (import `pushNucleo`; estado `envioNucleo`; `onCerrarToma`; `onReenviarNucleo`; props a `<ConteoView>`)
- Modify: `src/conteo.tsx` (props `envioNucleo`/`onReenviarNucleo`; resumen + botón "Reenviar al ERP" en el modal de cierre)

**Interfaces:**
- Consumes: `pushNucleo` (de `./api`).
- `ConteoView` gana props opcionales `envioNucleo?: any` y `onReenviarNucleo?: () => void`.

- [ ] **Step 1: `src/App.tsx` — importar `pushNucleo`**

En el bloque `import { ... } from "./api"` (líneas 4-11), agregar `pushNucleo` a la lista de imports (junto a `setMetaRemote`).

- [ ] **Step 2: `src/App.tsx` — estado del envío**

Después de la línea `const [exhibicion, setExhibicion] = useState<...>({});` (línea 37), agregar:

```tsx
  const [envioNucleo, setEnvioNucleo] = useState<any>(null);
```

- [ ] **Step 3: `src/App.tsx` — disparar el push en el cierre**

Reemplazar la función `onCerrarToma` (líneas 153-157) por:

```tsx
  async function onCerrarToma() {
    const f = new Date().toISOString();
    setMeta((m) => ({ ...m, tomaCerrada: f }));
    await setMetaRemote("tomaCerrada", f);
    try { setEnvioNucleo(await pushNucleo(f)); }
    catch (e: any) { setEnvioNucleo({ errores: [String(e?.message || e)] }); }
  }

  async function onReenviarNucleo() {
    if (!meta.tomaCerrada) return;
    try { setEnvioNucleo(await pushNucleo(meta.tomaCerrada)); }
    catch (e: any) { setEnvioNucleo({ errores: [String(e?.message || e)] }); }
  }
```

- [ ] **Step 4: `src/App.tsx` — pasar props a `<ConteoView>`**

En el `<ConteoView ... />` (a partir de la línea 198), junto a `onCerrarToma={onCerrarToma}` (línea 217), agregar:

```tsx
            envioNucleo={envioNucleo}
            onReenviarNucleo={onReenviarNucleo}
```

- [ ] **Step 5: `src/conteo.tsx` — declarar las props nuevas**

En la firma de `ConteoView` (líneas 173-182), agregar `envioNucleo` y `onReenviarNucleo` a la destructuración (junto a `meta, onCerrarToma`) y a su tipo. El tipo (cerca de la línea 182, donde dice `meta?: any; onCerrarToma?: () => void;`) queda:

```tsx
  meta?: any; onCerrarToma?: () => void; envioNucleo?: any; onReenviarNucleo?: () => void;
```

Y la destructuración (línea 173-174) incluye `... meta, onCerrarToma, envioNucleo, onReenviarNucleo }`.

- [ ] **Step 6: `src/conteo.tsx` — mostrar resumen + botón Reenviar**

Justo después del bloque del cierre marcado (líneas 305-307, el `<p className="cierre-ok">Toma cerrada — ...</p>`), agregar:

```tsx
            {envioNucleo && (
              <div className="cierre-erp" style={{ marginTop: 8 }}>
                {envioNucleo.errores?.length ? (
                  <p className="cierre-ok" style={{ color: "#b00020" }}>
                    No se pudo enviar al ERP: {envioNucleo.errores.join(", ")}
                  </p>
                ) : (
                  <p className="cierre-ok">
                    Enviado al ERP — {envioNucleo.productos} productos, {envioNucleo.ajustes} ajustes, {envioNucleo.sinCambio} sin cambio.
                  </p>
                )}
                <button className="conteo-reset" onClick={() => onReenviarNucleo?.()}>Reenviar al ERP</button>
              </div>
            )}
```

- [ ] **Step 7: Verificar que compila (build de Vite)**

Run: `cd "C:/Users/dell/Downloads/design_handoff_inventario/app" && npm run build`
Expected: build OK, sin errores de TypeScript.

- [ ] **Step 8: Commit**

```bash
cd "C:/Users/dell/Downloads/design_handoff_inventario/app"
git add src/App.tsx src/conteo.tsx
git commit -m "feat(nucleo): cerrar toma envía al ERP + botón Reenviar (Fase 1 task 3)"
```

---

### Task 4: Variables de entorno + deploy + primer sync real

**Files:**
- (sin archivos nuevos; configuración Vercel + deploy)

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: `/api/nucleo` en vivo en el proyecto `inventario-online` de Vercel; el núcleo poblado con el catálogo real y el stock cuadrado a la última toma.

- [ ] **Step 1: Enlazar el proyecto Vercel (si no lo está)**

Run: `cd "C:/Users/dell/Downloads/design_handoff_inventario/app" && vercel link --yes`
Expected: `Linked …/inventario-online` (o el nombre real del proyecto). Si pide elegir, escoger el proyecto de la app de inventario.

- [ ] **Step 2: Cargar las variables de entorno**

Run (usar la URL y el token del núcleo; el token es el `ERP_KEY` de Fase 0 = `72e8e6f89dacd9333ea1bc7262ea0589bef834b0bfb49643`):
```bash
cd "C:/Users/dell/Downloads/design_handoff_inventario/app"
vercel env add ERP_NUCLEO_URL production --value 'https://erp-nucleo.vercel.app' --yes
vercel env add ERP_NUCLEO_KEY production --value '72e8e6f89dacd9333ea1bc7262ea0589bef834b0bfb49643' --yes
```
Expected: ambas "Added Environment Variable".

- [ ] **Step 3: Deploy a producción**

Run: `cd "C:/Users/dell/Downloads/design_handoff_inventario/app" && vercel deploy --prod --yes`
Expected: imprime la URL de producción, estado READY.

- [ ] **Step 4: Primer sync real + verificación contra el núcleo**

Esto ejecuta la Fase 1 de verdad: sube el catálogo real (KV tiene ~159 artículos) y cuadra el stock a la última toma (KV tiene los conteos). Usar la URL pública del inventario (`https://inventario-online-xi.vercel.app`) y un `tomaId` de prueba estable:
```bash
INV="https://inventario-online-xi.vercel.app"
curl -s -m 60 -X POST -H "content-type: application/json" -d '{"tomaId":"sync-inicial-2026-06-22"}' "$INV/api/nucleo"
```
Expected: JSON tipo `{"productos":159,"ajustes":NNN,"sinCambio":N,"insertados":NNN,"duplicados":0,"errores":[]}`.

Luego verificar que el núcleo quedó poblado (debe haber productos y stock > 0 en algún SKU):
```bash
KEY="72e8e6f89dacd9333ea1bc7262ea0589bef834b0bfb49643"
curl -s -m 30 -H "x-erp-key: $KEY" "https://erp-nucleo.vercel.app/api/productos" | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{const j=JSON.parse(d);console.log('productos en núcleo:',j.length)})"
curl -s -m 30 -H "x-erp-key: $KEY" "https://erp-nucleo.vercel.app/api/stock" | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{const j=JSON.parse(d);const conStock=j.filter(x=>x.stock>0).length;console.log('SKU con stock>0:',conStock,'de',j.length)})"
```
Expected: productos en núcleo ≈ 159; varios SKU con stock > 0.

- [ ] **Step 5: Verificar idempotencia del reenvío (mismo tomaId)**

Run:
```bash
INV="https://inventario-online-xi.vercel.app"
curl -s -m 60 -X POST -H "content-type: application/json" -d '{"tomaId":"sync-inicial-2026-06-22"}' "$INV/api/nucleo"
```
Expected: responde igual pero `"duplicados"` > 0 (los ajustes del mismo `ref` ya existen) y `"insertados":0` — el stock del núcleo NO cambió. Confirmar con el comando de stock del Step 4 (mismos números).

- [ ] **Step 6: Anotar el resultado**

No requiere commit (solo configuración/deploy). Registrar en el ledger y la memoria que la Fase 1 quedó en vivo y el núcleo poblado con el primer sync.

---

## Self-Review

**Cobertura del spec:**
- Variables de entorno → Task 4. Función `construirEnvio` (ajuste = contado − stockActual, contado = bodega+exhibición, hallazgos creados, exclusión duplicado/oculto, upsert catálogo completo + reconciliar contados) → Task 1. Endpoint orquestador (lee KV, GET stock, upsert productos, POST movimientos) → Task 2. Frontend (gancho en cierre + resumen + botón Reenviar) → Task 3. Idempotencia (ref por toma) → cubierta por la lógica de Task 1 y verificada en vivo Task 4 Step 5. Manejo de errores (núcleo caído → 502, errores parciales en `errores[]`, cierre local independiente) → Task 2. Pruebas de `construirEnvio` (5 casos del spec) → Task 1 (6 tests). ✔ Sin huecos.
- Fuera de alcance respetado: no ingesta de canales, no stock vivo en la app, no propagación, no server Express local. ✔

**Placeholders:** los valores `NNN`/`N` en las salidas esperadas de Task 4 son números reales desconocidos hasta correr (dependen del estado de KV), no placeholders de lógica; cada paso de código tiene el código completo. ✔

**Consistencia de tipos:** `construirEnvio` (mismo objeto de entrada y salida en Task 1, Task 2 y tests), `pushNucleo(tomaId)` (Task 2 y Task 3), props `envioNucleo`/`onReenviarNucleo` (Task 3 App.tsx ↔ conteo.tsx), `ref="toma-"+tomaId`, movimiento `{codigo,tipo:"ajuste",cantidad,canal:"inventario",ref}` consistente con la API del núcleo de Fase 0. ✔

**Nota:** el primer sync (Task 4 Step 4) es una acción real sobre datos en vivo (puebla el núcleo con el catálogo y cuadra al último conteo de KV). Es justo el objetivo de la Fase 1, no solo un smoke test.
