export type TramoPrecio = { precioT1: number | null; precioT2: number | null; precioT3: number | null };

export function precioPorCantidad(p: TramoPrecio, cantidad: number): number {
  if (cantidad >= 21 && p.precioT3 != null) return p.precioT3;
  if (cantidad >= 6 && p.precioT2 != null) return p.precioT2;
  if (p.precioT1 != null) return p.precioT1;
  throw new Error("Producto sin precio");
}
export function subtotalLinea(p: TramoPrecio, cantidad: number): number {
  return precioPorCantidad(p, cantidad) * cantidad;
}
