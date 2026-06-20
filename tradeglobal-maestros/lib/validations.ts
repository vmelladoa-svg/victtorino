// ====== Validaciones (Chile) ======

export const cleanRut = (rut: string) => rut.replace(/[^0-9kK]/g, "").toUpperCase();

/** Valida RUT chileno con dígito verificador (módulo 11). */
export function validateRut(rut: string): boolean {
  const c = cleanRut(rut);
  if (c.length < 2) return false;
  const body = c.slice(0, -1);
  const dv = c.slice(-1);
  if (!/^\d+$/.test(body)) return false;
  let sum = 0;
  let mul = 2;
  for (let i = body.length - 1; i >= 0; i--) {
    sum += parseInt(body[i], 10) * mul;
    mul = mul === 7 ? 2 : mul + 1;
  }
  const res = 11 - (sum % 11);
  const dvCalc = res === 11 ? "0" : res === 10 ? "K" : String(res);
  return dv === dvCalc;
}

/** Formatea "123456789" -> "12.345.678-9" */
export function formatRut(rut: string): string {
  const c = cleanRut(rut);
  if (c.length < 2) return rut;
  const body = c.slice(0, -1);
  const dv = c.slice(-1);
  return body.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + "-" + dv;
}

export const cleanPhone = (p: string) => p.replace(/\D/g, "");

/** Valida celular chileno: 9 XXXX XXXX (9 dígitos) o con prefijo 56. */
export function validatePhone(p: string): boolean {
  const c = cleanPhone(p);
  if (c.length === 9) return /^9\d{8}$/.test(c);
  if (c.length === 11) return /^569\d{8}$/.test(c);
  return false;
}

/** Devuelve el teléfono en formato +56 9 XXXX XXXX. */
export function formatPhone(p: string): string {
  let c = cleanPhone(p);
  if (c.length === 11 && c.startsWith("56")) c = c.slice(2);
  if (c.length !== 9) return p;
  return `+56 ${c[0]} ${c.slice(1, 5)} ${c.slice(5)}`;
}

export const validateEmail = (e: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.trim());
