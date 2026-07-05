// Evaluación de clientes (híbrida). El score automático se calcula en vivo desde
// el comportamiento del comerciante; el admin lo ajusta con `scoreAjuste` y puede
// fijar un tier a mano (`tierManual`). Sin dependencias: entra data agregada, sale
// el score y el tier. La lógica de agregación (Prisma) vive en quien lo llama.

export type Tier = "A" | "B" | "C";

// Pesos de cada señal en el score automático (suman 1).
export const PESOS = {
  total: 0.35, // monto total comprado
  pago: 0.3, // cumplimiento de pago (pedidos validados vs rechazados)
  frecuencia: 0.2, // cantidad de pedidos
  antiguedad: 0.15, // tiempo como cliente
} as const;

// Valor de cada señal que "llega a 100". Ajustables a la realidad del negocio.
export const TOPE_TOTAL = 2_000_000; // CLP comprados => 100 pts
export const TOPE_PEDIDOS = 10; // nº de pedidos => 100 pts
export const TOPE_DIAS = 180; // días de antigüedad => 100 pts

// Umbrales de tier sobre el score final (0..100).
export const UMBRAL_A = 75;
export const UMBRAL_B = 50;

export interface DatosEval {
  totalComprado: number; // suma de pedidos con pago confirmado (validado en adelante)
  nPedidos: number; // total de pedidos del comerciante
  nBuenos: number; // pedidos con pago aceptado (validado/oc/despachado/entregado)
  nRechazados: number; // pedidos con pago rechazado
  antiguedadDias: number; // días desde el registro
}

export interface ResultadoEval {
  scoreAuto: number; // 0..100
  componentes: { total: number; pago: number; frecuencia: number; antiguedad: number };
}

const clamp100 = (n: number) => Math.max(0, Math.min(100, n));

// Calcula el score automático (0..100) y el desglose por componente.
export function calcularScoreAuto(d: DatosEval): ResultadoEval {
  const cTotal = clamp100((d.totalComprado / TOPE_TOTAL) * 100);
  // Sin historial de pago => neutral (50): ni premia ni castiga.
  const evaluables = d.nBuenos + d.nRechazados;
  const cPago = evaluables === 0 ? 50 : clamp100((d.nBuenos / evaluables) * 100);
  const cFrecuencia = clamp100((d.nPedidos / TOPE_PEDIDOS) * 100);
  const cAntiguedad = clamp100((d.antiguedadDias / TOPE_DIAS) * 100);

  const scoreAuto = Math.round(
    cTotal * PESOS.total +
      cPago * PESOS.pago +
      cFrecuencia * PESOS.frecuencia +
      cAntiguedad * PESOS.antiguedad
  );

  return {
    scoreAuto,
    componentes: {
      total: Math.round(cTotal),
      pago: Math.round(cPago),
      frecuencia: Math.round(cFrecuencia),
      antiguedad: Math.round(cAntiguedad),
    },
  };
}

// Score final = automático + ajuste manual del admin, acotado a 0..100.
export function scoreFinal(scoreAuto: number, ajuste: number): number {
  return Math.round(clamp100(scoreAuto + ajuste));
}

// Tier derivado del score final.
export function tierDeScore(score: number): Tier {
  if (score >= UMBRAL_A) return "A";
  if (score >= UMBRAL_B) return "B";
  return "C";
}

// Tier efectivo: el manual manda si el admin lo fijó; si no, el derivado del score.
export function tierEfectivo(scoreFinalVal: number, tierManual?: string | null): Tier {
  if (tierManual === "A" || tierManual === "B" || tierManual === "C") return tierManual;
  return tierDeScore(scoreFinalVal);
}

// Beneficio asociado a cada tier (referencia para el admin; el efecto real en
// precios/crédito se define en Fase 3).
export const BENEFICIO_TIER: Record<Tier, string> = {
  A: "Mejores condiciones (precio/crédito preferente)",
  B: "Condiciones estándar",
  C: "Prepago / condiciones básicas",
};
