// ============================================================
//  DATOS MOCK — Don Balón
//  En producción, reemplazar este archivo por llamadas a la API
//  real (ver lib/api.ts). La forma de los datos debe mantenerse.
// ============================================================

export type Sport =
  | "futbol"
  | "basquetbol"
  | "beisbol"
  | "voleibol"
  | "accesorios";

export type Badge = "Más vendido" | "Nuevo" | "Oferta" | "Profesional";

export interface Product {
  id: string;
  slug: string;
  name: string;
  sport: Sport;
  brand: string;
  price: number; // CLP
  compareAt?: number; // precio anterior (para ofertas), CLP
  images: string[]; // al menos 2 (la 2da para hover)
  description: string;
  specs: { label: string; value: string }[];
  badges: Badge[];
  stock: number;
  level: "amateur" | "profesional";
  use?: "indoor" | "outdoor";
  colors?: string[]; // nombres de variantes de color
  sizes?: string[];
  rating: number; // 0-5
  reviews: number;
}

export interface Category {
  slug: Sport;
  name: string;
  tagline: string;
  icon: string; // emoji liviano para la maqueta
  color: string; // hex de acento
  image: string;
}

// Helper para placeholders de marca (maqueta). Sustituir por imágenes reales.
const ph = (text: string, bg = "E8590C", fg = "FFFFFF") =>
  `https://placehold.co/700x700/${bg}/${fg}/png?text=${encodeURIComponent(text)}&font=montserrat`;

export const categories: Category[] = [
  { slug: "futbol", name: "Fútbol", tagline: "Pelotas, conos, chalecos y más", icon: "⚽", color: "#16A34A", image: ph("Fútbol", "16A34A") },
  { slug: "basquetbol", name: "Básquetbol", tagline: "Indoor, outdoor y entrenamiento", icon: "🏀", color: "#E8590C", image: ph("Básquetbol", "E8590C") },
  { slug: "beisbol", name: "Béisbol", tagline: "Pelotas, guantes y bates", icon: "⚾", color: "#2563EB", image: ph("Béisbol", "2563EB") },
  { slug: "voleibol", name: "Vóleibol", tagline: "Pelotas y redes oficiales", icon: "🏐", color: "#1A1A1A", image: ph("Vóleibol", "1A1A1A") },
  { slug: "accesorios", name: "Accesorios", tagline: "Infladores, bolsos, conos, bidones", icon: "🎒", color: "#D24A04", image: ph("Accesorios", "D24A04") },
];

export const brands = ["ProKick", "DunkMaster", "HomeRun", "SetPoint", "TopSport", "Arquero"];

