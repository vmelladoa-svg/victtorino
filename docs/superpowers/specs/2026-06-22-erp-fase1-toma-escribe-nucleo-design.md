# ERP propio — Fase 1: la toma física escribe al núcleo

Fecha: 2026-06-22
Estado: diseño aprobado; pendiente revisión del spec.

## Contexto

El ERP propio tiene su núcleo de datos **en vivo** (Fase 0, https://erp-nucleo.vercel.app):
catálogo + libro de movimientos = stock vivo. Ver
`2026-06-21-erp-nucleo-fase0-design.md`.

**Marco (decisión de Victor):** el núcleo **ES** el sistema nuevo y es el **dueño**
del catálogo y del stock. Defontana ya no es la autoridad — es solo la semilla/
referencia de donde salieron los productos. La toma física (Inventario On Line) es
la fuente de verdad del stock y la empuja al núcleo.

La Fase 1 conecta lo que hoy es la herramienta de toma física (**Inventario On
Line**, https://inventario-online-xi.vercel.app, app serverless Vercel + Upstash KV)
con el núcleo: al **cerrar la toma**, el conteo se escribe en el núcleo.

## Meta de la Fase 1

Cuando el usuario marca una toma como cerrada en Inventario On Line, el stock del
núcleo queda **igual a lo contado** (la toma manda y sobrescribe), y los productos
nuevos descubiertos en la toma se crean en el núcleo.

### Qué SÍ entrega
1. Inventario On Line, al cerrar la toma, **sube el catálogo** al núcleo (upsert) y
   **cuadra el stock** de cada SKU contado a lo contado.
2. Los **hallazgos** (productos nuevos de la toma) se crean como productos en el núcleo.
3. Un botón **"Reenviar al ERP"** que repite el envío (idempotente) si falló la red.
4. Un resumen visible del resultado (productos subidos, ajustes, errores).

### Qué NO entrega (fases posteriores)
- Ingesta de ventas de canales (Fase 2).
- Mostrar el stock vivo del núcleo dentro de Inventario On Line (Fase 3).
- Propagación de stock a los canales (Fase 7).
- Edición de productos del catálogo dentro de la app (futuro; hoy el catálogo se
  siembra desde el Excel de Artículos que la app ya carga).

## Cómo se asienta el conteo (regla central)

El stock del núcleo = `SUM(movimientos.cantidad)`. Para que después de la toma el
núcleo quede con **exactamente lo contado**, se escribe un movimiento de **ajuste**:

```
ajuste = contado − stock_actual_del_núcleo
```

- Primera toma (núcleo en 0): `ajuste = contado − 0 = contado`.
- Toma siguiente (ya hubo ventas que rebajaron): `ajuste = contado − stock_actual`,
  que cuadra a lo contado **sin borrar** el historial de ventas.
- `contado = bodega[codigo].qty + exhibición[codigo].qty` (el total combinado; el
  núcleo maneja un solo stock por SKU).

Movimiento resultante: `{ codigo, tipo:'ajuste', cantidad: diff, canal:'inventario',
ref:'toma-<fechaCierreISO>' }`. Solo se envían los SKU con `diff ≠ 0`.

## Arquitectura

Todo el código nuevo vive en **Inventario On Line**
(`C:\Users\dell\Downloads\design_handoff_inventario\app\`). El núcleo no se toca
(su API de Fase 0 ya hace todo lo necesario).

### 1. Variables de entorno (Vercel, proyecto inventario-online)
- `ERP_NUCLEO_URL` = `https://erp-nucleo.vercel.app`
- `ERP_NUCLEO_KEY` = el token `x-erp-key` del núcleo.

### 2. Lógica pura: `construirEnvio(...)`
Función pura y testeable en `api/_nucleo.ts` (convención `_` de módulos compartidos
no-endpoint, como `_lib.ts`/`_parser.ts`). Sin I/O — recibe todo por parámetro.

```
construirEnvio({ articulos, conteos, exhibicion, hallazgos, ediciones, stockActual, tomaId })
  -> { productos: Producto[], movimientos: Movimiento[], sinCambio: number }
```
- `articulos`: catálogo de KV (`Articulo[]`: codigo, descripcion, costoVigente, ...).
- `conteos`, `exhibicion`: `Record<codigo,{qty,ts}>` (bodega y sala).
- `hallazgos`: `Hallazgo[]` (productos nuevos). Se incluyen los que tienen `codigo` y
  cuyo `tipo` NO es `duplicado`; quedan fuera los `ediciones[codigo].oculto`.
- `stockActual`: `Record<codigo, number>` leído del núcleo.
- `tomaId`: la fecha ISO del cierre (estable por cierre → `ref` estable).

Construye:
- `productos`: upsert del catálogo (`{codigo, descripcion, costo: costoVigente}`) +
  los hallazgos válidos (`{codigo, descripcion, costo: 0}`).
- `movimientos`: para cada SKU contado (catálogo y hallazgos), `diff = contado −
  (stockActual[codigo] ?? 0)`; si `diff ≠ 0` → `{codigo, tipo:'ajuste',
  cantidad:diff, canal:'inventario', ref:'toma-'+tomaId}`. Cuenta los `diff===0` en
  `sinCambio`.

### 3. Endpoint orquestador: `api/nucleo.ts` (nuevo)
Función serverless en Inventario On Line, mismo patrón que los demás `api/*.ts`.
`POST /api/nucleo` con body `{ tomaId }`:
1. Lee de KV: `articulos`, `conteos`, `exhibicion`, `hallazgos`, `ediciones`.
2. `GET ${ERP_NUCLEO_URL}/api/stock` (con header `x-erp-key`) → `stockActual`.
3. `construirEnvio(...)`.
4. `POST ${ERP_NUCLEO_URL}/api/productos` con `productos` (upsert).
5. `POST ${ERP_NUCLEO_URL}/api/movimientos` con `movimientos`.
6. Responde `{ productos: n, ajustes: n, sinCambio: n, errores: [...] }`.

Helper de llamada: `fetch` nativo (Node 18+ en Vercel) con header `x-erp-key`.

### 4. Frontend: gancho en el cierre
`src/App.tsx` — `onCerrarToma` (hoy solo setea el meta `tomaCerrada`). Tras setear el
meta, llama `pushNucleo(tomaCerradaISO)` (nuevo export en `src/api.ts`:
`fetch("/api/nucleo", {method:"POST", body:{tomaId}})`) y guarda el resultado en un
estado para mostrarlo. En el modal de cierre (`src/conteo.tsx`):
- mostrar el resumen del envío (productos subidos / ajustes / errores);
- botón **"Reenviar al ERP"** que vuelve a llamar `pushNucleo(tomaId)` con el mismo
  `tomaId` (idempotente).

## Idempotencia y seguridad de no-doblar
- `ref = 'toma-'+tomaId` (el cierre genera un ISO estable) + el `UNIQUE(canal,ref,
  codigo)` del núcleo → reenviar el mismo cierre no duplica.
- Como se cuadra contra el `stockActual` leído en el momento, un reenvío después de
  una venta intermedia **no la deshace**: el `diff` ya refleja el stock actual, y el
  `ref` repetido se ignora (`ON CONFLICT DO NOTHING`).
- Un cierre nuevo (otra fecha ISO) genera un `ref` nuevo y un cuadre nuevo — correcto.

## Manejo de errores
- Si el núcleo no responde (red/caído): `api/nucleo.ts` responde error; el frontend
  muestra "no se pudo enviar" y deja el botón **"Reenviar al ERP"**. La toma queda
  **cerrada localmente igual** (el cierre y el push son independientes) y el CSV sigue
  como respaldo. No se pierde nada.
- `POST /api/productos`/`/api/movimientos` que devuelvan error parcial: se reportan en
  `errores[]`, no se aborta el resto. (El upsert de productos va primero, así los
  movimientos no fallan por SKU inexistente.)
- Un movimiento con `codigo` no subido como producto → el núcleo responde 400; se
  cuenta en `errores`. No debería pasar porque el upsert precede a los movimientos.

## Pruebas
`node:test` (mismo harness de Inventario On Line). Se testea la función pura
`construirEnvio` con:
1. **Primera toma:** stockActual vacío → `ajuste = contado` para cada SKU contado.
2. **Re-toma con venta intermedia:** stockActual < contado → `ajuste = contado −
   stockActual` (cuadra), `sinCambio` cuenta los iguales.
3. **Hallazgo nuevo:** un hallazgo `tipo≠duplicado` con codigo → aparece en
   `productos` (costo 0) y su `movimiento` de ajuste.
4. **Excluidos:** hallazgo `tipo='duplicado'` y SKU con `ediciones[codigo].oculto` →
   NO aparecen ni en productos ni en movimientos.
5. **Sin cambio:** SKU cuyo contado == stockActual → no genera movimiento.

## Decisiones tomadas (para no re-litigar)
- La toma **sobrescribe**: el núcleo queda igual a lo contado, vía `ajuste = contado −
  stock_actual` (no foto, no suma).
- `contado = bodega + exhibición` (un solo stock por SKU).
- Disparo: al **marcar toma cerrada** + botón **"Reenviar al ERP"** con resultado visible.
- Hallazgos (productos nuevos): **se crean en el núcleo** (el núcleo es la nueva casa
  del catálogo; Defontana ya no es la autoridad). Se excluyen los `duplicado`/ocultos.
- Todo el código nuevo va en Inventario On Line; el núcleo no se modifica.
- El cierre local y el push al ERP son **independientes** (si falla el push, la toma
  igual queda cerrada y hay CSV de respaldo).

## Fuera de alcance explícito de la Fase 1
Ingesta de ventas de canales (Fase 2), mostrar stock vivo del núcleo en la app
(Fase 3), propagación a canales (Fase 7), edición de catálogo dentro de la app.
