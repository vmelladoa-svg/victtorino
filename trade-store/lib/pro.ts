// Programa Trade Pro — niveles por compras acumuladas en período de 3 meses.
export interface ProTier {
  id: string;
  name: string;
  color: string;
  pct: number;
  min: number;
  perks: string[];
}

export const PRO_TIERS: ProTier[] = [
  {
    id: "cobre",
    name: "Pro Cobre",
    color: "#C98A5B",
    pct: 5,
    min: 0,
    perks: [
      "5% de descuento en todo el catálogo",
      "Atención preferente por WhatsApp",
      "Acceso a preventa de productos nuevos",
    ],
  },
  {
    id: "plata",
    name: "Pro Plata",
    color: "#B9C4D0",
    pct: 10,
    min: 400000,
    perks: [
      "10% de descuento en todo el catálogo",
      "Despacho prioritario en RM",
      "Cotizaciones por volumen en 24 h",
    ],
  },
  {
    id: "oro",
    name: "Pro Oro",
    color: "#E3B341",
    pct: 15,
    min: 900000,
    perks: [
      "15% de descuento en todo el catálogo",
      "Despacho prioritario a todo Chile",
      "Ejecutivo asignado y crédito a 30 días",
    ],
  },
];

export function tierForSpend(spend: number): ProTier {
  let tier = PRO_TIERS[0];
  for (const t of PRO_TIERS) if (spend >= t.min) tier = t;
  return tier;
}

export function nextTier(spend: number): ProTier | null {
  return PRO_TIERS.find((t) => spend < t.min) || null;
}

export interface ProAccount {
  name: string;
  rut: string;
  telefono: string;
  rubro: string;
  spend: number;
}
