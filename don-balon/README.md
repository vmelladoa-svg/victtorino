# 🏀 Don Balón — Maqueta E-commerce Deportiva

Maqueta (prototipo frontend) de una tienda online premium de artículos deportivos
(pelotas de fútbol, básquetbol, béisbol, vóleibol y accesorios). **No es una tienda en
producción**: el carrito funciona en el navegador y el pago con Webpay está **simulado**.

## 🧱 Stack
- **Next.js 14** (App Router) + React + TypeScript
- **Tailwind CSS** (identidad de marca en `tailwind.config.ts`)
- **Zustand** para el carrito (persistencia en `localStorage`)
- `next/image` optimizado · imágenes placeholder (`placehold.co`)
- Datos mock en `data/products.ts` · capa de servicios en `lib/api.ts`
- Stub de pago en `lib/payments/transbank.ts`

## 🚀 Instalación y uso
```bash
npm install
npm run dev      # http://localhost:3000
```
Otros scripts: `npm run build` (compilar) · `npm start` (servir build) · `npm run lint`.

## 📁 Estructura
```
app/
  layout.tsx              · layout + fuentes + Header/Footer/CartDrawer
  page.tsx                · Home
  catalogo/page.tsx       · Catálogo (filtros + orden)
  producto/[slug]/page.tsx· Ficha de producto
  checkout/page.tsx       · Checkout (1 paso) → Webpay
  checkout/confirmacion/  · Pantalla de pago confirmado (mock)
  sobre · envios · contacto · faq
components/                · Header, Footer, CartDrawer, ProductCard, Catalog, ProductDetail
lib/
  format.ts               · formatCLP() y helpers
  store.ts                · estado del carrito (Zustand + persist)
  api.ts                  · servicios mock (reemplazar por API real)
  payments/transbank.ts   · STUB de Webpay Plus (listo para integrar)
data/products.ts          · ~20 productos mock
```

## 💵 Moneda
Todos los precios en **CLP** con formato chileno (`$19.990`) mediante el helper
`formatCLP()` en `lib/format.ts`. Úsalo en toda la UI.

## 🔌 Cómo conectar Transbank Webpay Plus en producción

> El pago real **nunca** debe ejecutarse en el cliente: las credenciales van solo en el servidor.

1. **Instala el SDK oficial:**
   ```bash
   npm i transbank-sdk
   ```
2. **Variables de entorno** (`.env.local`, nunca commitear):
   ```
   TBK_COMMERCE_CODE=tu_codigo_comercio
   TBK_API_KEY=tu_api_key
   TBK_ENV=integration        # o "production"
   ```
3. **Crea route handlers en el servidor** (mueve la lógica del stub aquí):
   - `app/api/webpay/create/route.ts` → usa `WebpayPlus.Transaction.create(...)` y devuelve `{ token, url }`.
   - `app/api/webpay/commit/route.ts` → recibe `token_ws` y hace `tx.commit(token)`.
   El código de referencia (comentado) ya está en **`lib/payments/transbank.ts`**.
4. **En el checkout** (`app/checkout/page.tsx`), en la función `handlePay()` está marcado el
   **PUNTO DE INTEGRACIÓN**: reemplaza la llamada al stub `createWebpayTransaction()` por un
   `fetch("/api/webpay/create")`, y luego haz el **POST-redirect** al formulario de Transbank
   con el `token` recibido (Webpay devuelve `url` + `token`).
5. **Retorno:** Transbank redirige a tu `returnUrl` con `token_ws`. En
   `app/checkout/confirmacion/page.tsx` (o un route handler) llama a `commit` para confirmar y
   muestra el resultado real (hoy `commitWebpayTransaction()` está mockeado).

### Archivos que tocarías
| Archivo | Cambio |
|---|---|
| `lib/payments/transbank.ts` | Reemplazar cuerpos mock por el SDK (hay ejemplo comentado) |
| `app/api/webpay/create/route.ts` *(nuevo)* | Crear transacción en el server |
| `app/api/webpay/commit/route.ts` *(nuevo)* | Confirmar transacción |
| `app/checkout/page.tsx` | `handlePay()` → `fetch` al route + POST-redirect |
| `.env.local` | Credenciales Transbank |
| `lib/api.ts` | (opcional) cambiar mock por tu API/CMS real de productos |

## ⚠️ Notas de la maqueta
- Imágenes de producto: **placeholders** de marca. Reemplazar por fotos reales.
- Datos de productos: mock en `data/products.ts`.
- Pago: **simulado**, no se cobra nada.
- Formularios (newsletter, contacto): visuales, sin backend.
