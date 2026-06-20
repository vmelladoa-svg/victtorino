/* ============================================================
   Trade Global Solutions — datos mock del catálogo mayorista
   CLP, precios por volumen, stock en tiempo real, mínimo por embalaje
   ============================================================ */

const CLP = (n) =>
  "$" + Math.round(n).toLocaleString("es-CL", { maximumFractionDigits: 0 });

// Categorías (rubros) — multi-rubro
const CATEGORIES = [
  { id: "all", label: "Todo el catálogo", icon: "grid" },
  { id: "tec", label: "Tecnología", icon: "chip" },
  { id: "hogar", label: "Hogar", icon: "home" },
  { id: "belleza", label: "Belleza", icon: "drop" },
  { id: "bazar", label: "Bazar", icon: "box" },
  { id: "herr", label: "Herramientas", icon: "tool" },
  { id: "textil", label: "Textil", icon: "shirt" },
];

// Cada producto:
//  embalaje  = unidades por caja (el mínimo de compra y el "paso" del stepper)
//  stock     = unidades disponibles (en tiempo real, las descuenta el carrito)
//  tiers     = precio unitario por tramo de cajas [{ minCajas, precioUnit }]
//  importador= a quién se le compra al generar la venta
const PRODUCTS = [
  {
    id: "tec-01",
    name: "Audífonos Bluetooth TWS Pro",
    sku: "TGS-AUD-4521",
    cat: "tec",
    tint: "#1e6fa8",
    embalaje: 20,
    stock: 640,
    importador: "Shenzhen Aiyu Import",
    tiers: [
      { minCajas: 1, precioUnit: 7990 },
      { minCajas: 5, precioUnit: 7290 },
      { minCajas: 15, precioUnit: 6590 },
    ],
    tags: ["Más vendido"],
    desc: "Audífonos inalámbricos con estuche de carga, BT 5.3 y cancelación de ruido ambiente. Caja master de 20 unidades.",
  },
  {
    id: "tec-02",
    name: "Cargador Carga Rápida 33W USB-C",
    sku: "TGS-CRG-1180",
    cat: "tec",
    tint: "#1d8fc0",
    embalaje: 40,
    stock: 1200,
    importador: "Shenzhen Aiyu Import",
    tiers: [
      { minCajas: 1, precioUnit: 3490 },
      { minCajas: 6, precioUnit: 3090 },
      { minCajas: 20, precioUnit: 2790 },
    ],
    tags: [],
    desc: "Cabezal de carga rápida GaN, compatible PD/QC. Embalaje de 40 unidades con caja de exhibición.",
  },
  {
    id: "tec-03",
    name: "Smartwatch Serie 9 Multideporte",
    sku: "TGS-SMW-7732",
    cat: "tec",
    tint: "#1a5b96",
    embalaje: 10,
    stock: 180,
    importador: "Guangzhou Lemon Trade",
    tiers: [
      { minCajas: 1, precioUnit: 12990 },
      { minCajas: 4, precioUnit: 11790 },
      { minCajas: 12, precioUnit: 10490 },
    ],
    tags: ["Nuevo"],
    desc: "Reloj inteligente con medición de ritmo cardíaco, llamadas BT y 8 esferas. Embalaje de 10 unidades.",
  },
  {
    id: "hogar-01",
    name: "Set Organizadores Apilables x3",
    sku: "TGS-ORG-3390",
    cat: "hogar",
    tint: "#2486b8",
    embalaje: 24,
    stock: 96,
    importador: "Yiwu Home Goods Co.",
    tiers: [
      { minCajas: 1, precioUnit: 4290 },
      { minCajas: 5, precioUnit: 3890 },
      { minCajas: 15, precioUnit: 3490 },
    ],
    tags: [],
    desc: "Set de 3 cajas organizadoras apilables con tapa. Plástico reforzado. Embalaje de 24 sets.",
  },
  {
    id: "hogar-02",
    name: "Lámpara LED de Escritorio Regulable",
    sku: "TGS-LMP-5521",
    cat: "hogar",
    tint: "#1e6fa8",
    embalaje: 16,
    stock: 256,
    importador: "Yiwu Home Goods Co.",
    tiers: [
      { minCajas: 1, precioUnit: 6990 },
      { minCajas: 5, precioUnit: 6390 },
      { minCajas: 15, precioUnit: 5790 },
    ],
    tags: ["Más vendido"],
    desc: "Lámpara con 3 temperaturas de color y carga USB. Brazo flexible. Embalaje de 16 unidades.",
  },
  {
    id: "belleza-01",
    name: "Serum Facial Vitamina C 30ml",
    sku: "TGS-SER-2204",
    cat: "belleza",
    tint: "#1d8fc0",
    embalaje: 48,
    stock: 1440,
    importador: "Seoul Beauty Lab",
    tiers: [
      { minCajas: 1, precioUnit: 2990 },
      { minCajas: 6, precioUnit: 2690 },
      { minCajas: 20, precioUnit: 2390 },
    ],
    tags: ["Nuevo"],
    desc: "Serum con vitamina C estabilizada y ácido hialurónico. Frasco gotario 30ml. Embalaje de 48 unidades.",
  },
  {
    id: "belleza-02",
    name: "Set Brochas Maquillaje x12",
    sku: "TGS-BRC-8841",
    cat: "belleza",
    tint: "#1a5b96",
    embalaje: 30,
    stock: 60,
    importador: "Seoul Beauty Lab",
    tiers: [
      { minCajas: 1, precioUnit: 5490 },
      { minCajas: 4, precioUnit: 4990 },
      { minCajas: 12, precioUnit: 4490 },
    ],
    tags: [],
    desc: "Set profesional de 12 brochas con estuche. Cerda sintética. Embalaje de 30 sets.",
  },
  {
    id: "bazar-01",
    name: "Botella Térmica Acero 750ml",
    sku: "TGS-BOT-6610",
    cat: "bazar",
    tint: "#2486b8",
    embalaje: 36,
    stock: 720,
    importador: "Ningbo Daily Export",
    tiers: [
      { minCajas: 1, precioUnit: 4790 },
      { minCajas: 6, precioUnit: 4290 },
      { minCajas: 18, precioUnit: 3790 },
    ],
    tags: ["Más vendido"],
    desc: "Botella de acero inoxidable doble pared, mantiene 12h frío / 6h calor. Embalaje de 36 unidades.",
  },
  {
    id: "bazar-02",
    name: "Juego de Cubiertos Acero x24",
    sku: "TGS-CUB-1029",
    cat: "bazar",
    tint: "#1e6fa8",
    embalaje: 20,
    stock: 0,
    importador: "Ningbo Daily Export",
    tiers: [
      { minCajas: 1, precioUnit: 8990 },
      { minCajas: 5, precioUnit: 8190 },
      { minCajas: 15, precioUnit: 7390 },
    ],
    tags: [],
    desc: "Set de 24 piezas de acero inoxidable pulido, para 6 personas. Embalaje de 20 sets.",
  },
  {
    id: "herr-01",
    name: "Taladro Percutor Inalámbrico 21V",
    sku: "TGS-TAL-4407",
    cat: "herr",
    tint: "#1d8fc0",
    embalaje: 8,
    stock: 64,
    importador: "Jinhua Tools Manufacturing",
    tiers: [
      { minCajas: 1, precioUnit: 19990 },
      { minCajas: 3, precioUnit: 18490 },
      { minCajas: 10, precioUnit: 16990 },
    ],
    tags: ["Nuevo"],
    desc: "Taladro con 2 baterías de litio, maletín y set de 12 brocas. Embalaje de 8 unidades.",
  },
  {
    id: "herr-02",
    name: "Set Destornilladores Precisión x32",
    sku: "TGS-DES-7781",
    cat: "herr",
    tint: "#1a5b96",
    embalaje: 25,
    stock: 375,
    importador: "Jinhua Tools Manufacturing",
    tiers: [
      { minCajas: 1, precioUnit: 5990 },
      { minCajas: 5, precioUnit: 5390 },
      { minCajas: 15, precioUnit: 4790 },
    ],
    tags: [],
    desc: "Kit de 32 puntas magnéticas para electrónica con mango ergonómico. Embalaje de 25 sets.",
  },
  {
    id: "textil-01",
    name: "Polera Algodón Premium (pack colores)",
    sku: "TGS-POL-3318",
    cat: "textil",
    tint: "#2486b8",
    embalaje: 50,
    stock: 1500,
    importador: "Dhaka Textile Group",
    tiers: [
      { minCajas: 1, precioUnit: 3290 },
      { minCajas: 6, precioUnit: 2890 },
      { minCajas: 20, precioUnit: 2490 },
    ],
    tags: ["Más vendido"],
    desc: "Polera 100% algodón peinado 180g, tallas surtidas S–XL. Embalaje de 50 unidades.",
  },
  {
    id: "textil-02",
    name: "Calcetines Deportivos (pack x6)",
    sku: "TGS-CAL-9920",
    cat: "textil",
    tint: "#1e6fa8",
    embalaje: 60,
    stock: 240,
    importador: "Dhaka Textile Group",
    tiers: [
      { minCajas: 1, precioUnit: 1990 },
      { minCajas: 8, precioUnit: 1690 },
      { minCajas: 25, precioUnit: 1490 },
    ],
    tags: [],
    desc: "Pack de 6 pares, algodón con refuerzo de talón. Tallas surtidas. Embalaje de 60 packs.",
  },
  {
    id: "tec-04",
    name: "Parlante Bluetooth Resistente IPX6",
    sku: "TGS-PAR-2255",
    cat: "tec",
    tint: "#2486b8",
    embalaje: 12,
    stock: 144,
    importador: "Guangzhou Lemon Trade",
    tiers: [
      { minCajas: 1, precioUnit: 9990 },
      { minCajas: 4, precioUnit: 9090 },
      { minCajas: 12, precioUnit: 8190 },
    ],
    tags: [],
    desc: "Parlante portátil resistente al agua, 12h de batería y sonido 360°. Embalaje de 12 unidades.",
  },
  {
    id: "hogar-03",
    name: "Juego de Sábanas Microfibra 2 plazas",
    sku: "TGS-SAB-6614",
    cat: "hogar",
    tint: "#1d8fc0",
    embalaje: 18,
    stock: 90,
    importador: "Dhaka Textile Group",
    tiers: [
      { minCajas: 1, precioUnit: 7990 },
      { minCajas: 5, precioUnit: 7190 },
      { minCajas: 15, precioUnit: 6390 },
    ],
    tags: [],
    desc: "Juego de 4 piezas en microfibra suave, colores surtidos. Embalaje de 18 sets.",
  },
];

