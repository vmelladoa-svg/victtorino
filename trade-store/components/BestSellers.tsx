import type { Product } from "@/lib/types";
import { ProductCard } from "./ProductCard";

const BEST_SELLER_NAMES = [
  "Grifo Monomando Profesional Täumm",
  "Espejo Rectangular Moderno 3 Luces",
  "Lavaplatos Acero Inox Doble Empotrar",
  "Asiento con Tapa WC / Tapa Baño Soft Close",
  "Cabezal Ducha Redondo 3 Funciones",
  "Toallero Barra Doble Acero Inox",
  "Inodoro WC Doble Descarga Alargado",
  "Llave Monomando Lavatorio Lavamanos Modern",
];

export function BestSellers({ products }: { products: Product[] }) {
  const picks = BEST_SELLER_NAMES.map((n) =>
    products.find((p) => p.name.startsWith(n))
  ).filter((p): p is Product => Boolean(p));
  if (!picks.length) return null;
  return (
    <section className="block" id="mas-vendidos" style={{ paddingTop: 0 }}>
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Favoritos de nuestros clientes</span>
            <h2>Los más vendidos</h2>
            <p className="sec-sub">
              Los productos que más se repiten en los pedidos: calidad probada en hogares
              reales.
            </p>
          </div>
        </div>
        <div className="prod-grid">
          {picks.map((p) => (
            <ProductCard key={p.id} p={p} />
          ))}
        </div>
      </div>
    </section>
  );
}
