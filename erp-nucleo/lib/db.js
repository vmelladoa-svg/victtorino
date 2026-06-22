// Driver de DB. Producción: Postgres serverless (Neon) si hay ERP_DB_URL.
// Dev/tests: Postgres en proceso (PGlite, WASM) sin setup externo.
// ponytail: dos implementaciones reales (serverless prod / in-process test),
// no abstracción especulativa; elimina la dependencia externa del loop de dev.
// Ambos drivers exponen lo mismo: query(text, params) -> {rows}, y exec(sql).
import { splitSql } from './sqlsplit.js';

let _query, _exec;

if (process.env.ERP_DB_URL) {
  const { Pool } = await import('@neondatabase/serverless');
  const pool = new Pool({ connectionString: process.env.ERP_DB_URL });
  _query = (text, params) => pool.query(text, params);
  _exec = async (sql) => {
    for (const stmt of splitSql(sql)) {
      await pool.query(stmt);
    }
  };
} else {
  const { PGlite } = await import('@electric-sql/pglite');
  const db = new PGlite(); // en memoria
  _query = (text, params) => db.query(text, params);
  _exec = (sql) => db.exec(sql); // varias sentencias
}

export const query = (text, params) => _query(text, params);
export const exec = (sql) => _exec(sql);
