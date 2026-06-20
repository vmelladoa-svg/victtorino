import type { Product } from "@/lib/types";
import { ProductCard } from "./ProductCard";

export function OffersSection({ products }: { products: Product[] }) {
  const offers = products.filter((p) => p.priceOriginal);
  if (!offers.length) return null;
  return (
    <section className="block soft" id="ofertas">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Por tiempo limitado</span>
            <h2>Ofertas destacadas</h2>
            <p className="sec-sub">
              Productos seleccionados con descuento real sobre su precio de lista.
            </p>
          </div>
        </div>
        <div className="offers-rail">
          {offers.map((p) => (
            <ProductCard key={p.id} p={p} />
          ))}
        </div>
      </div>
    </section>
  );
}
