// Stock vivo = SUM(cantidad) sobre el libro. LEFT JOIN para incluir productos
// sin movimientos (stock 0).
// ponytail: GROUP BY directo; a cientos de SKU es instantáneo. Cachear solo si crece.
export async function stockVivo(query) {
  const { rows } = await query(
    `SELECT p.codigo, p.descripcion, p.costo,
            COALESCE(SUM(m.cantidad), 0)::int AS stock,
            (COALESCE(SUM(m.cantidad), 0) * p.costo)::int AS valor
     FROM productos p
     LEFT JOIN movimientos m ON m.codigo = p.codigo
     GROUP BY p.codigo, p.descripcion, p.costo
     ORDER BY p.codigo`);
  return rows;
}

export async function stockDe(query, codigo) {
  const { rows } = await query(
    `SELECT COALESCE(SUM(cantidad), 0)::int AS stock FROM movimientos WHERE codigo = $1`,
    [codigo]);
  return rows[0].stock;
}
