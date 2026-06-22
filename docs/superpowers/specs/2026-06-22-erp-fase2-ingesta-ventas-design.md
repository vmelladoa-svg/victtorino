# ERP propio — Fase 2: ingesta de ventas (Web + ML) que rebajan el núcleo

Fecha: 2026-06-22
Estado: diseño aprobado; pendiente revisión del spec.

## Contexto

El núcleo del ERP está en vivo (Fase 0) y la toma física ya escribe el stock real
(Fase 1). La Fase 2 hace que las **ventas de cada canal rebajen** el stock del
núcleo automáticamente, en vivo, entre tomas.

**Decisiones de Victor:**
- Canales en esta fase: **WooCommerce (Web) + Mercado Libre ×3** (los de API).
  Falabella queda como piloto aparte (su scraping de detalle por orden es otro tema).
- **Dónde corre:** un trabajo en la **PC de bodega**, junto al Monitor de Ventas,
  reusando el OAuth de ML y el cliente WooCommerce que el Monitor ya tiene ahí.
- **Marca de agua:** solo se rebajan ventas **posteriores a la última toma**; las
  anteriores ya están en el conteo físico (si no, se restaría doble).

**Por qué NO se reusa el `/feed` del Monitor tal cual:** ese feed es para *mostrar*
(KDS), no para *contabilizar*. No extrae la cantidad, toma solo la primera línea de
cada orden, y no filtra canceladas en ML. La Fase 2 construye ingesta de **grado
contable** reusando la *plomería* del Monitor (auth/clients), no su feed.

## Meta de la Fase 2

Cada venta confirmada de Web y ML, posterior a la última toma, genera en el núcleo
un movimiento `venta` negativo, una sola vez, rebajando el stock vivo.

### Qué SÍ entrega
1. Un trabajo `erp-ingesta.mjs` en la PC de bodega que lee ventas confirmadas de
   WooCommerce + ML ×3 y las manda al núcleo como movimientos negativos.
2. Lógica contable correcta: todas las líneas de cada orden, con cantidad, solo
   confirmadas, solo posteriores a la marca de agua.
3. Idempotencia por `(canal, ref, codigo)` — una orden nunca se cuenta dos veces.
4. SKU sin mapear se **saltan y registran**, sin frenar el lote.
5. Tarea programada de Windows (cada ~10-15 min), patrón del refresher de Falabella.

### Qué NO entrega (después)
- Falabella (piloto aparte — necesita fetch del detalle por orden).
- Reversa de devoluciones/cancelaciones de una venta ya ingestada (la próxima toma
  re-cuadra vía reconciliación).
- Poblar `canal_map` del núcleo para SKU que no calzan (hoy se saltan y registran).
- Propagación de stock HACIA los canales (eso es Fase 7).

## Arquitectura

Todo el código nuevo vive en **`C:\Users\dell\victtorino\monitor-ventas\server\`**.
El núcleo no se modifica.

### Componentes
1. **`erp-build.mjs`** — función pura y testeable (JS plano `.mjs`, sin I/O):
   ```
   construirVentas({ ordenes, canal, codigosConocidos, cursorTs })
     -> { movimientos: Mov[], saltados: Saltado[], maxTs: number }
   ```
   - `ordenes`: normalizadas por el fetcher → `{ orderId, fecha (ms), confirmada (bool), lineas: [{ sku, qty }] }[]`.
   - `canal`: `'web' | 'ml1' | 'ml2' | 'ml3'`.
   - `codigosConocidos`: `Set<string>` de códigos que el núcleo ya tiene.
   - `cursorTs`: marca de agua (ms); solo se procesan órdenes con `fecha > cursorTs`.
   - Por cada orden confirmada y posterior al cursor, por cada línea: si `sku ∈
     codigosConocidos` → `{ codigo: sku, tipo:'venta', cantidad: -qty, canal, ref:
     String(orderId) }`; si no → `saltados.push({ canal, orderId, sku, qty })`.
   - `maxTs` = mayor `fecha` entre las órdenes procesadas (para avanzar el cursor).

2. **`erp-ingesta.mjs`** — el orquestador (I/O). Al correr (`--once` o en loop):
   1. Lee `erp-cursor.json` (marca de agua por canal).
   2. `GET ${ERP_NUCLEO_URL}/api/productos` (header `x-erp-key`) → `codigosConocidos`.
   3. Por cada canal: el fetcher trae ventas recientes confirmadas → normaliza →
      `construirVentas(...)`.
   4. `POST ${ERP_NUCLEO_URL}/api/movimientos` con `movimientos` (idempotente).
   5. Si el POST fue OK, avanza el cursor del canal a `maxTs` y persiste
      `erp-cursor.json`. Registra `saltados` en un log.

3. **`erp-cursor.json`** — `{ "web": ts, "ml1": ts, "ml2": ts, "ml3": ts }` (ms).
   Sembrado al activar con la fecha de la última toma. Avanza por canal cada corrida.

4. **Fetchers por canal** (reusan la plomería del Monitor):
   - **Web (WooCommerce):** `GET /wp-json/wc/v3/orders?status=processing,completed&
     per_page=50&orderby=date&order=desc` (Basic auth `WC_CONSUMER_KEY/SECRET`).
     Normaliza: `orderId = o.id`, `fecha = Date.parse(o.date_created_gmt + 'Z')`,
     `confirmada = true` (el query ya filtra), `lineas = o.line_items.map(li => ({
     sku: li.sku, qty: li.quantity }))`. (Reusa el cliente de `web-feed.mjs`.)
     Nota: el feed actual usa `status=processing,on-hold`; para contabilidad se usa
     `processing,completed` (on-hold = sin pagar, no es venta confirmada).
   - **ML ×3:** `GET /orders/search/recent?seller={uid}&sort=date_desc&limit=50`
     (Bearer OAuth; tokens en `secrets/tokens_cuenta{1,2,3}.json`, refresco en 401
     vía `ML_CLIENT_ID/SECRET` — reusar los helpers de `ml-feed.mjs`). Normaliza por
     orden: `orderId = o.id`, `fecha = Date.parse(o.date_created)`, `confirmada =
     (o.status === 'paid')`, `lineas = o.order_items.map(oi => ({ sku:
     oi.item.seller_sku, qty: oi.quantity }))`. Cada cuenta → canal `ml1/ml2/ml3`.

### Mapeo SKU → código interno
- Web: `li.sku`. ML: `oi.item.seller_sku`. Se asume que el código interno se cargó
  como SKU al publicar.
- **Filtro de seguridad:** el núcleo rechaza un código inexistente y rechazar uno
  aborta el lote entero (`insertarMovimientos` lanza 400 en el primer desconocido).
  Por eso la ingesta lee `codigosConocidos` del núcleo y **solo manda los que
  existen**; los demás van a `saltados[]` (log) para arreglar después. El núcleo no
  se modifica.

## Flujo de datos

```
erp-cursor.json (marca de agua)
        │
        ▼
