export type CategoryName =
  | "Grifería"
  | "Baño"
  | "Cocina"
  | "Shower & Mamparas"
  | "Espejos"
  | "WC e Inodoros"
  | "Accesorios";

export interface Product {
  id: string;
  name: string;
  price: number;
  priceOriginal: number | null;
  lowStock: boolean;
  sku: string;
  category: CategoryName;
  /** Foto principal del producto (cards, carrito). Si no existe, se usa el placeholder. */
  image?: string;
  /** Galería completa (principal primero) para el modal de producto. */
  images?: string[];
  /** Atributos / ficha técnica (nombre → valor). */
  attributes?: { name: string; value: string }[];
}

export interface CartItem {
  id: string;
  qty: number;
}
