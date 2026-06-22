// Resetea el esquema en la base activa (PGlite en tests). exec() admite varias
// sentencias, así corremos drops + schema completo de una.
import { readFileSync } from 'node:fs';
import { exec } from './db.js';

const schema = readFileSync(new URL('./schema.sql', import.meta.url), 'utf8');

export async function resetDb() {
  await exec('DROP TABLE IF EXISTS movimientos CASCADE; DROP TABLE IF EXISTS canal_map CASCADE; DROP TABLE IF EXISTS productos CASCADE;');
  await exec(schema);
}
