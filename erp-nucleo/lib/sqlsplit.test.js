import { test } from 'node:test';
import assert from 'node:assert/strict';
import { splitSql } from './sqlsplit.js';

test('splitSql separa, recorta y descarta vacíos', () => {
  const out = splitSql('CREATE TABLE a (x int);\n  DROP TABLE a;\n;');
  assert.deepEqual(out, ['CREATE TABLE a (x int)', 'DROP TABLE a']);
});
