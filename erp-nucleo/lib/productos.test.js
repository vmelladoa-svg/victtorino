import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';
import { listarProductos, importarProductos } from './productos.js';

beforeEach(async () => { await resetDb(); });

test('importar inserta filas válidas y salta las incompletas', async () => {
  const r = await importarProductos(query, [
    { codigo: 'A1', descripcion: 'Llave', familia: 'Griferías', costo: 1000 },
    { codigo: '', descripcion: 'sin codigo' },          // saltada
    { codigo: 'B2', descripcion: '' },                   // saltada
    { codigo: 'C3', descripcion: 'Codo', costo: 500 },
  ]);
  assert.equal(r.importadas, 2);
  assert.equal(r.saltadas, 2);
  const lista = await listarProductos(query);
  assert.equal(lista.length, 2);
});

test('importar hace upsert: re-importar el mismo codigo actualiza, no duplica', async () => {
  await importarProductos(query, [{ codigo: 'A1', descripcion: 'Llave', costo: 1000 }]);
  await importarProductos(query, [{ codigo: 'A1', descripcion: 'Llave Cromada', costo: 1200 }]);
  const lista = await listarProductos(query);
  assert.equal(lista.length, 1);
  assert.equal(lista[0].descripcion, 'Llave Cromada');
  assert.equal(lista[0].costo, 1200);
});
