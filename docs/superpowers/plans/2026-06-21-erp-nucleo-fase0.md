# ERP Núcleo — Fase 0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el núcleo de datos del ERP propio: una base Postgres con productos + libro de movimientos, y una API que devuelve el stock vivo (calculado del libro), con carga del maestro y movimientos idempotentes.

**Architecture:** Proyecto nuevo `erp-nucleo/` con funciones serverless de Vercel (`api/*.js`, ESM, JS plano sin build). La lógica vive en módulos puros y testeables en `lib/`; los handlers de `api/` son envoltorios delgados que validan auth y delegan. El stock NO se guarda como número: se calcula con `SUM(cantidad) GROUP BY codigo` sobre la tabla `movimientos`.

**Tech Stack:** Node 20+ (ESM), `@neondatabase/serverless` (Pool, API compatible con `pg`), Postgres (Neon), `node:test`. Sin TypeScript, sin paso de build, sin frameworks de test.

## Global Constraints

- Lenguaje del código y mensajes: español neutro.
- JS plano ESM (`.js` con `export`/`import`), nunca TypeScript. Imports relativos con extensión `.js`.
- Driver único: `@neondatabase/serverless` (`Pool`). String de conexión en `ERP_DB_URL`.
- Auth: header `x-erp-key` debe igualar `process.env.ERP_KEY`. Sin login de usuarios.
- El núcleo NO escribe stock hacia los canales en ninguna tarea de esta fase.
- Idempotencia: ventas/compras se insertan con `ON CONFLICT (canal, ref, codigo) DO NOTHING`. Movimientos sin `ref` (saldo_inicial/ajuste manual) siempre se insertan.
- Las pruebas corren contra una base de prueba real apuntada por `ERP_DB_URL` (una base Neon free desechable). Cada test resetea el esquema.

---

### Task 1: Scaffold del proyecto, conexión a DB, esquema y auth

**Files:**
- Create: `erp-nucleo/package.json`
- Create: `erp-nucleo/.gitignore`
- Create: `erp-nucleo/lib/db.js`
- Create: `erp-nucleo/lib/schema.sql`
- Create: `erp-nucleo/lib/auth.js`
- Create: `erp-nucleo/lib/test-helpers.js`
- Create: `erp-nucleo/scripts/init-db.mjs`
- Test: `erp-nucleo/lib/auth.test.js`
- Test: `erp-nucleo/lib/db.test.js`

**Interfaces:**
- Produces: `query(text, params) -> Promise<{ rows, rowCount }>` (lib/db.js)
- Produces: `checkKey(req) -> boolean` (lib/auth.js)
- Produces: `resetDb() -> Promise<void>` (lib/test-helpers.js)

- [ ] **Step 1: Crear `erp-nucleo/package.json`**

```json
{
  "name": "erp-nucleo",
  "version": "0.0.1",
  "type": "module",
  "private": true,
  "scripts": {
    "db:init": "node scripts/init-db.mjs",
    "test": "node --test"
  },
  "dependencies": {
    "@neondatabase/serverless": "^0.10.0"
  }
}
```

- [ ] **Step 2: Crear `erp-nucleo/.gitignore`**

```
node_modules/
.env
.vercel/
```

- [ ] **Step 3: Crear `erp-nucleo/lib/schema.sql`**

```sql
CREATE TABLE IF NOT EXISTS productos (
  codigo      TEXT PRIMARY KEY,
  descripcion TEXT NOT NULL,
  familia     TEXT,
  costo       INTEGER DEFAULT 0,
  activo      BOOLEAN DEFAULT TRUE,
  actualizado TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS movimientos (
  id       BIGSERIAL PRIMARY KEY,
  codigo   TEXT NOT NULL REFERENCES productos(codigo),
  tipo     TEXT NOT NULL,
  cantidad INTEGER NOT NULL,
  canal    TEXT,
  ref      TEXT,
  fecha    TIMESTAMPTZ DEFAULT now(),
  UNIQUE (canal, ref, codigo)
);

CREATE TABLE IF NOT EXISTS canal_map (
  canal       TEXT NOT NULL,
  sku_externo TEXT NOT NULL,
  codigo      TEXT NOT NULL REFERENCES productos(codigo),
  PRIMARY KEY (canal, sku_externo)
);
```

- [ ] **Step 4: Crear `erp-nucleo/lib/db.js`**

