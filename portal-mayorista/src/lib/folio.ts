// Folio visible del pedido: primeros 8 chars del cuid, en mayúsculas.
// Único criterio en TODA la app (comerciante y admin) para que coincida.
export const folio = (id: string) => id.slice(0, 8).toUpperCase();
