# Venta por Mayor — Trade Global Solutions SpA

Portal de venta mayorista B2B para comerciantes. Modelo de negocio: se publican
productos en stock, el comerciante compra y paga por transferencia, se valida el
comprobante, se compra al importador y se gestiona el despacho a todo Chile.

## Estado actual (entregado y funcional)
- **Tienda mayorista** (`Portal Mayorista.html`): login de comerciante, catálogo
  multi-rubro con stock en tiempo real, precios por volumen, mínimo por embalaje
  (caja), carrito/cotización, checkout con datos de transferencia + subida de
  comprobante, y seguimiento de pedido (pago → despacho → entregado).
  Panel de Tweaks para variaciones (color, tipografía, bordes, densidad, hero).
- **Panel admin / back-office** (`Panel Admin.html`): Resumen con KPIs, Pagos por
  validar (ver comprobante → aprobar/rechazar), Pedidos con pipeline, Compras a
  importador (genera OC agrupada por importador), Catálogo & stock con costos/márgenes.
- Tienda ↔ admin enlazados en ambos sentidos.
- Marca: logo en `assets/logo.png` (azul/cyan). Acento por defecto #0e7cc4.
  Fuentes: Plus Jakarta Sans + Space Mono. Todo en español de Chile (CLP).

## Arquitectura
- React 18 + Babel inline. Datos mock en `data.js` y `admin_data.js`.
- Componentes compartidos en `components.jsx` / `admin_components.jsx`.
- Pantallas tienda: `screen_catalog.jsx`, `screen_detail.jsx`, `screen_checkout.jsx`, `screen_orders.jsx`.
- Pantallas admin: `admin_screen_pagos.jsx`, `admin_screen_pedidos.jsx`.
- Estilos: `styles.css` (tienda) + `admin.css` (admin).
- IMPORTANTE: admin usa alias `useStateA`/`useMemoA`/`useRefA` para no colisionar.

## Próximos pasos pendientes (EN EL RADAR — no perder de vista)
1. Cargar datos reales: productos, banco/RUT, importadores, márgenes.
2. Notificaciones por correo al cliente en cada cambio de estado.
3. Exportar la OC en PDF para enviar al importador.
