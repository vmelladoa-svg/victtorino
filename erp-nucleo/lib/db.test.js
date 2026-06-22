import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import { query } from './db.js';
import { resetDb } from './test-helpers.js';

before(async () => { await resetDb(); });

test('las 3 tablas existen tras resetDb', async () => {
  const { rows } = await query(
    `SELECT table_name FROM information_schema.tables
     WHERE table_schema = 'public' ORDER BY table_name`);
  const nombres = rows.map((r) => r.table_name);
  assert.ok(nombres.includes('productos'));
  assert.ok(nombres.includes('movimientos'));
  assert.ok(nombres.includes('canal_map'));
});
