// erp-build.mjs — Lógica pura de la ingesta de ventas al núcleo. Sin I/O.
// Forma común "Orden": { orderId, fecha(ms), confirmada, lineas: [{sku, qty}] }.

// WooCommerce crudo -> Orden[]. El query ya filtra a confirmadas, así que confirmada=true.
export function normalizarWeb(rawOrders) {
  return (rawOrders || []).map((o) => ({
    orderId: String(o.id),
    fecha: Date.parse((o.date_created_gmt ? o.date_created_gmt + "Z" : o.date_created)) || 0,
    confirmada: true,
    lineas: (o.line_items || []).map((li) => ({ sku: String(li.sku || ""), qty: Number(li.quantity || 0) })),
  }));
}

// Mercado Libre crudo -> Orden[]. confirmada solo si status==='paid'.
export function normalizarML(rawOrders) {
  return (rawOrders || []).map((o) => ({
    orderId: String(o.id),
    fecha: Date.parse(o.date_created) || 0,
    confirmada: o.status === "paid",
    lineas: (o.order_items || []).map((oi) => ({ sku: String(oi.item?.seller_sku || ""), qty: Number(oi.quantity || 0) })),
  }));
}

// Arma los movimientos de venta para el núcleo. Solo órdenes confirmadas y con
// fecha > cursorTs. Cada línea con SKU conocido -> movimiento; si no -> saltados.
export function construirVentas({ ordenes, canal, codigosConocidos, cursorTs }) {
  const movimientos = [];
  const saltados = [];
  let maxTs = cursorTs;
  for (const o of ordenes || []) {
    if (!o.confirmada) continue;
    if (!(o.fecha > cursorTs)) continue;
    if (o.fecha > maxTs) maxTs = o.fecha;
    for (const l of o.lineas || []) {
      if (!(l.qty > 0)) continue;
      if (l.sku && codigosConocidos.has(l.sku)) {
        movimientos.push({ codigo: l.sku, tipo: "venta", cantidad: -l.qty, canal, ref: o.orderId });
      } else {
        saltados.push({ canal, orderId: o.orderId, sku: l.sku, qty: l.qty });
      }
    }
  }
  return { movimientos, saltados, maxTs };
}
