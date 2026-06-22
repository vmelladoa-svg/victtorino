// Aplica el esquema a la base activa (Neon si hay ERP_DB_URL). Idempotente.
import { readFileSync } from 'node:fs';
import { exec } from '../lib/db.js';

const schema = readFileSync(new URL('../lib/schema.sql', import.meta.url), 'utf8');
await exec(schema);
console.log('esquema aplicado');
process.exit(0);
