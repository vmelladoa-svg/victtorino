import type { CategoryName } from "./types";

export interface CategoryDef {
  name: CategoryName;
  desc: string;
  /** clave de ícono en components/Icon */
  icon: string;
  /** slug para la imagen en /public/categories/{slug}.webp */
  slug: string;
}

export const CATEGORIES: CategoryDef[] = [
  { name: "Grifería", desc: "Llaves, monomandos y mezcladoras", icon: "faucet", slug: "griferia" },
  { name: "Baño", desc: "Lavatorios, vanitorios y accesorios", icon: "drop", slug: "bano" },
  { name: "Cocina", desc: "Lavaplatos, filtros y organización", icon: "sink", slug: "cocina" },
  { name: "Shower & Mamparas", desc: "Duchas, columnas y mamparas", icon: "shower", slug: "shower-mamparas" },
  { name: "Espejos", desc: "Espejos LED y de aumento", icon: "mirror", slug: "espejos" },
  { name: "WC e Inodoros", desc: "Inodoros, asientos y repuestos", icon: "wc", slug: "wc-inodoros" },
  { name: "Accesorios", desc: "Flexibles, sifones e instalación", icon: "tools", slug: "accesorios" },
];

/** Cuenta productos por categoría. */
export function countByCategory(
  products: { category: CategoryName }[]
): Record<string, number> {
  const c: Record<string, number> = {};
  for (const p of products) c[p.category] = (c[p.category] || 0) + 1;
  return c;
}
