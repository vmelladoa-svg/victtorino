# Plan de migración: victtorino.cl → tradeglobalchile.cl

> **Misma página, mismo motor.** Se usa el sitio WP instalado y funcionando (el de victtorino.cl) con el nombre tradeglobalchile.cl. Solo cambia el dominio (y la marca a Trade cuando se quiera).
> **Decisión 2026-06-16: SIN 301.** Victor no quiere que buscar "Victtorino" lleve a Trade → victtorino.cl se **apaga**, no redirige. (Costo: no se hereda el SEO del dominio viejo; el sitio/ventas/integraciones sí se conservan.)
> Stack: WordPress/WooCommerce en **Cloudways** (app `fdgkhxzdsv`, `164.92.65.11`, WP-CLI por SSH) detrás de **Cloudflare**.

## Regla de oro
Hacerlo **en orden**, en **horario de bajo tráfico**, y con **backup antes de cada fase crítica**. Es 100% reversible si hay backup. NADA de esto se ejecuta sin tu OK y sin respaldo previo.

---

## FASE 0 — Preparación (antes de tocar nada)
- [ ] Confirmar que **tradeglobalchile.cl** está registrado y tienes acceso a su **DNS**.
- [ ] **Backup completo** del sitio (Cloudways full backup + export de base de datos). Crítico.
- [ ] Inventario de lo que referencia "victtorino" o el dominio viejo, para actualizar después:
  - mu-plugins (header, vtr-cf-purge, venta-whatsApp, etc.), textos, logo, favicon, emails de WooCommerce, OG tags.
  - Integraciones: GA4 (G-HNMY9BH35K) / GTM, Search Console, Webpay/Transbank (URLs de retorno), Defontana (webhooks/URLs), Meta/Google Ads (dominio verificado, pixel), marketplaces, redirects previos (`redirects_pendientes.md`).
- [ ] Definir alcance del **rebrand** visible (qué cambia a "Trade") — alineado con el rebrand ya en curso. Ojo Falabella: dejar "Taumm" donde corresponde (ver memoria de marca en marketplaces).

## FASE 1 — Agregar el dominio nuevo al MISMO sitio (sin romper el viejo)
- [ ] En **Cloudways**: agregar `tradeglobalchile.cl` (y `www`) como **dominio adicional** de la app `fdgkhxzdsv`. (Todavía NO lo pongas como primario.)
- [ ] **DNS/Cloudflare:** apuntar `tradeglobalchile.cl` al server Cloudways (registro A → `164.92.65.11`), idealmente gestionado por Cloudflare como el actual.
- [ ] Emitir **SSL** (Let's Encrypt en Cloudways) incluyendo el dominio nuevo.
- [ ] **Verificar:** que `tradeglobalchile.cl` ya carga el sitio (aún como Victtorino, sin redirect). Si carga = listo para el cambio.

## FASE 2 — Cambiar el dominio primario en WordPress (el corazón)
- [ ] **Backup otra vez** (justo antes).
- [ ] Modo mantenimiento breve (o ventana de bajo tráfico).
- [ ] Cambiar dominio primario (Cloudways "Change Domain") + en WP:
  - `wp option update home 'https://tradeglobalchile.cl'`
  - `wp option update siteurl 'https://tradeglobalchile.cl'`
- [ ] **Search-replace en la base** (cambia URLs internas, enlaces, imágenes):
  - Primero **dry-run**: `wp search-replace 'victtorino.cl' 'tradeglobalchile.cl' --all-tables --precise --dry-run`
  - Si se ve bien: el mismo comando **sin** `--dry-run`.
- [ ] Limpiar todas las caches: object-cache/LiteSpeed, **purge Cloudflare** (y el mu-plugin vtr-cf-purge), regenerar permalinks.
- [ ] **Verificar a fondo** en tradeglobalchile.cl: home, ficha de producto, **carrito, checkout/Webpay**, búsqueda, móvil.

## FASE 3 — Apagar victtorino.cl (SIN 301) — decisión 2026-06-16
> Victor NO quiere puente Victtorino→Trade. Por eso **NO se pone redirect 301**.
- [ ] Quitar `victtorino.cl` del servidor (sacarlo de los dominios de la app en Cloudways) para que **no lleve a nadie** a Trade.
- [ ] Dejar `victtorino.cl` sin apuntar (o pausarlo en DNS). NO redirige.
- [ ] **Consecuencia asumida:** se pierde el posicionamiento/SEO acumulado de victtorino.cl; tradeglobalchile.cl rankea desde cero. El SITIO, integraciones y ventas se conservan igual (no dependen del 301).

## FASE 4 — Rebrand visible (de cara al público)
- [ ] Nombre del sitio, **logo**, favicon, textos "Victtorino" → "Trade", footer, **emails de WooCommerce**, OG/redes.
- [ ] Revisar mu-plugins que muestren la marca o el dominio viejo.
- [ ] Marketplaces: marca pública → Trade (respetando lo de Taumm en Falabella).

## FASE 5 — Integraciones y SEO (para no perder posicionamiento)
- [ ] **Search Console:** agregar `tradeglobalchile.cl` como propiedad, verificar, y usar **"Cambio de dirección"** desde victtorino.cl (le avisa formalmente a Google). Subir **sitemap** nuevo.
- [ ] **GA4 / GTM:** actualizar el data stream / contenedor al dominio nuevo.
- [ ] **Webpay/Transbank:** actualizar URLs de retorno/confirmación al dominio nuevo (si no, se rompe el pago).
- [ ] **Defontana:** actualizar cualquier webhook/URL que apunte a victtorino.cl.
- [ ] **Ads (Meta/Google):** dominio verificado, pixel, enlaces de campañas.
- [ ] Actualizar enlaces en **WhatsApp, redes, firmas, flyers, QR**.

## FASE 6 — Verificación y monitoreo (días siguientes)
- [ ] Crawl del sitio: que no haya **404** ni cadenas de redirect.
- [ ] Revisar **Search Console** (cobertura, errores) la primera semana.
- [ ] Monitorear tráfico/posiciones (una **baja temporal es normal** y se recupera).
- [ ] **Mantener victtorino.cl registrado y redirigiendo por años** (no soltarlo nunca).

---

## Reparto
- **Yo (Claude):** ejecuto los comandos **WP-CLI por SSH** (tengo el acceso), configuro las reglas de Cloudflare si me das acceso, ajusto mu-plugins/textos del rebrand, y te guío en cada paso. Siempre con backup antes.
- **Tú:** accesos (DNS de tradeglobalchile.cl, Cloudways, Cloudflare, Search Console, Transbank, Defontana, Ads) y las decisiones de marca.

## Orden resumido
`Backup → agregar dominio+SSL → verificar → cambiar primario + search-replace → verificar → 301 → rebrand → integraciones → verificar/monitorear → mantener dominio viejo vivo.`
