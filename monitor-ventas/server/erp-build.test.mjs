import { test } from "node:test";
import assert from "node:assert/strict";
import { normalizarWeb, normalizarML, construirVentas } from "./erp-build.mjs";

test("normalizarWeb extrae todas las líneas con sku y cantidad", () => {
  const out = normalizarWeb([{
    id: 12, date_created_gmt: "2026-06-20T10:00:00",
    line_items: [{ sku: "A1", quantity: 2 }, { sku: "B2", quantity: 1 }],
  }]);
  assert.equal(out.length, 1);
  assert.equal(out[0].orderId, "12");
  assert.equal(out[0].confirmada, true);
  assert.deepEqual(out[0].lineas, [{ sku: "A1", qty: 2 }, { sku: "B2", qty: 1 }]);
  assert.ok(out[0].fecha > 0);
});

test("normalizarML marca confirmada solo si status==='paid'", () => {
  const raw = [
    { id: 1, status: "paid", date_created: "2026-06-20T10:00:00.000-04:00", order_items: [{ item: { seller_sku: "A1" }, quantity: 3 }] },
    { id: 2, status: "cancelled", date_created: "2026-06-20T11:00:00.000-04:00", order_items: [{ item: { seller_sku: "C3" }, quantity: 1 }] },
  ];
  const out = normalizarML(raw);
  assert.equal(out[0].confirmada, true);
  assert.equal(out[0].lineas[0].sku, "A1");
  assert.equal(out[0].lineas[0].qty, 3);
  assert.equal(out[1].confirmada, false);
});

const ordenWeb = (orderId, fecha, lineas, confirmada = true) => ({ orderId: String(orderId), fecha, confirmada, lineas });

test("construirVentas: multi-línea genera un movimiento por línea", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(12, 2000, [{ sku: "A1", qty: 2 }, { sku: "B2", qty: 1 }, { sku: "C3", qty: 4 }])],
    canal: "web", codigosConocidos: new Set(["A1", "B2", "C3"]), cursorTs: 1000,
  });
  assert.equal(r.movimientos.length, 3);
  assert.deepEqual(r.movimientos[0], { codigo: "A1", tipo: "venta", cantidad: -2, canal: "web", ref: "12" });
  assert.equal(r.movimientos[2].cantidad, -4);
});

test("construirVentas: no confirmada no genera movimiento", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(1, 2000, [{ sku: "A1", qty: 1 }], false)],
    canal: "web", codigosConocidos: new Set(["A1"]), cursorTs: 1000,
  });
  assert.equal(r.movimientos.length, 0);
});

test("construirVentas: orden anterior o igual al cursor no entra", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(1, 1000, [{ sku: "A1", qty: 1 }]), ordenWeb(2, 999, [{ sku: "A1", qty: 1 }])],
    canal: "web", codigosConocidos: new Set(["A1"]), cursorTs: 1000,
  });
  assert.equal(r.movimientos.length, 0); // 1000 no es > 1000; 999 < 1000
});

test("construirVentas: SKU desconocido va a saltados, no a movimientos", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(7, 2000, [{ sku: "A1", qty: 1 }, { sku: "ZZZ", qty: 9 }])],
    canal: "ml1", codigosConocidos: new Set(["A1"]), cursorTs: 0,
  });
  assert.deepEqual(r.movimientos.map((m) => m.codigo), ["A1"]);
  assert.equal(r.saltados.length, 1);
  assert.equal(r.saltados[0].sku, "ZZZ");
});

test("construirVentas: maxTs es la mayor fecha procesada (avanza el cursor)", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(1, 2000, [{ sku: "A1", qty: 1 }]), ordenWeb(2, 5000, [{ sku: "A1", qty: 1 }])],
    canal: "web", codigosConocidos: new Set(["A1"]), cursorTs: 1000,
  });
  assert.equal(r.maxTs, 5000);
});

test("construirVentas: dos líneas de la misma orden comparten ref", () => {
  const r = construirVentas({
    ordenes: [ordenWeb(99, 2000, [{ sku: "A1", qty: 1 }, { sku: "B2", qty: 1 }])],
    canal: "web", codigosConocidos: new Set(["A1", "B2"]), cursorTs: 0,
  });
  assert.equal(r.movimientos[0].ref, "99");
  assert.equal(r.movimientos[1].ref, "99");
});

test("construirVentas: sin órdenes nuevas, maxTs queda en el cursor", () => {
  const r = construirVentas({ ordenes: [], canal: "web", codigosConocidos: new Set(), cursorTs: 1234 });
  assert.equal(r.maxTs, 1234);
  assert.equal(r.movimientos.length, 0);
});
