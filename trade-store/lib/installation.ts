import type { CategoryName, Product } from "./types";

// Servicios de instalación (precios de referencia victtorino). Solo Región Metropolitana.
// Se representan como "productos" para poder sumarlos como línea en el carrito.
export const INSTALLATION_SERVICES: Product[] = [
  { id: "inst-grif-lavamanos", name: "Instalación de Grifería de Lavamanos", price: 28990, priceOriginal: null, lowStock: false, sku: "SERV-GRIF-LM", category: "Accesorios" },
  { id: "inst-grif-ducha", name: "Instalación de Grifería de Ducha", price: 28990, priceOriginal: null, lowStock: false, sku: "SERV-GRIF-DU", category: "Accesorios" },
  { id: "inst-grif-lavaplatos", name: "Instalación de Grifería de Lavaplatos", price: 28990, priceOriginal: null, lowStock: false, sku: "SERV-GRIF-LP", category: "Accesorios" },
  { id: "inst-lavaplatos", name: "Instalación de Lavaplatos Empotrado", price: 54990, priceOriginal: null, lowStock: false, sku: "SERV-LAVA", category: "Accesorios" },
  { id: "inst-espejo", name: "Instalación de Espejo", price: 34990, priceOriginal: null, lowStock: false, sku: "SERV-ESP", category: "Accesorios" },
  { id: "inst-mampara", name: "Instalación de Mámparas para Ducha", price: 89990, priceOriginal: null, lowStock: false, sku: "SERV-MAMP", category: "Accesorios" },
  { id: "inst-bano", name: "Instalación de Accesorio de Baño", price: 28990, priceOriginal: null, lowStock: false, sku: "SERV-BANO", category: "Accesorios" },
  { id: "inst-wc", name: "Instalación de Set Sanitario", price: 52990, priceOriginal: null, lowStock: false, sku: "SERV-WC", category: "Accesorios" },
];

const SERVICE_BY_ID = new Map(INSTALLATION_SERVICES.map((s) => [s.id, s]));

// Categorías (no-grifería) → servicio sugerido.
const BY_CATEGORY: Partial<Record<CategoryName, string>> = {
  "Cocina": "inst-lavaplatos",
  "Espejos": "inst-espejo",
  "Shower & Mamparas": "inst-mampara",
  "Baño": "inst-bano",
  "WC e Inodoros": "inst-wc",
  // "Accesorios" no lleva instalación sugerida (productos muy variados).
};

// Para Grifería: sub-tipo según el nombre del producto.
function griferiaServiceId(name: string): string {
  const n = name.toLowerCase();
  if (/lavaplato|lavacopa|cocina/.test(n)) return "inst-grif-lavaplatos";
  if (/ducha|tina|shower/.test(n)) return "inst-grif-ducha";
  return "inst-grif-lavamanos"; // lavamanos / lavatorio / bidet / por defecto
}

/** Servicio de instalación sugerido para un producto, o null si no aplica. */
export function installationFor(p: Product): Product | null {
  if (p.category === "Grifería") return SERVICE_BY_ID.get(griferiaServiceId(p.name)) ?? null;
  const id = BY_CATEGORY[p.category];
  return id ? SERVICE_BY_ID.get(id) ?? null : null;
}

export const INSTALLATION_NOTE = "Servicio de instalación disponible solo en la Región Metropolitana.";
