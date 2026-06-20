// ============================================================
//  CAPA DE ENVÍO
//  Hoy: MOCK (simula éxito) para poder lanzar la captación ya.
//  Producción: descomentar el bloque BACKEND para POSTear a tu
//  API Express (Node) que inserta en PostgreSQL (tabla `maestros`).
//  Fallback alternativo: Tally / Google Sheets (ver bloque comentado).
// ============================================================

export interface SubmitResult {
  ok: boolean;
  error?: string;
}

// Define este env var en producción, ej: https://api.tradeglobalchile.cl
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "";

const delay = (ms = 700) => new Promise((r) => setTimeout(r, ms));

/** Ficha 1 — captación liviana (lead). Inserta en `maestros` (estado: lead). */
export async function submitCaptacion(data: Record<string, unknown>): Promise<SubmitResult> {
  // ---- BACKEND (producción) -------------------------------------------
  // if (API_BASE) {
  //   const r = await fetch(`${API_BASE}/maestros/captacion`, {
  //     method: "POST",
  //     headers: { "content-type": "application/json" },
  //     body: JSON.stringify(data),
  //   });
  //   return { ok: r.ok, error: r.ok ? undefined : `HTTP ${r.status}` };
  // }
  // ---- FALLBACK Tally / Google Sheets (opcional) ----------------------
  // const r = await fetch("https://script.google.com/macros/s/XXXX/exec", {
  //   method: "POST", body: JSON.stringify(data) });
  // return { ok: r.ok };
  // ---- MOCK (actual) --------------------------------------------------
  await delay();
  console.log("[MOCK] captación maestro:", data);
  return { ok: true };
}

/** Ficha 2 — registro completo (multipart, incluye documentos). */
export async function submitRegistro(formData: FormData): Promise<SubmitResult> {
  // El payload incluye el campo interno `estado: "Pendiente"` (no visible
  // para el maestro) para que el backend lo guarde y el admin lo gestione.
  // ---- BACKEND (producción) -------------------------------------------
  // if (API_BASE) {
  //   const r = await fetch(`${API_BASE}/maestros/registro`, {
  //     method: "POST",
  //     body: formData, // multipart/form-data con los archivos
  //   });
  //   return { ok: r.ok, error: r.ok ? undefined : `HTTP ${r.status}` };
  // }
  // ---- MOCK (actual) --------------------------------------------------
  await delay(900);
  const obj: Record<string, unknown> = {};
  formData.forEach((v, k) => (obj[k] = v instanceof File ? `📎 ${v.name}` : v));
  console.log("[MOCK] registro maestro:", obj);
  return { ok: true };
}