// Regiones de Chile + costo de despacho por caja (mock)
const REGIONES = [
  { id: "rm", label: "Región Metropolitana", costoCaja: 1200, dias: "1–2" },
  { id: "v", label: "Valparaíso", costoCaja: 1800, dias: "2–3" },
  { id: "vi", label: "O'Higgins", costoCaja: 1900, dias: "2–3" },
  { id: "vii", label: "Maule", costoCaja: 2200, dias: "3–4" },
  { id: "viii", label: "Biobío", costoCaja: 2600, dias: "3–4" },
  { id: "ix", label: "La Araucanía", costoCaja: 2900, dias: "4–5" },
  { id: "ii", label: "Antofagasta", costoCaja: 3400, dias: "4–6" },
  { id: "x", label: "Los Lagos", costoCaja: 3600, dias: "5–6" },
  { id: "xv", label: "Arica y Parinacota", costoCaja: 4200, dias: "6–8" },
  { id: "xii", label: "Magallanes", costoCaja: 4900, dias: "7–9" },
];

// Datos bancarios para la transferencia (mock)
const BANCO = {
  titular: "Trade Global Solutions SpA",
  rut: "77.412.905-K",
  banco: "Banco de Chile",
  tipo: "Cuenta Corriente",
  numero: "001-2845-09931",
  email: "pagos@tradeglobal.cl",
};

// helpers de pricing
function tierPara(prod, cajas) {
  let t = prod.tiers[0];
  for (const tier of prod.tiers) if (cajas >= tier.minCajas) t = tier;
  return t;
}
function precioUnit(prod, cajas) {
  return tierPara(prod, cajas).precioUnit;
}

Object.assign(window, {
  CLP, CATEGORIES, PRODUCTS, REGIONES, BANCO, tierPara, precioUnit,
});
