# Instructivo — Activar Cloudflare APO en victtorino.cl

**Objetivo:** que Cloudflare guarde el HTML en su nodo cercano (Santiago/Buenos Aires) y deje de ir a California en cada visita → TTFB de ~1 s a ~150 ms para clientes en Chile/Latam.

**Tu situación:** el dominio ya está en Cloudflare (nameservers `elliot/laura.ns.cloudflare.com` ✅), así que solo falta activar APO y conectar el plugin.

> ⚠️ **Clave para tiendas:** APO cachea el HTML en el borde. Hay que asegurar que el **carrito, checkout y "mi cuenta"** NO se sirvan cacheados. El plugin oficial de Cloudflare lo hace automático (detecta las cookies de WooCommerce y salta la caché). Por eso **instalamos el plugin sí o sí**, no solo el botón del panel.

---

## PASO 0 — Verificar el plan de Cloudflare (costo)

- **APO en plan gratis:** cuesta **US$5/mes** (se activa con tarjeta).
- **APO en plan Pro (US$20/mes) o superior:** viene **incluido**.

Si solo quieres APO, lo más barato es plan gratis + los $5 de APO.

---

## PASO 1 — Instalar el plugin oficial de Cloudflare en WordPress

1. Entra a **victtorino.cl/wp-admin/**
2. **Plugins → Añadir nuevo** → busca **"Cloudflare"** (autor: **Cloudflare, Inc.**)
3. **Instalar** → **Activar**

---

## PASO 2 — Crear un API Token en Cloudflare (para conectar el plugin)

1. Entra a **dash.cloudflare.com** → arriba a la derecha, tu perfil → **My Profile → API Tokens**
   (o directo: https://dash.cloudflare.com/profile/api-tokens )
2. **Create Token** → usa la plantilla **"WordPress"** (Cloudflare la trae lista) → **Use template**
3. En "Zone Resources" deja: **Include → Specific zone → victtorino.cl**
4. **Continue to summary → Create Token**
5. **Copia el token** (se muestra una sola vez). Guárdalo.

---

## PASO 3 — Conectar el plugin

1. En wp-admin → **Configuración (Settings) → Cloudflare**
2. Clic en **"Sign in here"** (o "Enter your authentication") → elige **API Token**
3. Pega el **token** del paso 2 → **Save / Sign in**
4. Debe quedar conectado y mostrar tu dominio `victtorino.cl`.

---

## PASO 4 — Activar APO (el interruptor que importa)

1. En la misma pantalla del plugin de Cloudflare en wp-admin, busca:
   **"Automatic Platform Optimization (APO)"**
2. Activa el toggle **"Enable Automatic Platform Optimization for WordPress"**.
   - Si es plan gratis, aquí te pedirá confirmar la suscripción de **US$5/mes**.
3. Marca también, si aparece: **"Cache by device type"** solo si usas diseños muy distintos en móvil/desktop (en general **déjalo apagado**, así cachea mejor).
4. Guarda.

> Esto activa APO tanto en el plugin como en tu zona de Cloudflare automáticamente. No necesitas tocar el dashboard aparte.

---

## PASO 5 — Verificación de seguridad para la TIENDA (no te saltes esto)

Confirma que el carrito/checkout NO se cachean:

1. En **incógnito**, agrega un producto al carrito.
2. Entra a **victtorino.cl/carrito/** → debe mostrar **tu** carrito (no vacío, no el de otro).
3. Entra a **/finalizar-compra/** (checkout) → debe cargar tu pedido bien.
4. Si todo se ve correcto y personalizado → APO está respetando las cookies de WooCommerce ✅.

Si algo del carrito se viera "pegado"/incorrecto, avísame y ajustamos las reglas de bypass (es raro con el plugin oficial, pero se soluciona en 2 minutos).

---

## PASO 6 — Comprobar que APO está cacheando (opcional, técnico)

- Abre la home, recárgala 2-3 veces.
- Con las herramientas del navegador (F12 → Network → click en el documento principal → Headers) busca:
  - `cf-cache-status: HIT` ← ✅ APO funcionando (antes decía `DYNAMIC`)
  - `cf-edge-cache: cache,platform=wordpress`
- O dime y lo verifico yo desde fuera (mido el TTFB nuevo y confirmo el HIT).

---

## Si algo sale mal (rollback)

- En wp-admin → Settings → Cloudflare → **apaga el toggle de APO**. Listo, vuelve a como estaba.
- O en dash.cloudflare.com → Speed → Optimization → desactivar APO.

---

## Convivencia con LiteSpeed Cache

- APO (borde de Cloudflare) y LiteSpeed (plugin, optimiza CSS/JS) **conviven bien**.
- No es necesario desactivar LiteSpeed. Mantén **minify CSS/JS activo** y **object cache de LiteSpeed APAGADO** (ya está así).
- Cuando publiques/edites productos, el plugin de Cloudflare purga el caché del borde automáticamente.

---

**Resumen:** instalar plugin Cloudflare → token → conectar → activar APO → probar carrito. Con eso, tu tienda pasa a servirse desde un nodo cercano a Chile y se siente casi instantánea para tus clientes.
