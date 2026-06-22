import { test } from 'node:test';
import assert from 'node:assert/strict';
import { checkKey } from './auth.js';

test('checkKey acepta la clave correcta y rechaza el resto', () => {
  process.env.ERP_KEY = 'secreto123';
  assert.equal(checkKey({ headers: { 'x-erp-key': 'secreto123' } }), true);
  assert.equal(checkKey({ headers: { 'x-erp-key': 'malo' } }), false);
  assert.equal(checkKey({ headers: {} }), false);
});

test('checkKey rechaza si no hay ERP_KEY configurada', () => {
  delete process.env.ERP_KEY;
  assert.equal(checkKey({ headers: { 'x-erp-key': 'lo-que-sea' } }), false);
});