```js
// Conexión única a Postgres (Neon). Pool con API compatible pg.
import { Pool } from '@neondatabase/serverless';

const pool = new Pool({ connectionString: process.env.ERP_DB_URL });

export const query = (text, params) => pool.query(text, params);
```

- [ ] **Step 5: Crear `erp-nucleo/lib/auth.js`**

```js
// Auth mínima por token compartido. ponytail: un solo negocio, no hay multi-usuario.
export function checkKey(req) {
  const key = req.headers['x-erp-key'];
  return !!process.env.ERP_KEY && key === process.env.ERP_KEY;
}
```

- [ ] **Step 6: Crear `erp-nucleo/lib/test-helpers.js`**

```js
// Resetea el esquema en la base de prueba (ERP_DB_URL). pg permite varias
// sentencias en un query simple sin params, así corremos el schema completo.
import { readFileSync } from 'node:fs';
import { query } from './db.js';

const schema = readFileSync(new URL('./schema.sql', import.meta.url), 'utf8');

export async function resetDb() {
  await query('DROP TABLE IF EXISTS movimientos CASCADE; DROP TABLE IF EXISTS canal_map CASCADE; DROP TABLE IF EXISTS productos CASCADE;');
  await query(schema);
}
```

- [ ] **Step 7: Crear `erp-nucleo/scripts/init-db.mjs`**

```js
// Aplica el esquema a ERP_DB_URL. Idempotente (CREATE TABLE IF NOT EXISTS).
import { readFileSync } from 'node:fs';
import { query } from '../lib/db.js';

const schema = readFileSync(new URL('../lib/schema.sql', import.meta.url), 'utf8');
await query(schema);
console.log('esquema aplicado');
process.exit(0);
```

- [ ] **Step 8: Escribir el test de auth `erp-nucleo/lib/auth.test.js`**

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { checkKey } from './auth.js';

test('checkKey acepta la clave correcta y rechaza el resto', () => {
  process.env.ERP_KEY = 'secreto123';
  assert.equal(checkKey({ headers: { 'x-erp-key': 'secreto123' } }), true);
  assert.equal(checkKey({ headers: { 'x-erp-key': 'malo' } }), false);
  assert.equal(checkKey({ headers: {} }), false);
});

test('checkKey rechaza si no hay ERP_KEY configurada', () => {
  delete process.env.ERP_KEY;
  assert.equal(checkKey({ headers: { 'x-erp-key': 'lo-que-sea' } }), false);
});
```

- [ ] **Step 9: Escribir el test de DB `erp-nucleo/lib/db.test.js`**

```js
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';

before(async () => { await resetDb(); });

test('las 3 tablas existen tras resetDb', async () => {
  const { rows } = await query(
    `SELECT table_name FROM information_schema.tables
     WHERE table_schema = 'public' ORDER BY table_name`);
  const nombres = rows.map((r) => r.table_name);
  assert.ok(nombres.includes('productos'));
  assert.ok(nombres.includes('movimientos'));
  assert.ok(nombres.includes('canal_map'));
});
```

- [ ] **Step 10: Instalar deps y correr los tests**

Run: `cd erp-nucleo && npm install && ERP_DB_URL=<url-base-prueba> npm test`
Expected: 3 tests PASS. (Requiere una base Neon de prueba; crear una free y exportar `ERP_DB_URL`.)

- [ ] **Step 11: Commit**

```bash
git add erp-nucleo/package.json erp-nucleo/.gitignore erp-nucleo/lib erp-nucleo/scripts
git commit -m "feat(erp-nucleo): scaffold, conexión DB, esquema y auth (Fase 0 task 1)"
```

---

### Task 2: Stock vivo + GET /api/stock

**Files:**
- Create: `erp-nucleo/lib/stock.js`
- Create: `erp-nucleo/api/stock.js`
- Test: `erp-nucleo/lib/stock.test.js`

**Interfaces:**
- Consumes: `query` (lib/db.js), `resetDb` (lib/test-helpers.js)
- Produces: `stockVivo(query) -> Promise<Array<{codigo, descripcion, costo, stock, valor}>>`
- Produces: `stockDe(query, codigo) -> Promise<number>`

- [ ] **Step 1: Escribir el test `erp-nucleo/lib/stock.test.js`**

```js
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';
import { stockVivo, stockDe } from './stock.js';

