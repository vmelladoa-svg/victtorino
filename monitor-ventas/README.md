# Monitor de Ventas Multicanal (estilo KDS) — MAQUETA

Tablero visual tipo "Kitchen Display System" pero para **ventas y preguntas** de todos
los canales (MercadoLibre ×cuentas, Falabella, París, Walmart, Web). Pensado para una
TV/monitor en bodega: las comandas caen en vivo, suenan, y el operador hace clic para
marcarlas como vistas. **No reemplaza la gestión en cada canal**, solo da visibilidad.

## Correr la maqueta

```bash
npm install
npm run dev
```

Abre el navegador en el puerto que indique Vite (configurado en `5180`).
Haz clic en **🔔 Activar sonido** una vez (el navegador exige un gesto del usuario
antes de reproducir audio).

## Qué hace hoy (maqueta, datos mock)

- Set inicial de ~16 comandas con antigüedades variadas.
- Generador que agrega una comanda nueva cada **5–15 s** (en `src/lib/mock.ts`).
- Al caer una nueva: **din-don** (Web Audio API, sin archivos) + animación de entrada.
- **Clic** en la tarjeta → animación de salida → se quita del tablero. No escribe en
  ningún sistema externo (el punto de "historial a futuro" está comentado en `App.tsx`).
- Las comandas más antiguas se **intensifican** (ámbar a los 3 min, rojo pulsante a los 6).
- Encabezado: contadores en vivo, filtro por tipo y canal, mute, reloj.

## Conectar las APIs reales (fase posterior)

Todo lo de datos vive en `src/lib/`:

| Archivo | Rol |
|---|---|
| `lib/mock.ts` | Datos de prueba + generador. **Se reemplaza** por las fuentes reales. |
| `lib/sources/index.ts` | Orquesta todas las fuentes y valida cada venta con Defontana. |
| `lib/sources/mercadolibre.ts` | Stub: orders + questions por cuenta (C1/C2/C3), idealmente webhooks. |
| `lib/sources/falabella.ts` | Stub: Seller Center API. |
| `lib/sources/paris.ts` | Stub: Mirakl (Cencosud). |
| `lib/sources/walmart.ts` | Stub: Mirakl (Lider). |
| `lib/sources/web.ts` | Stub: WooCommerce REST (orders) + contacto. |
| `lib/sources/defontana.ts` | **Validador**, no fuente: confirma la venta en el ERP. |

Pasos para la fase real:

1. Implementar cada stub `obtenerNuevas(desde)` para que devuelva las comandas nuevas.
2. En `App.tsx`, reemplazar el `setInterval` del generador mock por un polling/websocket
   que llame a `obtenerTodas(desde)` de `lib/sources/index.ts`.
3. Defontana **no dispara** comandas: por cada venta se llama a `validarEnDefontana()` y
   se setea `validadoDefontana` (ya cableado en `obtenerTodas`). En la tarjeta se ve como
   `✓ Defontana` / `⚠ Sin validar`.

Colores/íconos por canal: `lib/channels.ts`. Formato CLP y "hace X": `lib/format.ts`.

## Canales conectados (real, solo lectura)

`/feed` (middleware de Vite) agrega todos los canales conectados; el frontend hace un solo poll.

- **MercadoLibre** (`server/ml-feed.mjs`): C1/C2/C3 vía API oficial, tokens en `tokens_cuenta{1,2,3}.json` (refresh automático). Ventas + preguntas.
- **Web WooCommerce** (`server/web-feed.mjs`): tradeglobalchile.cl `/wc/v3/orders` (processing/on-hold), llaves WC. Solo ventas.
- **Falabella** (`server/falabella-feed.mjs` + refrescador): el endpoint está tras WAF y solo responde a la app en el navegador, así que un **refrescador Playwright** captura las órdenes y las vuelca a `server/falabella_raw.json`, que el feed lee.

### Refrescador de Falabella

```bash
npm run fala:login     # 1ª vez: abre Chrome, inicia sesión como Trade Global (perfil server/.fala-profile)
npm run fala:refresh   # deja corriendo: captura órdenes pendientes cada 5 min (headless)
```

Reutilizar una sesión ya logueada: `FALA_PROFILE=<ruta-perfil> npm run fala:refresh`.
Para que sea siempre-activo, programar `fala:refresh` como tarea de Windows. Si la sesión expira,
volver a correr `fala:login`. El feed sirve lo último capturado; si el JSON falta, Falabella sale vacío (no inventa).