GET núcleo /api/productos ──► codigosConocidos (Set)
        │
   por canal: fetcher (Woo / ML×3) ──► ordenes normalizadas
        │
   construirVentas(ordenes, canal, codigosConocidos, cursorTs)
        │
   ├─► movimientos[]  ──► POST núcleo /api/movimientos (idempotente)
   ├─► saltados[]     ──► log (SKU sin mapear)
   └─► maxTs          ──► avanza cursor del canal (si POST OK) ──► erp-cursor.json
```

## Idempotencia y marca de agua
- `ref = String(orderId)` + `UNIQUE(canal, ref, codigo)` del núcleo → una orden
  nunca se cuenta dos veces, aunque se reprocese una ventana solapada.
- El cursor (marca de agua) evita reprocesar y, sobre todo, **evita restar ventas
  previas a la toma** (que ya están en el conteo). Se inicializa con la fecha de la
  última toma al activar la Fase 2.
- Una toma nueva re-cuadra el stock por reconciliación (Fase 1); el cursor solo
  avanza, no necesita detectar tomas.

## Manejo de errores
- Si el núcleo no responde (POST falla): **no se avanza el cursor** de ese canal →
  se reintenta en el próximo ciclo (la idempotencia evita dobles).
- Si un fetcher de un canal falla (token, red): se salta ese canal en esa corrida,
  los demás siguen; se reintenta al próximo ciclo.
- Errores parciales por código desconocido: se previenen con el filtro
  `codigosConocidos` (no llegan al POST); quedan en `saltados[]`.

## Cómo corre
- Tarea programada de Windows que ejecuta `node server/erp-ingesta.mjs --once` cada
  ~10-15 min (archivo `.cmd` como `server/fala_refresh.cmd`). Modo `--once` corre
  una pasada y termina. (Opcional: modo loop con `setInterval` para dev.)
- Variables: `ERP_NUCLEO_URL`, `ERP_NUCLEO_KEY` (las del núcleo), más las
  credenciales de Woo/ML que el Monitor ya usa.

## Pruebas
`node --test server/erp-build.test.mjs` (JS plano, sin tsx). Casos de
`construirVentas`:
1. **Multi-línea:** una orden con 3 líneas → 3 movimientos con sus cantidades
   negativas.
2. **Cantidad:** `qty: 2` → `cantidad: -2`.
3. **Cancelada/no confirmada:** orden con `confirmada:false` → no genera movimiento.
4. **Anterior al cursor:** orden con `fecha <= cursorTs` → no entra.
5. **SKU desconocido:** línea cuyo `sku ∉ codigosConocidos` → va a `saltados`, no a
   `movimientos`.
6. **`maxTs`:** es la mayor `fecha` de las órdenes procesadas (para avanzar el cursor).
7. **`ref` por orden:** dos líneas de la misma orden comparten `ref = orderId`.

## Decisiones tomadas (para no re-litigar)
- Canales: Web + ML ×3. Falabella aparte.
- Corre en la PC de bodega (tarea programada), reusando plomería del Monitor.
- Marca de agua desde la última toma; idempotencia por `(canal, ref, codigo)`.
- SKU sin mapear → se saltan y registran, NO frenan el lote (filtro
  `codigosConocidos`, núcleo intacto).
- `canal`: `web`, `ml1`, `ml2`, `ml3`. `ref` = id de orden.
- El núcleo NO se modifica.

## Fuera de alcance explícito de la Fase 2
Falabella, reversa de cancelaciones/devoluciones, poblar `canal_map`, propagación de
stock hacia los canales (Fase 7).