beforeEach(async () => {
  await resetDb();
  await query(`INSERT INTO productos (codigo, descripcion, costo) VALUES ('A1','Llave',1000)`);
  await query(`INSERT INTO movimientos (codigo, tipo, cantidad, canal, ref) VALUES
    ('A1','saldo_inicial',100,'inventario','toma-1'),
    ('A1','venta',-5,'ml1','orden-9'),
    ('A1','compra',20,'proveedor','oc-3')`);
});

test('stockDe suma el libro: 100 - 5 + 20 = 115', async () => {
  assert.equal(await stockDe(query, 'A1'), 115);
});

test('stockVivo devuelve stock y valor por SKU', async () => {
  const filas = await stockVivo(query);
  const a1 = filas.find((f) => f.codigo === 'A1');
  assert.equal(a1.stock, 115);
  assert.equal(a1.valor, 115000); // 115 * 1000
});

test('stockVivo incluye productos sin movimientos con stock 0', async () => {
  await query(`INSERT INTO productos (codigo, descripcion, costo) VALUES ('B2','Codo',500)`);
  const filas = await stockVivo(query);
  const b2 = filas.find((f) => f.codigo === 'B2');
  assert.equal(b2.stock, 0);
  assert.equal(b2.valor, 0);
});
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `cd erp-nucleo && ERP_DB_URL=<url> node --test lib/stock.test.js`
Expected: FAIL ("Cannot find module './stock.js'").

- [ ] **Step 3: Crear `erp-nucleo/lib/stock.js`**

```js
// Stock vivo = SUM(cantidad) sobre el libro. LEFT JOIN para incluir productos
// sin movimientos (stock 0).
// ponytail: GROUP BY directo; a cientos de SKU es instantáneo. Cachear solo si crece.
export async function stockVivo(query) {
  const { rows } = await query(
    `SELECT p.codigo, p.descripcion, p.costo,
            COALESCE(SUM(m.cantidad), 0)::int AS stock,
            (COALESCE(SUM(m.cantidad), 0) * p.costo)::int AS valor
     FROM productos p
     LEFT JOIN movimientos m ON m.codigo = p.codigo
     GROUP BY p.codigo, p.descripcion, p.costo
     ORDER BY p.codigo`);
  return rows;
}

export async function stockDe(query, codigo) {
  const { rows } = await query(
    `SELECT COALESCE(SUM(cantidad), 0)::int AS stock FROM movimientos WHERE codigo = $1`,
    [codigo]);
  return rows[0].stock;
}
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `cd erp-nucleo && ERP_DB_URL=<url> node --test lib/stock.test.js`
Expected: 3 tests PASS.

- [ ] **Step 5: Crear el handler `erp-nucleo/api/stock.js`**

```js
import { query } from '../lib/db.js';
import { checkKey } from '../lib/auth.js';
import { stockVivo, stockDe } from '../lib/stock.js';

export default async function handler(req, res) {
  if (!checkKey(req)) return res.status(401).json({ error: 'no autorizado' });
  try {
    if (req.query?.codigo) {
      const stock = await stockDe(query, req.query.codigo);
      return res.status(200).json({ codigo: req.query.codigo, stock });
    }
    return res.status(200).json(await stockVivo(query));
  } catch (e) {
    return res.status(e.status || 500).json({ error: e.message });
  }
}
```

- [ ] **Step 6: Commit**

```bash
git add erp-nucleo/lib/stock.js erp-nucleo/lib/stock.test.js erp-nucleo/api/stock.js
git commit -m "feat(erp-nucleo): stock vivo + GET /api/stock (Fase 0 task 2)"
```

---

### Task 3: Insertar movimientos (idempotente + validación) + POST /api/movimientos

**Files:**
- Create: `erp-nucleo/lib/movimientos.js`
- Create: `erp-nucleo/api/movimientos.js`
- Test: `erp-nucleo/lib/movimientos.test.js`

**Interfaces:**
- Consumes: `query` (lib/db.js), `resetDb` (lib/test-helpers.js), `stockDe` (lib/stock.js)
- Produces: `insertarMovimientos(query, movs) -> Promise<{insertados, duplicados}>`
  donde `movs` es `Array<{codigo, tipo, cantidad, canal?, ref?}>`. Lanza
  `Error` con `.status = 400` si algún `codigo` no existe en `productos`.

- [ ] **Step 1: Escribir el test `erp-nucleo/lib/movimientos.test.js`**

```js
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';
import { insertarMovimientos } from './movimientos.js';
import { stockDe } from './stock.js';