export const products: Product[] = [
  // ---------------- FÚTBOL ----------------
  {
    id: "f1", slug: "balon-futbol-pro-match", name: "Balón Fútbol Pro Match N°5", sport: "futbol", brand: "ProKick",
    price: 29990, compareAt: 39990, images: [ph("Pro Match N°5", "16A34A"), ph("Pro Match · vista 2", "0F7A37")],
    description: "Balón de competición tamaño 5, cosido térmicamente para un vuelo estable y un toque preciso. Apto para cancha de pasto y sintética.",
    specs: [{ label: "Tamaño", value: "N°5 (oficial)" }, { label: "Peso", value: "420–445 g" }, { label: "Material", value: "PU termosellado" }, { label: "Cámara", value: "Latex" }],
    badges: ["Más vendido", "Oferta"], stock: 24, level: "profesional", use: "outdoor", colors: ["Blanco/Verde", "Negro/Naranja"], rating: 4.8, reviews: 132,
  },
  {
    id: "f2", slug: "balon-futsal-control", name: "Balón Futsal Control Bajo", sport: "futbol", brand: "ProKick",
    price: 24990, images: [ph("Futsal Control", "16A34A"), ph("Futsal · vista 2", "0F7A37")],
    description: "Balón de fútbol sala con bote bajo controlado, ideal para superficies de madera y cemento pulido.",
    specs: [{ label: "Tamaño", value: "N°4 futsal" }, { label: "Peso", value: "400–440 g" }, { label: "Material", value: "PU microcelular" }],
    badges: ["Nuevo"], stock: 18, level: "amateur", use: "indoor", rating: 4.6, reviews: 41,
  },
  {
    id: "f3", slug: "guantes-arquero-grip", name: "Guantes de Arquero Grip+", sport: "futbol", brand: "Arquero",
    price: 34990, compareAt: 44990, images: [ph("Guantes Grip+", "16A34A"), ph("Guantes · palma", "0F7A37")],
    description: "Guantes con látex de alto agarre y refuerzo de muñeca. Calce envolvente para máxima seguridad bajo los tres palos.",
    specs: [{ label: "Látex", value: "4 mm contacto" }, { label: "Cierre", value: "Correa elástica" }, { label: "Corte", value: "Roll finger" }],
    badges: ["Oferta", "Profesional"], stock: 12, level: "profesional", sizes: ["7", "8", "9", "10"], rating: 4.7, reviews: 58,
  },
  {
    id: "f4", slug: "set-conos-entrenamiento", name: "Set 20 Conos de Entrenamiento", sport: "futbol", brand: "TopSport",
    price: 12990, images: [ph("20 Conos", "16A34A"), ph("Conos · set", "0F7A37")],
    description: "Set de 20 conos flexibles de colores para circuitos de agilidad y velocidad. Incluye base de transporte.",
    specs: [{ label: "Cantidad", value: "20 unidades" }, { label: "Altura", value: "20 cm" }, { label: "Material", value: "PVC flexible" }],
    badges: [], stock: 40, level: "amateur", use: "outdoor", rating: 4.5, reviews: 23,
  },
  {
    id: "f5", slug: "chalecos-entrenamiento-x10", name: "Pack 10 Chalecos de Entrenamiento", sport: "futbol", brand: "TopSport",
    price: 18990, images: [ph("10 Chalecos", "16A34A"), ph("Chalecos · pack", "0F7A37")],
    description: "Petos livianos y transpirables para diferenciar equipos en los entrenamientos. Talla ajustable adulto.",
    specs: [{ label: "Cantidad", value: "10 unidades" }, { label: "Material", value: "Poliéster mesh" }, { label: "Talla", value: "Universal adulto" }],
    badges: ["Nuevo"], stock: 30, level: "amateur", colors: ["Naranjo", "Verde", "Azul"], rating: 4.4, reviews: 15,
  },

  // ---------------- BÁSQUETBOL ----------------
  {
    id: "b1", slug: "balon-basquetbol-indoor-pro", name: "Balón Básquetbol Indoor Pro N°7", sport: "basquetbol", brand: "DunkMaster",
    price: 39990, compareAt: 49990, images: [ph("Indoor Pro N°7", "E8590C"), ph("Indoor · vista 2", "B23C03")],
    description: "Balón de competición indoor con cuero compuesto premium y canales profundos para un dominio total del balón.",
    specs: [{ label: "Tamaño", value: "N°7 (oficial)" }, { label: "Peso", value: "567–650 g" }, { label: "Material", value: "Cuero compuesto" }, { label: "Uso", value: "Indoor" }],
    badges: ["Más vendido", "Profesional", "Oferta"], stock: 20, level: "profesional", use: "indoor", rating: 4.9, reviews: 210,
  },
  {
    id: "b2", slug: "balon-basquetbol-outdoor-street", name: "Balón Básquetbol Outdoor Street", sport: "basquetbol", brand: "DunkMaster",
    price: 27990, images: [ph("Outdoor Street", "E8590C"), ph("Outdoor · vista 2", "B23C03")],
    description: "Diseñado para el asfalto: goma resistente a la abrasión y agarre firme en cancha exterior.",
    specs: [{ label: "Tamaño", value: "N°7" }, { label: "Material", value: "Goma de alta resistencia" }, { label: "Uso", value: "Outdoor" }],
    badges: [], stock: 35, level: "amateur", use: "outdoor", rating: 4.6, reviews: 64,
  },
  {
    id: "b3", slug: "balon-entrenamiento-pesado", name: "Balón de Entrenamiento Pesado 1kg", sport: "basquetbol", brand: "DunkMaster",
    price: 32990, images: [ph("Training 1kg", "E8590C"), ph("Training · vista 2", "B23C03")],
    description: "Balón con peso extra para mejorar el control, el dribbling y la fuerza de muñeca en los entrenamientos.",
    specs: [{ label: "Peso", value: "1 kg" }, { label: "Tamaño", value: "N°7" }, { label: "Uso", value: "Entrenamiento" }],
    badges: ["Profesional"], stock: 14, level: "profesional", rating: 4.7, reviews: 38,
  },
  {
    id: "b4", slug: "red-basquetbol-anti-whip", name: "Red de Básquetbol Anti-Whip", sport: "basquetbol", brand: "TopSport",
    price: 8990, images: [ph("Red Anti-Whip", "E8590C"), ph("Red · detalle", "B23C03")],
    description: "Red de nylon trenzado de alta densidad que reduce el enredo y soporta el clima exterior.",
    specs: [{ label: "Material", value: "Nylon trenzado" }, { label: "Ganchos", value: "12" }, { label: "Uso", value: "Indoor / Outdoor" }],
    badges: ["Nuevo"], stock: 50, level: "amateur", rating: 4.3, reviews: 19,
  },

  // ---------------- BÉISBOL ----------------
  {
    id: "be1", slug: "pelota-beisbol-oficial-x3", name: "Pack 3 Pelotas Béisbol Oficiales", sport: "beisbol", brand: "HomeRun",
    price: 19990, images: [ph("3 Pelotas MLB", "2563EB"), ph("Pelotas · pack", "1E40AF")],
    description: "Pelotas de cuero genuino con costura roja clásica, peso y tamaño reglamentario para partido y práctica.",
    specs: [{ label: "Cantidad", value: "3 unidades" }, { label: "Peso", value: "142–149 g c/u" }, { label: "Material", value: "Cuero genuino" }],
    badges: ["Más vendido"], stock: 28, level: "profesional", rating: 4.8, reviews: 73,
  },
  {
    id: "be2", slug: "guante-beisbol-cuero-12", name: "Guante de Béisbol Cuero 12\"", sport: "beisbol", brand: "HomeRun",
    price: 49990, compareAt: 64990, images: [ph('Guante 12"', "2563EB"), ph("Guante · interior", "1E40AF")],
    description: "Guante de cuero premium de 12 pulgadas, pre-formado para un cierre rápido. Ideal para jardineros.",
    specs: [{ label: "Tamaño", value: "12 pulgadas" }, { label: "Material", value: "Cuero vacuno" }, { label: "Mano", value: "Diestro / Zurdo" }],
    badges: ["Oferta", "Profesional"], stock: 9, level: "profesional", colors: ["Café", "Negro"], rating: 4.7, reviews: 44,
  },
  {
    id: "be3", slug: "bate-aluminio-aero", name: "Bate de Aluminio Aero", sport: "beisbol", brand: "HomeRun",
    price: 38990, images: [ph("Bate Aero", "2563EB"), ph("Bate · grip", "1E40AF")],
    description: "Bate de aleación de aluminio liviano con balance optimizado y empuñadura antideslizante.",
    specs: [{ label: "Largo", value: "32 / 34 pulg" }, { label: "Material", value: "Aleación aluminio" }, { label: "Empuñadura", value: "Goma" }],
    badges: ["Nuevo"], stock: 16, level: "amateur", sizes: ["32\"", "34\""], rating: 4.5, reviews: 27,
  },

  // ---------------- VÓLEIBOL ----------------
  {
    id: "v1", slug: "balon-voleibol-soft-touch", name: "Balón Vóleibol Soft Touch", sport: "voleibol", brand: "SetPoint",
    price: 26990, compareAt: 32990, images: [ph("Soft Touch", "1A1A1A"), ph("Soft Touch · 2", "000000")],
    description: "Balón de toque suave laminado, cómodo para recepción y ataque. Apto para indoor y playa.",
    specs: [{ label: "Tamaño", value: "N°5 oficial" }, { label: "Peso", value: "260–280 g" }, { label: "Material", value: "PU laminado" }],
    badges: ["Más vendido", "Oferta"], stock: 22, level: "profesional", use: "indoor", rating: 4.7, reviews: 51,
  },
  {
    id: "v2", slug: "balon-voleibol-playa", name: "Balón Vóleibol Playa Resistente", sport: "voleibol", brand: "SetPoint",
    price: 22990, images: [ph("Beach Volley", "1A1A1A"), ph("Beach · 2", "000000")],
    description: "Resistente a la arena, el sol y la humedad. Superficie con textura para mejor agarre al aire libre.",
    specs: [{ label: "Tamaño", value: "N°5" }, { label: "Material", value: "PVC resistente" }, { label: "Uso", value: "Outdoor / Playa" }],
    badges: ["Nuevo"], stock: 19, level: "amateur", use: "outdoor", rating: 4.4, reviews: 18,
  },
  {
    id: "v3", slug: "red-voleibol-oficial", name: "Red de Vóleibol Oficial 9.5m", sport: "voleibol", brand: "SetPoint",
    price: 29990, images: [ph("Red 9.5m", "1A1A1A"), ph("Red · detalle", "000000")],
    description: "Red de competición con cable de acero y banda superior reforzada. Incluye bolso de transporte.",
    specs: [{ label: "Largo", value: "9.5 m" }, { label: "Alto", value: "1 m" }, { label: "Refuerzo", value: "Cable de acero" }],
    badges: ["Profesional"], stock: 11, level: "profesional", rating: 4.6, reviews: 22,
  },

  // ---------------- ACCESORIOS ----------------
  {
    id: "a1", slug: "inflador-doble-accion", name: "Inflador Doble Acción + Agujas", sport: "accesorios", brand: "TopSport",
    price: 9990, images: [ph("Inflador", "D24A04"), ph("Inflador · kit", "B23C03")],
    description: "Bomba manual de doble acción que infla en ambos sentidos. Incluye 3 agujas y manguera flexible.",
    specs: [{ label: "Tipo", value: "Doble acción" }, { label: "Incluye", value: "3 agujas + manguera" }, { label: "Material", value: "ABS + aluminio" }],
    badges: ["Más vendido"], stock: 60, level: "amateur", rating: 4.6, reviews: 88,
  },
  {
    id: "a2", slug: "bolso-deportivo-pro-bag", name: "Bolso Deportivo Pro Bag 45L", sport: "accesorios", brand: "TopSport",
    price: 27990, compareAt: 34990, images: [ph("Pro Bag 45L", "D24A04"), ph("Pro Bag · interior", "B23C03")],
    description: "Bolso amplio con compartimento para zapatillas, bolsillo ventilado y correa acolchada. 45 litros.",
    specs: [{ label: "Capacidad", value: "45 L" }, { label: "Material", value: "Poliéster 600D" }, { label: "Compartimentos", value: "4" }],
    badges: ["Oferta"], stock: 17, level: "amateur", colors: ["Negro", "Naranjo"], rating: 4.5, reviews: 36,
  },
  {
    id: "a3", slug: "bidon-deportivo-1l", name: "Bidón Deportivo 1L Anti-goteo", sport: "accesorios", brand: "TopSport",
    price: 6990, images: [ph("Bidón 1L", "D24A04"), ph("Bidón · tapa", "B23C03")],
    description: "Botella de 1 litro libre de BPA con pico anti-goteo y apertura rápida de una mano.",
    specs: [{ label: "Capacidad", value: "1 L" }, { label: "Material", value: "Tritan sin BPA" }, { label: "Tapa", value: "Pico anti-goteo" }],
    badges: [], stock: 80, level: "amateur", colors: ["Naranjo", "Verde", "Azul", "Negro"], rating: 4.4, reviews: 29,
  },
  {
    id: "a4", slug: "cinta-kinesica-pro", name: "Cinta Kinésica Pro (5 cm x 5 m)", sport: "accesorios", brand: "TopSport",
    price: 5990, images: [ph("Cinta Kinésica", "D24A04"), ph("Cinta · rollo", "B23C03")],
    description: "Vendaje neuromuscular elástico, hipoalergénico y resistente al agua para soporte muscular.",
    specs: [{ label: "Medidas", value: "5 cm x 5 m" }, { label: "Material", value: "Algodón elástico" }, { label: "Adhesivo", value: "Acrílico hipoalergénico" }],
    badges: ["Nuevo"], stock: 45, level: "amateur", colors: ["Negro", "Azul", "Beige"], rating: 4.3, reviews: 12,
  },
];

// -------- helpers de consulta (mock; espejo de la API real) --------
export const getAllProducts = () => products;
export const getProductBySlug = (slug: string) =>
  products.find((p) => p.slug === slug);
export const getProductsBySport = (sport: Sport) =>
  products.filter((p) => p.sport === sport);
export const getBestSellers = () =>
  products.filter((p) => p.badges.includes("Más vendido"));
export const getRelated = (p: Product, n = 4) =>
  products.filter((x) => x.sport === p.sport && x.id !== p.id).slice(0, n);
