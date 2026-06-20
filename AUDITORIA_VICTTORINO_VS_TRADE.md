# Auditoría funcional — victtorino.cl  vs  Trade (tradeglobalchile.cl)

Fecha: 2026-06-10 · Solo lectura (no se modificó ninguna fuente).

## Resumen ejecutivo
- **victtorino.cl** = tienda WooCommerce **completa y configurada** (~32 plugins): pago real Webpay,
  despacho por región + retiro en local, cuentas, wishlist, búsqueda avanzada, boleta electrónica,
  catálogo FB/Google, SEO. Pero **0 pedidos** (aún no ha vendido) y 16 clientes registrados.
- **Trade tiene DOS capas, ambas casi vacías de comercio:**
  - **Frontend Next.js** (el sitio nuevo, lindo): catálogo + carrito local + checkout **simulado**.
  - **Backend WooCommerce (Hostinger):** instalación **pelada** — solo woocommerce + litespeed +
    hostinger. **Sin pasarela de pago, 0 zonas de despacho, 0 clientes.** Solo tiene el catálogo (331).

> Conclusión: "emular toda la funcionalidad" = (1) dejar el **backend de Trade** a la par de
> victtorino (pago, despacho, etc.) y (2) conectar el **frontend Next** a ese backend (headless)
> para que herede todo con el diseño nuevo.

## Lo que tiene victtorino.cl (plugins clave)
| Plugin | Función |
|---|---|
| transbank-webpay-plus-rest | **Pago real Webpay** (tarjetas, Transbank) — ACTIVO |
| woo-enviame-shipping + woocommerce-services | Tarifas de despacho (courier Envíame) |
| retiro-tienda-victtorino (custom) | Retiro en local |
| ti-woocommerce-wishlist | Lista de deseos |
| advanced-woo-search | Búsqueda avanzada |
| woo-product-filter | Filtros de producto |
| yith-woocommerce-request-a-quote | Cotización / pedir presupuesto |
| woocommerce-abandoned-cart | Recuperación de carrito abandonado |
| facturacion-victtorino (custom) | **Boleta/factura electrónica** (Chile) |
| gnu-woo-order (custom) | Gestión de pedidos |
| facebook-for-woocommerce | Catálogo Facebook/Instagram |
| google-listings-and-ads | Google Shopping |
| seo-by-rank-math | SEO por producto |
| google-site-kit + hotjar | Analítica + mapas de calor |
| victtorino-sync (custom) | Sincronización con ERP (Defontana) |
| elementor + elementor-pro | Constructor de páginas |
| object-cache-pro / litespeed / cloudflare | Rendimiento |
| updraftplus | Respaldos |

**Pago activo:** Transbank Webpay Plus. **Despacho:** 3 zonas (RM, Regiones, Zona Centro) ×
(Precio fijo + Envío gratuito + Retiro en local). **Páginas:** Checkout, Mi Cuenta.

## Brecha por función (qué le falta a Trade)
| Función | victtorino | Front Next | Back Woo (Hostinger) | Prioridad |
|---|:---:|:---:|:---:|:---:|
| Pago real (Webpay) | ✅ | ❌ simulado | ❌ sin gateway | 🔴 Alta |
| Pedidos reales | ✅ | ❌ | ⚠️ base | 🔴 Alta |
| Despacho por región + retiro | ✅ | ❌ fijo | ❌ 0 zonas | 🔴 Alta |
| Boleta electrónica | ✅ | ❌ | ❌ | 🟠 Media |
| Cuentas de usuario / Mis pedidos | ✅ | ❌ | ⚠️ base | 🟠 Media |
| Stock y precio en tiempo real | ✅ | ❌ snapshot | ✅ | 🟠 Media |
| Sync con ERP (Defontana) | ✅ | ⚠️ npm sync | ❌ | 🟠 Media |
| SEO por producto (páginas) | ✅ | ⚠️ 1 página | — | 🟠 Media |
| Wishlist | ✅ | ❌ | ❌ | 🟡 Baja |
| Búsqueda avanzada | ✅ | ⚠️ básica | — | 🟡 Baja |
| Filtros de producto | ✅ | ⚠️ cat/orden | — | 🟡 Baja |
| Carrito abandonado | ✅ | ❌ | ❌ | 🟡 Baja |
| Reseñas / Cupones / Cotización | ✅ | ❌ | ⚠️ | 🟡 Baja |
| Catálogo FB/IG + Google Shopping | ✅ | ❌ | ❌ | 🟡 Baja |

## Recomendación (camino realista)
Rehacer TODO esto a mano en Next.js = meses + re-licenciar plugins pagados + recrear los plugins
custom. **No conviene.** Mejor aprovechar lo que victtorino ya tiene probado:

- **Fase 1 — Backend a la par:** configurar el WooCommerce de Trade (Hostinger) como victtorino:
  activar Webpay (Transbank), zonas de despacho + retiro, cuentas, boleta. Queda una tienda que
  **cobra de verdad**. (Requiere credenciales: cuenta Transbank/Webpay, cuenta Envíame, datos de
  facturación.)
- **Fase 2 — Headless:** conectar el frontend Next al backend vía WooCommerce Store API, para que
  el carrito, el pago, las cuentas y el stock sean reales — con el diseño nuevo por delante.
- **Fase 3 — Marketing/SEO:** Rank Math, catálogo FB/IG, Google Shopping, analítica.

## Ojo (consideraciones)
- Varios plugins son **pagados** (Elementor Pro, YITH, TI Wishlist, object-cache-pro, Envíame) o
  **custom de victtorino** (facturación, retiro, sync, gnu-order) — estos últimos hay que recrearlos
  o re-brandearlos.
- victtorino.cl es la marca VIEJA. Hay que replicar **función**, no la marca.
- El pago real exige credenciales de comercio (Transbank) y datos legales (boleta) que solo tú tienes.
