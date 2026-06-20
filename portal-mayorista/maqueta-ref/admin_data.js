/* ============================================================
   Back-office (admin) — datos mock
   Pedidos con comprobante, costo de importador y márgenes.
   Reusa PRODUCTS / CLP / precioUnit / REGIONES de data.js
   ============================================================ */

// costo unitario que TÚ le pagás al importador (mock: ~60% del precio base)
function costoImportador(prod) {
  return Math.round(prod.tiers[0].precioUnit * 0.6 / 10) * 10;
}

// estados del back-office (pipeline operativo)
const ADM_ESTADOS = [
  { id: "por_validar", label: "Pago por validar", icon: "clock", tone: "amber" },
  { id: "validado", label: "Pago validado", icon: "check", tone: "brand" },
  { id: "comprado", label: "Comprado a importador", icon: "package", tone: "blue" },
  { id: "despachado", label: "En despacho", icon: "truck", tone: "blue" },
  { id: "entregado", label: "Entregado", icon: "shield", tone: "ok" },
];
function admEstado(id) { return ADM_ESTADOS.find((e) => e.id === id); }
function admIndex(id) { return ADM_ESTADOS.findIndex((e) => e.id === id); }

function admLine(id, cajas) {
  const p = PRODUCTS.find((x) => x.id === id);
  const pu = precioUnit(p, cajas);
  const u = cajas * p.embalaje;
  const costo = costoImportador(p);
  return {
    id, name: p.name, sku: p.sku, importador: p.importador,
    cajas, unidades: u, precioUnit: pu, ventaTotal: pu * u,
    costoUnit: costo, costoTotal: costo * u, margen: (pu - costo) * u,
  };
}

function buildOrder(o) {
  o.items = o.itemsRaw.map((r) => admLine(r[0], r[1]));
  o.cajas = o.items.reduce((s, i) => s + i.cajas, 0);
  o.unidades = o.items.reduce((s, i) => s + i.unidades, 0);
  o.subtotal = o.items.reduce((s, i) => s + i.ventaTotal, 0);
  o.total = o.subtotal + o.despacho;
  o.costoTotal = o.items.reduce((s, i) => s + i.costoTotal, 0);
  o.margen = o.subtotal - o.costoTotal;
  o.margenPct = Math.round((o.margen / o.subtotal) * 100);
  return o;
}

const ADM_ORDERS = [
  buildOrder({
    folio: "TGS-851077", fecha: "6 jun 2026", hora: "09:14", estado: "por_validar",
    cliente: { empresa: "Comercial Andes Ltda.", contacto: "María F. Rojas", rut: "76.998.221-4", fono: "+56 9 8765 4321", email: "compras@comercialandes.cl" },
    itemsRaw: [["belleza-01", 3], ["herr-02", 2]],
    despacho: 6000, reg: REGIONES[1], dir: "Av. Brasil 980, Valparaíso",
    comprobante: { archivo: "transf_estado.png", banco: "Banco Estado", monto: null, fecha: "6 jun 2026 · 08:55", ref: "Transferencia recibida" },
  }),
  buildOrder({
    folio: "TGS-851066", fecha: "6 jun 2026", hora: "08:40", estado: "por_validar",
    cliente: { empresa: "Distribuidora El Sol", contacto: "Jorge Pérez", rut: "77.230.110-9", fono: "+56 9 5521 8890", email: "jorge@elsol.cl" },
    itemsRaw: [["tec-02", 5], ["bazar-01", 3]],
    despacho: 9600, reg: REGIONES[0], dir: "San Pablo 3450, Santiago",
    comprobante: { archivo: "comprobante_bci.pdf", banco: "BCI", monto: null, fecha: "6 jun 2026 · 08:31", ref: "Comprobante adjunto" },
  }),
  buildOrder({
    folio: "TGS-850980", fecha: "5 jun 2026", hora: "17:22", estado: "validado",
    cliente: { empresa: "Bazar Norte SpA", contacto: "Camila Soto", rut: "78.001.554-2", fono: "+56 9 4410 2233", email: "camila@bazarnorte.cl" },
    itemsRaw: [["hogar-02", 6], ["bazar-02", 2]],
    despacho: 13600, reg: REGIONES[6], dir: "Av. Argentina 1200, Antofagasta",
    comprobante: { archivo: "transferencia_santander.jpg", banco: "Santander", monto: 0, fecha: "5 jun 2026 · 16:50", ref: "Validado por J. Méndez" },
  }),
  buildOrder({
    folio: "TGS-840192", fecha: "5 jun 2026", hora: "11:05", estado: "comprado",
    cliente: { empresa: "Comercial Andes Ltda.", contacto: "María F. Rojas", rut: "76.998.221-4", fono: "+56 9 8765 4321", email: "compras@comercialandes.cl" },
    itemsRaw: [["tec-01", 6], ["bazar-01", 4]],
    despacho: 12000, reg: REGIONES[4], dir: "Camino a Penco 450, Concepción",
    comprobante: { archivo: "transferencia_bci.pdf", banco: "BCI", monto: 0, fecha: "5 jun 2026 · 10:40", ref: "Validado por J. Méndez" },
    ocImportador: "OC-IMP-2291",
  }),
  buildOrder({
    folio: "TGS-840020", fecha: "4 jun 2026", hora: "14:38", estado: "despachado",
    cliente: { empresa: "MultiHogar Chile", contacto: "Andrés Lillo", rut: "76.554.901-1", fono: "+56 9 7782 1190", email: "andres@multihogar.cl" },
    itemsRaw: [["hogar-01", 5], ["bazar-01", 6]],
    despacho: 13200, reg: REGIONES[3], dir: "Av. San Miguel 233, Talca",
    comprobante: { archivo: "transf_falabella.pdf", banco: "Banco Falabella", monto: 0, fecha: "4 jun 2026 · 14:02", ref: "Validado por J. Méndez" },
    ocImportador: "OC-IMP-2284", transportista: "Starken", tracking: "STK-99381204",
  }),
  buildOrder({
    folio: "TGS-829934", fecha: "2 jun 2026", hora: "10:11", estado: "entregado",
    cliente: { empresa: "Tienda Aurora", contacto: "Paula Vega", rut: "77.882.330-5", fono: "+56 9 6620 4471", email: "paula@aurora.cl" },
    itemsRaw: [["textil-01", 8]],
    despacho: 9600, reg: REGIONES[0], dir: "Gran Avenida 5560, Santiago",
    comprobante: { archivo: "comprobante_santander.jpg", banco: "Santander", monto: 0, fecha: "2 jun 2026 · 09:50", ref: "Validado por J. Méndez" },
    ocImportador: "OC-IMP-2270", transportista: "Bluexpress", tracking: "BX-44120983",
  }),
];

Object.assign(window, {
  costoImportador, ADM_ESTADOS, admEstado, admIndex, admLine, ADM_ORDERS,
});
