// Validaciones de entrada en el límite de confianza. Sin dependencias.

export function esEmail(v: unknown): boolean {
  return typeof v === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

// Saneo de texto libre: recorta y acota longitud. Devuelve "" si no es string.
export function texto(v: unknown, max = 200): string {
  return typeof v === "string" ? v.trim().slice(0, max) : "";
}

// RUT chileno con dígito verificador (módulo 11). Acepta con o sin puntos/guion.
export function esRut(v: unknown): boolean {
  if (typeof v !== "string") return false;
  const limpio = v.replace(/[.\-\s]/g, "").toUpperCase();
  if (!/^\d{7,8}[0-9K]$/.test(limpio)) return false;
  const cuerpo = limpio.slice(0, -1);
  const dv = limpio.slice(-1);
  let suma = 0;
  let factor = 2;
  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += parseInt(cuerpo[i], 10) * factor;
    factor = factor === 7 ? 2 : factor + 1;
  }
  const resto = 11 - (suma % 11);
  const dvCalc = resto === 11 ? "0" : resto === 10 ? "K" : String(resto);
  return dv === dvCalc;
}

// Entero >= 1 y <= max; null si la entrada no es un número usable.
export function cantidadValida(v: unknown, max = 100000): number | null {
  const n = typeof v === "number" ? v : parseInt(String(v), 10);
  if (!Number.isFinite(n) || n < 1) return null;
  return Math.min(max, Math.floor(n));
}
