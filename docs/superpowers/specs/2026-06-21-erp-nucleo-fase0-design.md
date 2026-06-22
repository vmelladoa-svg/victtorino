# ERP propio — Fase 0: Núcleo de datos (catálogo + stock vivo)

Fecha: 2026-06-21
Estado: diseño aprobado en estructura; pendiente revisión del spec.

## Contexto y meta global

Construir un ERP propio que reemplace a Defontana en casi todo. La facturación
electrónica al SII se delega a un **emisor externo certificado por API** (LibreDTE
/ SimpleAPI / etc.); no se reconstruye el emisor DTE. Todo lo demás (catálogo,
stock, ventas multicanal, compras, reportes) es propio.

**Idea central:** una sola base de datos manda. El stock de cada SKU se calcula
como **saldo inicial (toma física) + compras − ventas de todos los canales**, en
vivo. Inventario On Line *pone* el saldo inicial; los canales *rebajan*; el stock
vivo *vuelve* a Inventario On Line.

**Ancla de verdad (aclaración de Victor):** hoy el sistema más confiable es la
toma física con Inventario On Line — es lo más real posible — y con esa toma se
*actualiza Defontana*. El ERP propio solo cambia el destino: la misma toma pasa a
actualizar el **núcleo propio** en vez de Defontana. La toma física es el
`saldo_inicial` del libro; desde ahí los canales rebajan.

```
  Hoy:     toma física (Inventario On Line) ──actualiza──▶ Defontana
  Mañana:  toma física (Inventario On Line) ──actualiza──▶ núcleo propio ──▶ canales rebajan
```

Roadmap por fases (cada una se especifica e implementa por separado):

- **Fase 0 — Núcleo** ← este documento.
- Fase 1 — Toma física escribe el `saldo_inicial` al núcleo (Inventario On Line).
- Fase 2 — Ingesta de ventas directo de cada canal (rebaja stock).
- Fase 3 — Stock vivo de vuelta a Inventario On Line.
- Fase 4 — Compras / reposición (movimientos de entrada).
- Fase 5 — Reportes / contabilidad.
- Fase 6 — Facturación DTE por emisor externo.
- Fase 7 — **Propagación de stock a los canales** (reemplaza la función central de
  Defontana). Meta = reemplazo total. Pero se hace por **pilotos acotados, canal
  por canal**: para cada canal, probar el push de stock con 1-2 SKU controlados,
  verificar que llega correcto y que NO se dispara el falso "sin stock" (ML
  cancela ventas), y solo entonces escalar ese canal. Nunca encender los 6 de
  golpe. Va al final, después de que el libro esté probado y confiable.

Decisión de ingesta (Fase 2): **(A) directo de cada canal** (ML×3, Web Woo,
Falabella, París, Walmart, POS), reusando el bridge del Monitor KDS. Razón: la
meta es soltar Defontana, y el Monitor ya tiene casi todo el trabajo hecho.