beforeEach(async () => {
  await resetDb();
  await query(`INSERT INTO productos (codigo, descripcion, costo) VALUES ('A1','Llave',1000)`);
});

test('inserta movimientos y el stock refleja la suma', async () => {
  const r = await insertarMovimientos(query, [
    { codigo: 'A1', tipo: 'saldo_inicial', cantidad: 50, canal: 'inventario', ref: 'toma-1' },
    { codigo: 'A1', tipo: 'venta', cantidad: -8, canal: 'ml1', ref: 'orden-1' },
  ]);
  assert.equal(r.insertados, 2);
  assert.equal(await stockDe(query, 'A1'), 42);
});

test('idempotencia: reinsertar misma (canal, ref, codigo) no duplica', async () => {
  const venta = [{ codigo: 'A1', tipo: 'venta', cantidad: -3, canal: 'web', ref: 'pedido-77' }];
  await insertarMovimientos(query, venta);
  const r2 = await insertarMovimientos(query, venta);
  assert.equal(r2.insertados, 0);
  assert.equal(r2.duplicados, 1);
  assert.equal(await stockDe(query, 'A1'), -3); // no -6
});

test('codigo inexistente lanza error 400', async () => {
  await assert.rejects(
    () => insertarMovimientos(query, [{ codigo: 'NOPE', tipo: 'ajuste', cantidad: 1 }]),
    (e) => { assert.equal(e.status, 400); return true; });
});
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `cd erp-nucleo && ERP_DB_URL=<url> node --test lib/movimientos.test.js`
Expected: FAIL ("Cannot find module './movimientos.js'").

- [ ] **Step 3: Crear `erp-nucleo/lib/movimientos.js`**

```js
// Inserta movimientos al libro. Valida que el producto exista (no crear
// fantasmas desde el libro). Idempotente por (canal, ref, codigo).
export async function insertarMovimientos(query, movs) {
  const res = { insertados: 0, duplicados: 0 };
  for (const m of movs) {
    const existe = await query('SELECT 1 FROM productos WHERE codigo = $1', [m.codigo]);
    if (existe.rows.length === 0) {
      const e = new Error(`codigo desconocido: ${m.codigo}`);
      e.status = 400;
      throw e;
    }
    const r = await query(
      `INSERT INTO movimientos (codigo, tipo, cantidad, canal, ref)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (canal, ref, codigo) DO NOTHING`,
      [m.codigo, m.tipo, m.cantidad, m.canal ?? null, m.ref ?? null]);
    if (r.rowCount === 1) res.insertados++;
    else res.duplicados++;
  }
  return res;
}
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `cd erp-nucleo && ERP_DB_URL=<url> node --test lib/movimientos.test.js`
Expected: 3 tests PASS.

- [ ] **Step 5: Crear el handler `erp-nucleo/api/movimientos.js`**

```js
import { query } from '../lib/db.js';
import { checkKey } from '../lib/auth.js';
import { insertarMovimientos } from '../lib/movimientos.js';

export default async function handler(req, res) {
  if (!checkKey(req)) return res.status(401).json({ error: 'no autorizado' });
  if (req.method !== 'POST') return res.status(405).json({ error: 'método no permitido' });
  try {
    const movs = Array.isArray(req.body) ? req.body : [req.body];
    return res.status(200).json(await insertarMovimientos(query, movs));
  } catch (e) {
    return res.status(e.status || 500).json({ error: e.message });
  }
}
```

- [ ] **Step 6: Commit**

```bash
git add erp-nucleo/lib/movimientos.js erp-nucleo/lib/movimientos.test.js erp-nucleo/api/movimientos.js
git commit -m "feat(erp-nucleo): movimientos idempotentes + POST /api/movimientos (Fase 0 task 3)"
```

---

### Task 4: Maestro de productos — listar + importar (GET/POST /api/productos)

**Files:**
- Create: `erp-nucleo/lib/productos.js`
- Create: `erp-nucleo/api/productos.js`
- Test: `erp-nucleo/lib/productos.test.js`

**Interfaces:**
- Consumes: `query` (lib/db.js), `resetDb` (lib/test-helpers.js)
- Produces: `listarProductos(query) -> Promise<Array<{codigo, descripcion, familia, costo, activo}>>`
- Produces: `importarProductos(query, filas) -> Promise<{importadas, saltadas}>`
  donde `filas` es `Array<{codigo, descripcion, familia?, costo?}>` (upsert por `codigo`).

- [ ] **Step 1: Escribir el test `erp-nucleo/lib/productos.test.js`**

```js
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';
import { listarProductos, importarProductos } from './productos.js';

