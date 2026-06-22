// Inserta movimientos al libro. Valida que el producto exista (no crear
// fantasmas desde el libro). Idempotente por (canal, ref, codigo).
export async function insertarMovimientos(query, movs) {
  const res = { insertados: 0, duplicados: 0 };
  for (const m of movs) {
    const existe = await query('SELECT 1 FROM productos WHERE codigo = $1', [m.codigo]);
    if (existe.rows.length === 0) {
      const e = new Error(`codigo desconocido: ${m.codigo}`);
      e.status = 400;
      throw e;
    }
    // RETURNING id + rows.length: funciona igual en pg (Neon) y PGlite,
    // sin depender de rowCount/affectedRows (difieren entre drivers).
    const r = await query(
      `INSERT INTO movimientos (codigo, tipo, cantidad, canal, ref)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (canal, ref, codigo) DO NOTHING
       RETURNING id`,
      [m.codigo, m.tipo, m.cantidad, m.canal ?? null, m.ref ?? null]);
    if (r.rows.length === 1) res.insertados++;
    else res.duplicados++;
  }
  return res;
}
