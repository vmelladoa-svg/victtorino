# Datos reales — Portal Mayorista (Venta por Mayor)
_Para pasar la maqueta a producción. Llena lo que falte; lo marcado ✅ ya lo tenemos._

## 1. Empresa y pago
- ✅ Razón social: **Trade Global Solutions SpA**
- ✅ RUT: **78.103.712-5**
- ✅ Dirección: **Madame Adriana Bolland 430, La Cisterna, RM — CP 7970000**
- ✅ **Datos bancarios para transferencia** (Scotiabank):
  - Banco: **Scotiabank**
  - Titular: **Trade Global Solutions SpA** · RUT **78.103.712-5**
  - Tipo de cuenta: **Cuenta Corriente**
  - N° de cuenta: **000993556831**
  - Email contacto banco: javier.galvez@comercialsolutions.cl · Ejecutiva: Javiera Barra · Sucursal: Santa Elena
- [ ] **Correo donde llegan los comprobantes** de pago (¿pagos@comercialsolutions.cl? ¿contacto@?)

## 2. Acceso de comerciantes
- [ ] ¿Quién puede comprar mayorista? Criterio de aprobación (¿exigir RUT de empresa / giro comercial?)
- [ ] ¿El precio mayorista se ve **solo logueado**, o también público? (recomendado: solo logueado)
- [ ] ¿Aprobación manual de cada comerciante, o registro automático?

## 3. Catálogo mayorista
_No tiene que ser todo el catálogo: solo lo que quieras vender al por mayor._
- [ ] Lista de productos que entran, por rubro/categoría
- [ ] Por producto: **código interno (SKU)**, nombre, rubro, foto

## 4. Precios, tramos y embalaje (lo más importante)
Por cada producto del mayorista:
- [ ] **Costo de reposición** (para que el admin calcule margen)
- [ ] **Unidad de venta**: ¿caja? ¿cuántas unidades por caja?
- [ ] **Mínimo de compra** (¿por producto o por pedido total?)
- [ ] **Tramos de precio por cantidad** — ej.: 1–5 cajas = $X · 6–20 = $Y · 21+ = $Z

## 5. Stock
- [ ] Fuente del stock real: **Defontana** (¿sincroniza solo o lo cargas manual por ahora?)

## 6. Despacho
- [ ] Regiones a las que despachas
- [ ] **Tarifa por región** (o por peso/volumen) + plazo de entrega
- [ ] Transportistas que usas (para el tracking del pedido)

## 7. Proveedor / Órdenes de Compra
_Para el panel admin "Compras a proveedor → generar OC"._
- ✅ **Proveedor único = AlilaTop.** NO se compra a 1688 directo. La OC se genera para AlilaTop usando el código Alila (ej. 6002803).
- ✅ **AlilaTop tiene stock LOCAL en Chile, ~1 día desde la compra** → lead time = 1 día (cumplimiento rápido, no importación). El link 1688 queda solo como referencia de origen.
- [ ] Datos de contacto/pedido de AlilaTop (cómo se le envía la OC: ¿app, correo, WhatsApp?)

## 8. Reglas comerciales
- [ ] Condición de pago: ¿transferencia adelantada o crédito a X días?
- [ ] ¿Descuento de lanzamiento? ¿Vigencia?
- [ ] Logo en versión **sin recuadro/fondo blanco** (para header limpio)