beforeEach(async () => { await resetDb(); });

test('importar inserta filas válidas y salta las incompletas', async () => {
  const r = await importarProductos(query, [
    { codigo: 'A1', descripcion: 'Llave', familia: 'Griferías', costo: 1000 },
    { codigo: '', descripcion: 'sin codigo' },          // saltada
    { codigo: 'B2', descripcion: '' },                   // saltada
    { codigo: 'C3', descripcion: 'Codo', costo: 500 },
  ]);
  assert.equal(r.importadas, 2);
  assert.equal(r.saltadas, 2);
  const lista = await listarProductos(query);
  assert.equal(lista.length, 2);
});

test('importar hace upsert: re-importar el mismo codigo actualiza, no duplica', async () => {
  await importarProductos(query, [{ codigo: 'A1', descripcion: 'Llave', costo: 1000 }]);
  await importarProductos(query, [{ codigo: 'A1', descripcion: 'Llave Cromada', costo: 1200 }]);
  const lista = await listarProductos(query);
  assert.equal(lista.length, 1);
  assert.equal(lista[0].descripcion, 'Llave Cromada');
  assert.equal(lista[0].costo, 1200);
});
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `cd erp-nucleo && ERP_DB_URL=<url> node --test lib/productos.test.js`
Expected: FAIL ("Cannot find module './productos.js'").

- [ ] **Step 3: Crear `erp-nucleo/lib/productos.js`**

```js
export async function listarProductos(query) {
  const { rows } = await query(
    `SELECT codigo, descripcion, familia, costo, activo FROM productos ORDER BY codigo`);
  return rows;
}

// Upsert del maestro desde filas ya parseadas (el Excel lo parsea el llamador).
// Salta filas sin codigo o sin descripcion.
export async function importarProductos(query, filas) {
  let importadas = 0, saltadas = 0;
  for (const f of filas) {
    if (!f.codigo || !f.descripcion) { saltadas++; continue; }
    await query(
      `INSERT INTO productos (codigo, descripcion, familia, costo, actualizado)
       VALUES ($1, $2, $3, $4, now())
       ON CONFLICT (codigo) DO UPDATE SET
         descripcion = EXCLUDED.descripcion,
         familia = EXCLUDED.familia,
         costo = EXCLUDED.costo,
         actualizado = now()`,
      [f.codigo, f.descripcion, f.familia ?? null, Math.round(f.costo ?? 0)]);
    importadas++;
  }
  return { importadas, saltadas };
}
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `cd erp-nucleo && ERP_DB_URL=<url> node --test lib/productos.test.js`
Expected: 2 tests PASS.

- [ ] **Step 5: Crear el handler `erp-nucleo/api/productos.js`** (GET lista, POST importa — un solo archivo)

```js
import { query } from '../lib/db.js';
import { checkKey } from '../lib/auth.js';
import { listarProductos, importarProductos } from '../lib/productos.js';

export default async function handler(req, res) {
  if (!checkKey(req)) return res.status(401).json({ error: 'no autorizado' });
  try {
    if (req.method === 'GET') {
      return res.status(200).json(await listarProductos(query));
    }
    if (req.method === 'POST') {
      const filas = Array.isArray(req.body) ? req.body : (req.body?.filas ?? []);
      return res.status(200).json(await importarProductos(query, filas));
    }
    return res.status(405).json({ error: 'método no permitido' });
  } catch (e) {
    return res.status(e.status || 500).json({ error: e.message });
  }
}
```

- [ ] **Step 6: Correr toda la suite**

Run: `cd erp-nucleo && ERP_DB_URL=<url> npm test`
Expected: todos los tests de las 4 tareas PASS.

- [ ] **Step 7: Commit**

```bash
git add erp-nucleo/lib/productos.js erp-nucleo/lib/productos.test.js erp-nucleo/api/productos.js
git commit -m "feat(erp-nucleo): maestro de productos listar + importar (Fase 0 task 4)"
```

---

### Task 5: Deploy a Vercel + base Neon de producción

**Files:**
- Create: `erp-nucleo/vercel.json`
- Create: `erp-nucleo/README.md`

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: API en vivo en `https://<proyecto>.vercel.app/api/{stock,movimientos,productos}`.

