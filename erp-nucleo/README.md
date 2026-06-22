# erp-nucleo

Núcleo de datos del ERP propio (Fase 0): catálogo + libro de movimientos + stock vivo.
Es la fuente única de verdad: el stock se **calcula** (saldo inicial + compras − ventas), no se guarda como número.

## Variables de entorno
- `ERP_DB_URL` — string de conexión Postgres (Neon). Si NO está definida, usa PGlite en memoria (dev/tests).
- `ERP_KEY` — token compartido; va en el header `x-erp-key` de cada request.

## Endpoints (todos requieren header `x-erp-key`)
- `GET /api/stock` — stock vivo por SKU. `?codigo=X` para uno solo.
- `GET /api/productos` — maestro de productos.
- `POST /api/productos` — importar/actualizar maestro (array de filas o `{filas:[...]}`); upsert por `codigo`.
- `POST /api/movimientos` — insertar movimiento(s). Idempotente por `(canal, ref, codigo)`.

### Forma de un movimiento
```json
{ "codigo": "A1", "tipo": "venta", "cantidad": -3, "canal": "ml1", "ref": "orden-99" }
```
`tipo`: `saldo_inicial` | `venta` | `compra` | `ajuste`. `cantidad`: + entra / − sale.
Ventas/compras deben traer `canal` + `ref` (para no doble-contar). Movimientos sin `ref` se insertan siempre.

## Local / tests
```
npm install
npm test          # 13 tests contra PGlite en proceso, sin DB externa
```

## Deploy (producción, Vercel + Neon)
```
vercel link
vercel env add ERP_DB_URL production   # connection string de Neon
vercel env add ERP_KEY production       # token elegido
ERP_DB_URL=<url-neon> npm run db:init   # crea el esquema en Neon
vercel deploy --prod --yes
```

## Roadmap
Fase 0 (esto) = núcleo. Siguientes: 1 toma física escribe el saldo inicial · 2 ventas de canales rebajan · 3 stock vivo de vuelta a Inventario On Line · 4 compras · 5 reportes · 6 facturación DTE (emisor externo) · 7 propagación de stock a canales (pilotos por canal). Ver `docs/superpowers/specs/2026-06-21-erp-nucleo-fase0-design.md`.
