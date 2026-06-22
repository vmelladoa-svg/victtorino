import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';
import { stockVivo, stockDe } from './stock.js';

beforeEach(async () => {
  await resetDb();
  await query(`INSERT INTO productos (codigo, descripcion, costo) VALUES ('A1','Llave',1000)`);
  await query(`INSERT INTO movimientos (codigo, tipo, cantidad, canal, ref) VALUES
    ('A1','saldo_inicial',100,'inventario','toma-1'),
    ('A1','venta',-5,'ml1','orden-9'),
    ('A1','compra',20,'proveedor','oc-3')`);
});

test('stockDe suma el libro: 100 - 5 + 20 = 115', async () => {
  assert.equal(await stockDe(query, 'A1'), 115);
});

test('stockVivo devuelve stock y valor por SKU', async () => {
  const filas = await stockVivo(query);
  const a1 = filas.find((f) => f.codigo === 'A1');
  assert.equal(a1.stock, 115);
  assert.equal(a1.valor, 115000); // 115 * 1000
});

test('stockVivo incluye productos sin movimientos con stock 0', async () => {
  await query(`INSERT INTO productos (codigo, descripcion, costo) VALUES ('B2','Codo',500)`);
  const filas = await stockVivo(query);
  const b2 = filas.find((f) => f.codigo === 'B2');
  assert.equal(b2.stock, 0);
  assert.equal(b2.valor, 0);
});
