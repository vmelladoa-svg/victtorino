// ============================================================
//  CAPA DE SERVICIOS (MOCK)
//  Hoy lee de data/products.ts con un pequeño delay simulado.
//  En producción: reemplazar los cuerpos por fetch() a tu API
//  o a tu CMS/headless commerce, manteniendo las firmas.
// ============================================================
import {
  products,
  categories,
  getProductBySlug,
  getProductsBySport,
  getBestSellers,
  getRelated,
  type Product,
  type Sport,
} from "@/data/products";

const delay = (ms = 120) => new Promise((r) => setTimeout(r, ms));

export async function fetchProducts(): Promise<Product[]> {
  await delay();
  return products;
}

export async function fetchCategories() {
  await delay();
  return categories;
}

export async function fetchProductBySlug(slug: string): Promise<Product | undefined> {
  await delay();
  return getProductBySlug(slug);
}

export async function fetchProductsBySport(sport: Sport): Promise<Product[]> {
  await delay();
  return getProductsBySport(sport);
}

export async function fetchBestSellers(): Promise<Product[]> {
  await delay();
  return getBestSellers();
}

export async function fetchRelated(product: Product): Promise<Product[]> {
  await delay();
  return getRelated(product);
}

/** Búsqueda con autocompletado (mock). En prod: endpoint /search?q= */
export async function searchProducts(q: string): Promise<Product[]> {
  await delay(60);
  const term = q.trim().toLowerCase();
  if (!term) return [];
  return products
    .filter(
      (p) =>
        p.name.toLowerCase().includes(term) ||
        p.brand.toLowerCase().includes(term) ||
        p.sport.toLowerCase().includes(term)
    )
    .slice(0, 6);
}
