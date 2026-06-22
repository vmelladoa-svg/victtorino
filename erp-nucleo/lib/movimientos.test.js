import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';
import { insertarMovimientos } from './movimientos.js';
import { stockDe } from './stock.js';

beforeEach(async () => {
  await resetDb();
  await query(`INSERT INTO productos (codigo, descripcion, costo) VALUES ('A1','Llave',1000)`);
});

test('inserta movimientos y el stock refleja la suma', async () => {
  const r = await insertarMovimientos(query, [
    { codigo: 'A1', tipo: 'saldo_inicial', cantidad: 50, canal: 'inventario', ref: 'toma-1' },
    { codigo: 'A1', tipo: 'venta', cantidad: -8, canal: 'ml1', ref: 'orden-1' },
  ]);
  assert.equal(r.insertados, 2);
  assert.equal(await stockDe(query, 'A1'), 42);
});

test('idempotencia: reinsertar misma (canal, ref, codigo) no duplica', async () => {
  const venta = [{ codigo: 'A1', tipo: 'venta', cantidad: -3, canal: 'web', ref: 'pedido-77' }];
  await insertarMovimientos(query, venta);
  const r2 = await insertarMovimientos(query, venta);
  assert.equal(r2.insertados, 0);
  assert.equal(r2.duplicados, 1);
  assert.equal(await stockDe(query, 'A1'), -3); // no -6
});

test('codigo inexistente lanza error 400', async () => {
  await assert.rejects(
    () => insertarMovimientos(query, [{ codigo: 'NOPE', tipo: 'ajuste', cantidad: 1 }]),
    (e) => { assert.equal(e.status, 400); return true; });
});