- [ ] **Step 1: Crear `erp-nucleo/vercel.json`** (mínimo; funciones Node por defecto)

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json"
}
```

- [ ] **Step 2: Crear `erp-nucleo/README.md`**

```markdown
# erp-nucleo

Núcleo de datos del ERP propio (Fase 0): catálogo + libro de movimientos + stock vivo.

## Variables de entorno
- `ERP_DB_URL` — string de conexión Postgres (Neon).
- `ERP_KEY` — token compartido; va en el header `x-erp-key` de cada request.

## Endpoints (requieren header `x-erp-key`)
- `GET /api/stock` — stock vivo por SKU. `?codigo=X` para uno solo.
- `GET /api/productos` — maestro.
- `POST /api/productos` — importar/actualizar maestro (array de filas o `{filas:[...]}`).
- `POST /api/movimientos` — insertar movimiento(s) (idempotente por canal+ref+codigo).

## Local
`npm install`; exportar `ERP_DB_URL` y `ERP_KEY`; `npm run db:init`; `npm test`.
```

- [ ] **Step 3: Provisionar Neon de producción + variables**

Run (manual, requiere cuenta Vercel/Neon de Victor):
```bash
cd erp-nucleo
# crear base Neon (Vercel Marketplace) y enlazarla al proyecto, luego:
vercel link
vercel env add ERP_DB_URL production   # connection string Neon prod
vercel env add ERP_KEY production       # token elegido
```
Expected: variables creadas en el proyecto Vercel.

- [ ] **Step 4: Inicializar el esquema en la base de producción**

Run: `cd erp-nucleo && ERP_DB_URL=<url-neon-prod> npm run db:init`
Expected: "esquema aplicado".

- [ ] **Step 5: Deploy**

Run: `cd erp-nucleo && vercel deploy --prod --yes`
Expected: URL de producción impresa.

- [ ] **Step 6: Smoke test en vivo**

Run:
```bash
curl -s -H "x-erp-key: <token>" https://<proyecto>.vercel.app/api/productos
# esperado: [] (vacío, aún sin import)
curl -s -X POST -H "x-erp-key: <token>" -H "content-type: application/json" \
  -d '[{"codigo":"A1","descripcion":"Llave","costo":1000}]' \
  https://<proyecto>.vercel.app/api/productos
# esperado: {"importadas":1,"saltadas":0}
curl -s -H "x-erp-key: <token>" "https://<proyecto>.vercel.app/api/stock?codigo=A1"
# esperado: {"codigo":"A1","stock":0}
```
Expected: las 3 respuestas como se indica.

- [ ] **Step 7: Commit**

```bash
git add erp-nucleo/vercel.json erp-nucleo/README.md
git commit -m "chore(erp-nucleo): config Vercel + README + deploy (Fase 0 task 5)"
```

---

## Self-Review

**Cobertura del spec:**
- DB 3 tablas → Task 1. API stock vivo → Task 2. Insertar movimiento idempotente → Task 3. Maestro listar + importar → Task 4. Deploy/infra (Neon, Vercel, auth token) → Tasks 1 y 5. Pruebas (suma, idempotencia, 400) → Tasks 2 y 3. ✔ Sin huecos.
- Fuera de alcance respetado: no hay UI, ni ingesta de canales, ni escritura a la toma, ni stock hacia canales. ✔

**Placeholders:** los `<url>` / `<token>` / `<proyecto>` son valores que solo Victor posee (credenciales/cuenta), no placeholders de lógica; cada paso muestra el código/comando completo. ✔

**Consistencia de tipos:** `query(text, params)`, `stockDe(query, codigo)`, `stockVivo(query)`, `insertarMovimientos(query, movs)`, `listarProductos(query)`, `importarProductos(query, filas)` usados igual en tests, libs y handlers. ✔

**Nota de idempotencia:** el `UNIQUE (canal, ref, codigo)` solo deduplica cuando `canal` y `ref` no son NULL — correcto: ventas/compras los traen; saldo_inicial/ajuste manual sin `ref` se insertan siempre (intencional).
