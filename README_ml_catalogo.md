# ml_catalogo_publicaciones.py

Rescata todas las publicaciones en **catalog listing** (`catalog_listing = true`)
de las cuentas MercadoLibre conectadas (C1 / C2 / C3) y exporta a Excel + CSV.

## Que hace

1. Para cada cuenta corre 3 busquedas (union de resultados):
   - `GET /users/{id}/items/search?search_type=scan&status=active`  (scroll, sin tope)
   - `GET /users/{id}/items/search?listing_type_id=gold_pro&status=active`
   - `GET /users/{id}/items/search?catalog_listing=true`
2. Hace **multi-get** `/items?ids=...&attributes=...` (lotes de 20) y filtra
   `catalog_listing == true`.
3. Exporta:
   - `catalogo_publicaciones_YYYY-MM-DD.xlsx` con una hoja por cuenta + hoja `RESUMEN`
   - `catalogo_publicaciones_YYYY-MM-DD.csv` consolidado
4. Imprime el resumen por consola.

## Autenticacion

El script reutiliza los archivos que ya genera `ml_auth.py`:

```
tokens_cuenta1.json
tokens_cuenta2.json
tokens_cuenta3.json
```

y las credenciales de app en `.env`:

```
ML_CLIENT_ID=...
ML_CLIENT_SECRET=...
```

(si no estan en `.env` usa el `CLIENT_ID/SECRET` hardcodeados en `ml_auth.py`).

Cuando un access token devuelve 401, el script llama a `/oauth/token` con el
`refresh_token`, actualiza el JSON correspondiente y reintenta la llamada
transparentemente. Tambien sincroniza `.env` si la clave existia.

Para generar tokens desde cero:

```powershell
python ml_auth.py 1     # muestra URL OAuth
python ml_auth.py 1 TG-xxxxxx   # intercambia codigo por token
```

## Instalacion

```powershell
pip install -r requirements_ml_catalogo.txt
```

## Uso

```powershell
# todas las cuentas
python ml_catalogo_publicaciones.py

# solo una
python ml_catalogo_publicaciones.py --cuenta C3

# nombre de salida custom
python ml_catalogo_publicaciones.py --salida catalogo_qa.xlsx
```

## Manejo de errores

- **429 (rate limit)**: respeta `Retry-After`; si no viene, espera
  `2^intento` segundos con jitter (hasta 60 s). Hasta 5 reintentos.
- **5xx**: backoff exponencial hasta 30 s, 5 reintentos.
- **401**: refresh + reintento (una sola vez por request).
- **items que fallan en multi-get**: se loguean uno a uno en
  `data/catalogo_logs/errores_<CUENTA>_<epoch>.txt`.

## Columnas exportadas

`seller_id, cuenta, item_id, title, catalog_product_id, listing_type_id,
price, available_quantity, status, permalink, thumbnail, date_created,
last_updated`

## Notas tecnicas

- `/users/{id}/items/search` con `offset` tiene tope ~1000; por eso usamos
  `search_type=scan` (scroll) para la pasada principal y `offset` solo
  para los filtros mas estrechos.
- `catalog_listing` es un **atributo del item**, no una bandera fiable
  del search en todas las cuentas; por eso siempre se valida con la
  respuesta de `/items`.