Aviso permanente de seguridad: en Fases 0-6 el núcleo **lee** ventas y rebaja
stock interno; **no escribe stock hacia los canales** (eso lo sigue haciendo
Defontana, como hoy). El reemplazo total —el núcleo propagando stock él mismo— es
la **Fase 7**, por pilotos acotados canal por canal (1-2 SKU antes de escalar
cada uno), porque ML cancela ventas por un falso "sin stock" (regla "PROHIBIDO
tocar stock").

---

## Alcance de la Fase 0

La Fase 0 entrega **el cimiento de datos y nada más**: la base de datos, la API de
stock vivo, la carga del maestro de productos y la inserción manual de
movimientos. NO incluye UI nueva, NI ingesta automática de canales, NI escritura
desde Inventario On Line (eso es Fase 1/2). Es deliberadamente pequeña y
verificable.

### Qué SÍ entrega

1. Base de datos con 3 tablas (`productos`, `movimientos`, `canal_map`).
2. API que devuelve **stock vivo** por SKU (calculado del libro).
3. Carga del maestro de productos desde el último export de Defontana (el mismo
   Excel de artículos que Inventario On Line ya parsea).
4. Endpoint para insertar un movimiento (idempotente).
5. Una prueba que falla si el libro suma mal o si la idempotencia se rompe.

### Qué NO entrega (fases posteriores)

- Lectura automática de canales (Fase 2).
- Escritura del saldo inicial desde la toma física (Fase 1).
- Panel/reportes (Fase 5).
- Cualquier escritura de stock hacia los canales.

---

## Arquitectura

### Dónde vive

Proyecto **nuevo e independiente** `erp-nucleo/` (no dentro de Inventario On
Line). Razón: el núcleo es un servicio compartido — tanto Inventario On Line como
el Monitor KDS (proyectos distintos) lo van a llamar. Una API "fuente de verdad"
no debe vivir dentro de uno de sus consumidores.

- **Stack:** Node + funciones serverless en Vercel (mismo patrón que Inventario
  On Line: carpeta `api/`, ESM, imports relativos con extensión `.js`).
- **Base de datos:** **Postgres** (Neon, free, vía Vercel Marketplace). Se eligió
  relacional sobre KV-JSON porque el libro de movimientos necesita agregación
  (`SUM ... GROUP BY`) y una restricción de unicidad para idempotencia — eso en un
  blob JSON se vuelve frágil. Una sola base para local y producción (string de
  conexión); las pruebas usan un esquema/DB desechable.

### Esquema (mínimo)

```sql
-- maestro único de productos
CREATE TABLE productos (
  codigo        TEXT PRIMARY KEY,   -- código interno = SKU (fuente: Defontana)
  descripcion   TEXT NOT NULL,
  familia       TEXT,
  costo         INTEGER DEFAULT 0,  -- costo neto en CLP
  activo        BOOLEAN DEFAULT TRUE,
  actualizado   TIMESTAMPTZ DEFAULT now()
);

-- EL LIBRO: todo el stock se deriva de aquí
CREATE TABLE movimientos (
  id        BIGSERIAL PRIMARY KEY,
  codigo    TEXT NOT NULL REFERENCES productos(codigo),
  tipo      TEXT NOT NULL,          -- 'saldo_inicial' | 'venta' | 'compra' | 'ajuste'
  cantidad  INTEGER NOT NULL,       -- +entra / -sale  (venta = negativo)
  canal     TEXT,                   -- 'ml1' | 'web' | 'falabella' | 'pos' | 'inventario' | ...
  ref       TEXT,                   -- id de documento/orden en el origen (para idempotencia)
  fecha     TIMESTAMPTZ DEFAULT now(),
  -- una venta/compra del mismo origen no se cuenta dos veces:
  UNIQUE (canal, ref, codigo)
);

-- traducción código interno <-> SKU/ID de cada canal
CREATE TABLE canal_map (
  canal        TEXT NOT NULL,
  sku_externo  TEXT NOT NULL,
  codigo       TEXT NOT NULL REFERENCES productos(codigo),
  PRIMARY KEY (canal, sku_externo)
);
```

**Stock vivo** = consulta, no columna:

```sql
SELECT codigo, COALESCE(SUM(cantidad), 0) AS stock
FROM movimientos GROUP BY codigo;
```
<!-- ponytail: GROUP BY directo. A cientos de SKU es instantáneo.
     Agregar tabla de saldo cacheado solo si el volumen de movimientos lo hace lento. -->

### Idempotencia (crítico)

El `UNIQUE (canal, ref, codigo)` es lo que hace confiable al libro: reingestar las
ventas de un canal (reintentos, recargas) **no** duplica movimientos. El insert usa
`ON CONFLICT (canal, ref, codigo) DO NOTHING`. Movimientos sin origen externo
(ajustes manuales, saldo inicial) usan un `ref` propio (p.ej. `ajuste-<fecha>` o el
id de la toma).

### API (funciones Vercel en `api/`)

| Método | Ruta | Hace |
|---|---|---|
| GET | `/api/stock` | stock vivo por SKU (codigo, descripcion, stock, costo, valor) |
| GET | `/api/stock?codigo=X` | stock vivo de un SKU |
| GET | `/api/productos` | lista del maestro |
| POST | `/api/movimientos` | inserta 1+ movimientos (idempotente por `ref`) |
| POST | `/api/productos/import` | carga/actualiza maestro desde export Defontana (upsert por `codigo`) |

Autenticación: token compartido por header (`x-erp-key`), simple, suficiente para
una API de un solo negocio. Sin login de usuarios en Fase 0.
<!-- ponytail: token único. OAuth/usuarios solo si alguna vez hay multi-usuario real. -->

### Carga inicial del maestro

`POST /api/productos/import` recibe el Excel de artículos de Defontana (el mismo
que Inventario On Line ya parsea con `server/parser.ts`) y hace upsert en
`productos` (codigo, descripcion, familia, costo). Reusar ese parser. El saldo
inicial **no** se setea aquí (eso es Fase 1, desde la toma física); tras la carga,
el stock vivo de todos es 0 hasta que entren movimientos.

---

## Flujo de datos (Fase 0)

```
Export Defontana (.xlsx artículos)
   │  POST /api/productos/import  (upsert)
   ▼
productos ──┐
            │   (Fase 1+: saldo_inicial, ventas, compras)
movimientos ┤── POST /api/movimientos (idempotente)
            │
            ▼
   GET /api/stock  →  SUM(cantidad) GROUP BY codigo  →  stock vivo
```

## Manejo de errores

- Insert de movimiento con `codigo` inexistente → 400 (no crear productos
  fantasma desde el libro).
- Conflicto de idempotencia → no es error: `DO NOTHING`, responde "ya existía".
- Import con filas malformadas → reporta cuántas se cargaron y cuántas se
  saltaron, no aborta todo.

## Pruebas (mínimo verificable)

`node:test` (mismo harness que Inventario On Line). Una suite que comprueba:

1. **El libro suma:** insertar saldo_inicial 100, venta −5, compra +20 →
   `GET /api/stock` devuelve 115.
2. **Idempotencia:** insertar dos veces la misma `(canal, ref, codigo)` → el stock
   no cambia la segunda vez.
3. **Producto inexistente:** movimiento con codigo desconocido → 400.

Sin frameworks extra, sin fixtures elaboradas; DB de prueba por string de conexión
desechable (`ERP_DB_URL` apuntando a un esquema temporal).

---

## Decisiones tomadas (para no re-litigar)

- Modelo de stock: **libro de movimientos** (no foto). Saldo inicial = toma física.
- Ingesta de ventas: **(A) directo de cada canal**, reusando el Monitor KDS (Fase 2).
- Núcleo = **proyecto/servicio independiente**, no dentro de Inventario On Line.
- Almacenamiento: **Postgres (Neon)**, no KV.
- DTE: **emisor externo por API**, no propio.
- Reemplazo total como meta; el núcleo propaga stock a los canales en la **Fase 7**, por pilotos acotados canal por canal. En Fases 0-6 no escribe stock a canales.

## Fuera de alcance explícito de la Fase 0

UI, ingesta automática, escritura desde la toma, reportes, compras, facturación.
Cada uno es una fase con su propio spec.
