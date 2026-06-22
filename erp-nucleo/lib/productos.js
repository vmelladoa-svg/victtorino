export async function listarProductos(query) {
  const { rows } = await query(
    `SELECT codigo, descripcion, familia, costo, activo FROM productos ORDER BY codigo`);
  return rows;
}

// Upsert del maestro desde filas ya parseadas (el Excel lo parsea el llamador).
// Salta filas sin codigo o sin descripcion.
export async function importarProductos(query, filas) {
  let importadas = 0, saltadas = 0;
  for (const f of filas) {
    if (!f.codigo || !f.descripcion) { saltadas++; continue; }
    await query(
      `INSERT INTO productos (codigo, descripcion, familia, costo, actualizado)
       VALUES ($1, $2, $3, $4, now())
       ON CONFLICT (codigo) DO UPDATE SET
         descripcion = EXCLUDED.descripcion,
         familia = EXCLUDED.familia,
         costo = EXCLUDED.costo,
         actualizado = now()`,
      [f.codigo, f.descripcion, f.familia ?? null, Math.round(f.costo ?? 0)]);
    importadas++;
  }
  return { importadas, saltadas };
}
