/** Formatea un entero CLP como "$81.990" (locale es-CL). */
export function formatCLP(n: number): string {
  return "$" + n.toLocaleString("es-CL");
}

export const CUOTAS = 12;
// Monto mínimo para ofrecer cuotas sin interés (evita "12 cuotas de $116").
export const MIN_CUOTAS = 30000;

/** Texto "12 cuotas sin interés de $X", o null si el monto es muy bajo. */
export function cuotaText(price: number): string | null {
  if (price < MIN_CUOTAS) return null;
  return `${CUOTAS} cuotas sin interés de ${formatCLP(Math.round(price / CUOTAS))}`;
}
