# Portal Mayorista (Comercial Solutions) — Diseño v1

_Fecha: 2026-06-20 · Estado: aprobado para implementación_

## Objetivo
Portal B2B donde comerciantes aprobados ven precios mayoristas, hacen pedidos, pagan por transferencia (subiendo comprobante) y siguen su estado. Modelo **dropship a pedido**: se vende primero y se compra después al proveedor. Es el canal más rentable porque apalanca el sourcing barato de AlilaTop.

## Decisiones clave
- **Modelo:** dropship puro, sin inventario propio. Todo "a pedido".
- **Proveedor único:** **AlilaTop** (tiene stock local en Chile, ~1 día desde la compra). La OC se genera para AlilaTop usando el código Alila. El link 1688 es solo referencia.
- **Acceso:** auto-registro del comerciante + **aprobación manual del admin** antes de ver precios/comprar.
- **Pagos:** transferencia bancaria (Scotiabank, Cuenta Corriente 000993556831, Trade Global Solutions SpA) + subida de comprobante. Sin pasarela online.
- **Avisos:** WhatsApp (CallMeBot) al admin en: nuevo comerciante por aprobar y nuevo pago por validar.
- **URL:** `comercialsolutions.cl` (raíz). El correo @comercialsolutions.cl convive (registros MX aparte de la web).
- **Catálogo v1:** 117 productos (63 monopolio + 54 oportunidad) cargados desde `mayorista_catalogo.xlsx` por script seed; no editable desde el panel en v1.

## Arquitectura
- **Next.js (App Router) en Vercel** — una sola app sirve tienda (comerciante) y panel (admin), separados por rol.
- **Postgres (Neon)** — datos.
- **Vercel Blob** — comprobantes (imágenes/PDF), URL privada.
- **Auth.js** — login comerciante + admin, claves cifradas (bcrypt).
- **CallMeBot** — avisos WhatsApp (phone 56996953815).

## Modelo de datos (5 tablas)
- **comerciantes**: nombre, email, clave (hash), rut_empresa, giro, telefono, estado (pendiente|aprobado|rechazado), created_at.
- **productos**: codigo_alila, nombre, categoria, costo, precio_t1, precio_t2, precio_t3, unid_caja, min_compra, foto_url, link_1688, activo.
- **pedidos**: comerciante_id, estado (pago_en_validacion|validado|oc_generada|despachado|entregado|rechazado), total, region, direccion, comprobante_url, transportista, tracking, created_at.
- **pedido_items**: pedido_id, producto_id, cantidad, precio_aplicado, subtotal.
- **ocs**: pedido_id, proveedor (AlilaTop), numero_oc, estado, created_at.

### Regla de precio por tramo (camino del dinero)
El precio de cada línea se calcula por la **cantidad de ESE producto**:
- 1–5 u → precio_t1 (×2,5 costo)
- 6–20 u → precio_t2 (×2,2 costo)
- 21+ u → precio_t3 (×2,0 costo)

## Pantallas
### Comerciante
1. Registro / Login (datos de empresa: RUT, giro).
2. "Cuenta en revisión" (si pendiente; no ve precios).
3. Catálogo (grilla con foto, nombre, precios por tramo; buscador + filtro por categoría).
4. Detalle / agregar (cantidad → precio del tramo).
5. Carrito / cotización.
6. Checkout (región + dirección → datos de transferencia → subir comprobante).
7. Mis pedidos (estado + seguimiento).

### Admin
1. Comerciantes (aprobar / rechazar pendientes).
2. Pagos por validar (ver comprobante → aprobar / rechazar).
3. Pedidos (lista + estado).
4. Generar OC (desde pedido validado → OC AlilaTop).
5. Despacho (marcar despachado con transportista + tracking → entregado).

## Flujo
1. Comerciante arma pedido → checkout → sube comprobante → estado **pago_en_validacion** → WhatsApp al admin.
2. Admin valida pago → **validado**.
3. Admin genera OC (compra a AlilaTop, llega ~1 día) → **oc_generada**.
4. Admin marca despachado (transportista + tracking) → **despachado** (el comerciante lo ve).
5. Entregado → **entregado**.

## Seguridad
- Auth.js + bcrypt. Dos roles (comerciante, admin); panel admin solo con rol admin.
- Precios visibles solo a comerciante **aprobado**; sin login no se ve nada.
- Comprobantes con URL privada en Blob. HTTPS por defecto.

## Errores
- Validación de formularios (RUT, email, obligatorios).
- Comprobante: solo imágenes/PDF, límite de tamaño, mensaje claro si falla.
- Transiciones de estado controladas (no generar OC de pedido no validado, etc.).
- Si CallMeBot falla, el pedido igual se guarda (aviso no bloquea la venta).

## Pruebas
- Test de la regla de precios por tramo (obligatorio).
- Test del flujo de estados del pedido (no saltar pasos).
- Resto se verifica a mano al desplegar.

## Fuera de alcance (v2)
Dashboard de KPIs / reportes · exportar OC a PDF · avisos por correo · editar catálogo desde el panel · multi-usuario admin · agrupar varios pedidos en una OC.

## Dependencias / pendientes externos
- **Restaurar `comercialsolutions.cl`** en nic.cl antes del 10-07-2026 (vencido) — bloquea el deploy final.
- Datos de despacho (regiones + tarifas), unid×caja y mín. compra por producto, datos de contacto de AlilaTop para enviar la OC, correo para comprobantes. (Ver `MAYORISTA_DATOS_REALES.md`.)
