export const formatCLP = (n: number) => "$" + Math.round(n || 0).toLocaleString("es-CL");

/** "YYYY-MM" desde una fecha ISO (YYYY-MM-DD). */
export const monthKey = (iso: string) => iso.slice(0, 7);

const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
const MESES_LARGO = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

export const monthLabel = (key: string) => {
  const [y, m] = key.split("-");
  return `${MESES[+m - 1]} ${y}`;
};
export const monthLabelLong = (key: string) => {
  const [y, m] = key.split("-");
  return `${MESES_LARGO[+m - 1]} ${y}`;
};

export const todayISO = () => {
  const d = new Date();
  const off = d.getTimezoneOffset();
  return new Date(d.getTime() - off * 60000).toISOString().slice(0, 10);
};

export const fmtFecha = (iso: string) => {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
};

/** Lista de meses (keys) presentes en los datos, descendente, incluyendo el actual. */
export const prevMonthKey = (key: string) => {
  const [y, m] = key.split("-").map(Number);
  const d = new Date(y, m - 2, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
};
