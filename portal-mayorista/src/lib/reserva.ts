// Lógica de stock/reserva. stock = null significa "sin dato aún" (el scraper de
// AlilaTop todavía no corrió) → no se limita la venta. Cuando el scraper puebla
// stock, las reservas lo respetan.

export function disponible(stock: number | null, reservado: number): number {
  if (stock == null) return Infinity; // sin dato de stock -> sin límite
  return Math.max(0, stock - reservado);
}

export function puedeReservar(stock: number | null, reservado: number, cantidad: number): boolean {
  if (cantidad <= 0) return false;
  return cantidad <= disponible(stock, reservado);
}
