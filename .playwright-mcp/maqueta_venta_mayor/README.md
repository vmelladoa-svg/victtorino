# Trade Global Solutions — Código fuente (Venta por Mayor)

Paquete con TODO el código actual del prototipo, tal cual está. Sirve como base
para migrar a un proyecto Next.js real. **No se modificó el diseño ni la estética.**

## Qué incluye

### Tienda mayorista
- `Portal Mayorista.html` — punto de entrada (carga los scripts)
- `app.jsx` — routing + estado (carrito, pedidos, sesión)
- `screen_catalog.jsx` — header, login, catálogo, tarjeta de producto
- `screen_detail.jsx` — detalle de producto (precios por volumen)
- `screen_checkout.jsx` — carrito, checkout, transferencia + comprobante
- `screen_orders.jsx` — seguimiento de pedidos (timeline)
- `components.jsx` — componentes compartidos (iconos, botones, badges, stepper)
- `data.js` — datos mock del catálogo (productos, regiones, banco)
- `styles.css` — estilos de la tienda
- `tweaks-panel.jsx` — panel de variaciones (solo prototipo)

### Panel admin / back-office
- `Panel Admin.html` — punto de entrada del admin
- `admin_app.jsx` — routing + estado del admin
- `admin_components.jsx` — sidebar, topbar, KPIs, pipeline, modal
- `admin_screen_pagos.jsx` — Resumen (dashboard) + Pagos por validar
- `admin_screen_pedidos.jsx` — Pedidos, Compras a importador (OC), Catálogo & stock
- `admin_data.js` — datos mock del back-office
- `admin.css` — estilos del admin

### Marca
- `assets/logo.png` — logo (azul/cyan)

## Stack actual
- React 18 + Babel **inline** (se transpila en el navegador, sin build).
- Cada `<script type="text/babel">` se ejecuta en scope global; los componentes
  se exponen vía `Object.assign(window, {...})` al final de cada archivo.
- El admin usa alias `useStateA` / `useMemoA` / `useRefA` para no colisionar
  con la tienda (definidos en `admin_components.jsx`).
- Datos 100% mock en memoria — se reinician al recargar (no hay base de datos).

## Cómo abrirlo tal cual (sin migrar)
Abrí `Portal Mayorista.html` o `Panel Admin.html` en el navegador.
(Idealmente con un servidor estático local para evitar restricciones de archivos,
ej. `npx serve` en esta carpeta.)

---

## Notas para migrar a Next.js (App Router)

Esto es una guía orientativa para el desarrollador. El objetivo es reusar el
diseño y los componentes, reemplazando los datos mock por datos reales.

1. **Crear el proyecto**
   `npx create-next-app@latest` (con React 18+, TypeScript opcional).

2. **Componentes → archivos reales**
   - Cada `*.jsx` de acá pasa a un componente en `components/` o a rutas en `app/`.
   - Quitar los `Object.assign(window, {...})` y reemplazar por `export`/`import`.
   - Quitar Babel inline y los `<script>` de los HTML: Next compila los JSX.
   - Las pantallas con estado (carrito, login) → componentes cliente (`"use client"`).

3. **Estilos**
   - `styles.css` y `admin.css` se pueden importar tal cual (CSS global) o pasar
     a CSS Modules. Las variables CSS (`--brand`, etc.) se mantienen igual.

4. **Datos mock → base de datos**
   - `data.js` y `admin_data.js` describen el modelo (productos, pedidos, regiones,
     banco, importadores). Usarlos como referencia del esquema.
   - Reemplazar por una DB (Postgres/MySQL) + una capa de acceso (Prisma, etc.).

5. **Rutas sugeridas**
   - Tienda: `/login`, `/catalogo`, `/producto/[id]`, `/carrito`, `/checkout`, `/pedidos`
   - Admin: `/admin`, `/admin/pagos`, `/admin/pedidos`, `/admin/compras`, `/admin/catalogo`

6. **Pendientes de backend (los "puntos" del proyecto)**
   - Login real + cuentas de comerciante.
   - Subida real del comprobante (storage) y validación.
   - Notificaciones por correo en cada cambio de estado.
   - Exportar la OC del importador en PDF.

> Importante: este paquete es el **diseño y la lógica de UI** ya resuelta. La parte
> de servidor (base de datos, auth, correos, pagos) es la que falta construir.
