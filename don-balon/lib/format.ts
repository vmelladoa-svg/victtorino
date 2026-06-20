/**
 * Formatea un número como peso chileno (CLP).
 * Sin decimales, separador de miles con punto, signo $.
 * Ej: formatCLP(19990) => "$19.990"
 */
export function formatCLP(value: number): string {
  const rounded = Math.round(value);
  return "$" + rounded.toLocaleString("es-CL");
}

/** Calcula el % de descuento entre precio normal y precio oferta. */
export function discountPct(price: number, compareAt?: number): number | null {
  if (!compareAt || compareAt <= price) return null;
  return Math.round((1 - price / compareAt) * 100);
}
