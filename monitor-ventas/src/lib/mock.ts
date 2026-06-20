import type { Canal, Comanda, Tipo } from './types'

// ----- DATOS DE PRUEBA -----
// Productos REALES del catálogo en vivo (tradeglobalchile.cl, WooCommerce Store API).
// foto = imagen real del producto. FASE REAL: vendrán directo de la API de cada canal.
const PRODUCTOS: { producto: string; sku: string; foto: string }[] = [
  { producto: 'Lavaplatos Empotrado Simple 100x44 Inoxidable Derecho Plateado', sku: 'ML-MLC1306255938', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_910214-MLC74003851818_012024-O-300x295.webp' },
  { producto: 'Llave Doble Para Lavadora Lavadero Jardín 2 Salidas 3/4', sku: 'ML-MLC1307538393', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_943927-MLC91913413780_092025-O-300x300.jpg' },
  { producto: 'Lavaplatos Empotrado Simple 80x44 Secador Izquierdo', sku: 'ML-MLC1306255939', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_691282-MLC91744053644_092025-O-2-300x300.webp' },
  { producto: 'Llave Monomando Lavaplato Inox Cepillado Plateado', sku: 'ML-MLC1404838803', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_943149-MLA99991170473_112025-O-240x300.jpg' },
  { producto: 'Mezcladora Baño Monocomando Acero Inox Ducha Empotrada', sku: 'ML-MLC3767961162', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_710162-MLA108190225109_032026-O-300x300.webp' },
  { producto: 'Válvula Lateral Para WC Eficiente Y Durable', sku: 'ML-MLC3724867792', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_866374-MLC108817551572_032026-O-300x300.jpg' },
  { producto: 'Llave Monomando Lavatorio Lavamanos Modern Plateado', sku: 'ML-MLC1513791879', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_718660-MLA95980862400_102025-O-300x300.webp' },
  { producto: 'Espejo Rectangular Moderno 3 Luces LED Fría-Cálida Blanco', sku: 'ML-MLC1754361903', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_688714-MLC98392613393_112025-O-300x300.jpg' },
  { producto: 'Kit Para Estanque WC Carga Descarga Y Fijaciones', sku: 'ML-MLC1404819393', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_657004-MLC70602523476_072023-O-300x300.jpg' },
  { producto: 'Grifería Baño Monocomando Lavatorio Cromado Inox', sku: 'ML-MLC1880204983', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_872925-MLA96682091979_102025-O-300x300.jpg' },
  { producto: 'Barra De Seguridad Esquinera 3 Apoyos 90° Acero Inox', sku: 'ML-MLC1293237008', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_650381-MLC91966243996_092025-O-300x192.jpg' },
  { producto: 'Dispensador De Jabón Manual Täumm Pared Blanco 500 Ml', sku: 'ML-MLC1810379138', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_935561-MLA95841037981_102025-O-248x300.jpg' },
  { producto: 'Barra De Soporte Ducha Deslizable 65 Cm Acero Inox', sku: 'ML-MLC1293267551', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_780350-MLC71331161872_082023-O-1-291x300.jpg' },
  { producto: 'Plato Ducha Redondo Acero Inoxidable 20 Cm', sku: 'ML-MLC3794114904', foto: 'https://tradeglobalchile.cl/wp-content/uploads/2026/05/D_801529-MLC108559586956_032026-O-300x218.jpg' },
]

// Precio de lista real por SKU (tradeglobalchile.cl), en CLP.
const PRECIOS: Record<string, number> = {
  'ML-MLC1306255938': 36390, 'ML-MLC1307538393': 27271, 'ML-MLC1306255939': 35990,
  'ML-MLC1404838803': 37406, 'ML-MLC3767961162': 40480, 'ML-MLC3724867792': 6290,
  'ML-MLC1513791879': 27690, 'ML-MLC1754361903': 81990, 'ML-MLC1404819393': 16390,
  'ML-MLC1880204983': 17418, 'ML-MLC1293237008': 46222, 'ML-MLC1810379138': 6090,
  'ML-MLC1293267551': 17890, 'ML-MLC3794114904': 18754,
}

// ML, web y falabella ya son reales (vía /feed) -> fuera del mock. Quedan paris y walmart.
const CANALES: Canal[] = ['paris', 'walmart']

// Cuenta/seller por canal (en qué cuenta cayó la venta o pregunta).
const CUENTAS: Record<Canal, string[]> = {
  mercadolibre: ['C3 · NOVAGRIFERIAS3', 'C2 · VICTTORINOFICIAL2', 'C1 · PREMIUMGRIFERIAS1'],
  falabella: ['Trade Global'],
  paris: ['Trade Global'],
  walmart: ['Trade Global'],
  web: ['tradeglobalchile.cl'],
}

const PREGUNTAS = [
  '¿Tienen stock para despacho inmediato a Santiago?',
  '¿Esta grifería sirve para agua caliente y fría?',
  '¿Hacen factura? Necesito para empresa.',
  '¿Qué garantía tiene el producto?',
  '¿El precio incluye el flexible de conexión?',
  '¿Llega a regiones? ¿Cuánto demora a Concepción?',
  '¿Viene con instructivo de instalación?',
  '¿Es de acero inoxidable real o enchapado?',
]

let seq = 0
const pick = <T,>(a: T[]) => a[Math.floor(Math.random() * a.length)]

function nueva(tipo: Tipo, ingreso: number): Comanda {
  const canal = pick(CANALES)
  const p = pick(PRODUCTOS)
  const base: Comanda = {
    id: `c${++seq}`,
    tipo,
    canal,
    producto: p.producto,
    sku: p.sku,
    foto: p.foto, // foto real del producto
    precio: PRECIOS[p.sku] ?? 0, // precio de lista real
    ingreso,
    cuenta: pick(CUENTAS[canal]), // en qué cuenta/seller cayó (ventas y preguntas)
  }
  if (tipo === 'venta') {
    base.monto = base.precio // la venta = precio del producto
    base.validadoDefontana = Math.random() > 0.35
    base.envio = Math.random() > 0.5 ? 'flex' : 'normal'
    // Límite de despacho: Flex = mismo día (2–6 h); Normal = al día siguiente (20–36 h).
    const horas = base.envio === 'flex' ? 2 + Math.random() * 4 : 20 + Math.random() * 16
    base.despacharAntes = ingreso + horas * 3_600_000
  } else {
    base.pregunta = pick(PREGUNTAS)
  }
  return base
}

// Set inicial ~16 tarjetas con antigüedades variadas para que se vea el envejecimiento.
export function seedInicial(ahora: number): Comanda[] {
  const out: Comanda[] = []
  for (let i = 0; i < 16; i++) {
    const tipo: Tipo = Math.random() > 0.45 ? 'venta' : 'pregunta'
    const edadMin = Math.floor(Math.random() * 9) // 0–8 min atrás
    out.push(nueva(tipo, ahora - edadMin * 60_000))
  }
  // Demo: garantizar estados de plazo visibles desde el arranque.
  const ventas = out.filter((c) => c.tipo === 'venta')
  if (ventas[0]) { ventas[0].envio = 'flex'; ventas[0].despacharAntes = ahora - 20 * 60_000 }  // vencido
  if (ventas[1]) { ventas[1].envio = 'flex'; ventas[1].despacharAntes = ahora + 45 * 60_000 }  // por vencer
  return out
}

// Generador en vivo: una comanda nueva con timestamp "ahora".
export function generarComanda(ahora: number): Comanda {
  const tipo: Tipo = Math.random() > 0.45 ? 'venta' : 'pregunta'
  return nueva(tipo, ahora)
}
