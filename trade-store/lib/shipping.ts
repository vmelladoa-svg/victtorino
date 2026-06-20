// Zonas de despacho (tarifas fijas, réplica de la config WooCommerce — decisión A.1).
// Envío gratis sobre el monto indicado por zona. Retiro en bodega siempre gratis.
export interface Zone {
  id: string;
  name: string;
  cost: number;
  eta: string;
  /** Monto del subtotal (ya con descuento) sobre el cual el despacho es gratis. */
  freeMin?: number;
}

export const ZONES: Zone[] = [
  { id: "rm", name: "Región Metropolitana", cost: 2490, eta: "24 horas hábiles", freeMin: 50000 },
  { id: "centro", name: "Zona Centro (Valparaíso y O'Higgins)", cost: 3490, eta: "1–2 días hábiles", freeMin: 60000 },
  { id: "regiones", name: "Regiones (resto de Chile)", cost: 4990, eta: "2–3 días hábiles", freeMin: 60000 },
  { id: "retiro", name: "Retiro en bodega", cost: 0, eta: "Coordinamos por WhatsApp" },
];

export const DEFAULT_ZONE = "rm";

export function zoneById(id: string): Zone {
  return ZONES.find((z) => z.id === id) ?? ZONES[0];
}

/** Costo de despacho para una zona dado el subtotal (ya con descuento). */
export function shippingFor(zoneId: string, afterDiscount: number): number {
  const z = zoneById(zoneId);
  if (z.cost === 0) return 0; // retiro en bodega
  if (z.freeMin && afterDiscount >= z.freeMin) return 0; // envío gratis por monto
  return z.cost;
}
