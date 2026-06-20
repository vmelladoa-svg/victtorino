# Trade — Tienda online (Next.js)

Tienda e-commerce de una página para **Trade** ("Soluciones para tu hogar"), recreada en
Next.js (App Router + TypeScript) a partir de la especificación de diseño hifi.

## Stack
- **Next.js 15** (App Router) + **React 19** + **TypeScript**
- CSS global con los design tokens exactos de la marca (`app/globals.css`)
- Fuentes **Sora** + **Hanken Grotesk** vía `next/font`
- Estado del carrito con React Context + `localStorage` (clave `trade_cart_v1`)

## Estructura
```
app/
  layout.tsx        # fuentes, metadata, StoreProvider + overlays globales
  page.tsx          # composición del home (server component)
  globals.css       # design tokens + estilos de componentes
components/          # Header, Hero, Catalog, ProductCard, CartDrawer, Checkout, etc.
lib/
  products.ts       # 172 productos (fuente de verdad — reemplazar por CMS/BD en prod)
  types.ts          # tipos Product / CartItem / CategoryName
  categories.ts     # las 7 categorías + conteo
  store-context.tsx # carrito + estado de UI (drawer, modal, checkout, toast, filtro)
  site.ts           # datos de contacto/marca (provisorios)
  format.ts         # formato CLP es-CL
public/logo.png     # logo de la marca
```

## Desarrollo
```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # build de producción
npm run start    # sirve el build
npm run sync     # resincroniza catálogo + fotos desde la tienda (solo lectura)
```

### Atributos / ficha técnica (`npm run enrich`)
`scripts/enrich-attributes.mjs` agrega los atributos (marca, material, color, medidas, etc.) a
cada producto en `lib/products.ts`, desde MercadoLibre (ítems por SKU `ML-MLC...` + catálogos
completos de las 3 cuentas: C3 en vivo + C1/C2 desde los snapshots `.c1-attrs.json` /
`.c2-attrs.json`) con fallback a atributos derivados del nombre. **Correr DESPUÉS de `npm run sync`**
(sync regenera `products.ts` sin atributos). Requiere credenciales ML C3 en el `.env` de la raíz
del repo. Cobertura actual: **193 con atributos ricos de ML + 96 derivados del nombre = 289/331**.
Los snapshots `.cN-attrs.json` (gitignored) se regeneran reautorizando C1/C2 por OAuth si su
catálogo cambia.

### Sincronizar catálogo (`npm run sync`)
`scripts/sync-catalog.mjs` trae nombre, precio, oferta, SKU, categoría y la foto de cada
producto desde la tienda WooCommerce **en modo solo lectura** (no modifica la fuente):
`wp eval-file` por SSH para los datos y `tar` para las imágenes (ssh/stdin manejados por
Node, multiplataforma). Regenera `lib/products.ts` y `public/products/`. Configurable por
env vars (`TRADE_SSH`, `TRADE_SSH_PORT`, `TRADE_SSH_KEY`, `TRADE_WP_PATH`, `TRADE_BASE_URL`);
los defaults apuntan al server actual de Hostinger.

## Catálogo (datos reales)
`lib/products.ts` contiene **331 productos reales** sincronizados (solo lectura) desde la
tienda Trade en WooCommerce: nombre, precio, precio de oferta, SKU, categoría y **galería de
fotos** (`images[]`, principal primero). Las fotos reales están en `public/products/` (~1085
imágenes; 221 productos con galería). Las 11 categorías de la tienda se mapean a las 7 del
diseño (Lavaplatos→Cocina, Lavamanos/Dispensador/Agarraderas→Baño, etc.). El modal de
producto muestra la galería con miniaturas; las cards usan `image` (la principal).

## Pendiente para producción
- **Checkout**: el paso de pago es una simulación → conectar Webpay/Transbank o Mercado Pago.
- **Datos de contacto** (`lib/site.ts`): WhatsApp y email son provisorios.
- **Catálogo en vivo**: hoy el catálogo es un snapshot. En producción conviene alimentarlo
  desde la misma BD/CMS de la tienda (o un export programado) para mantenerlo sincronizado.
- **Stock**: el dato de stock de la fuente no es fiable (muchos en 0/1), por eso el badge
  "Últimas unidades" está desactivado. Reactivar cuando el stock sea confiable.
- **Newsletter**: conectar a la herramienta de email marketing.
