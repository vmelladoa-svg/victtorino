"use client";

import { useEffect, useMemo, useState } from "react";
import { CATEGORIES } from "@/lib/categories";
import { useStore } from "@/lib/store-context";
import type { Product } from "@/lib/types";
import { ProductCard } from "./ProductCard";
import { Icon, ICONS } from "./Icon";

const PAGE_SIZE = 24;
type SortKey = "relevance" | "price-asc" | "price-desc" | "name";

export function Catalog({ products }: { products: Product[] }) {
  const { activeCat, setActiveCat } = useStore();
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("relevance");
  const [shown, setShown] = useState(PAGE_SIZE);

  const filtered = useMemo(() => {
    let list = products;
    if (activeCat !== "Todos") list = list.filter((p) => p.category === activeCat);
    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter(
        (p) => p.name.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q)
      );
    }
    if (sort === "price-asc") list = [...list].sort((a, b) => a.price - b.price);
    if (sort === "price-desc") list = [...list].sort((a, b) => b.price - a.price);
    if (sort === "name") list = [...list].sort((a, b) => a.name.localeCompare(b.name, "es"));
    return list;
  }, [products, activeCat, query, sort]);

  useEffect(() => {
    setShown(PAGE_SIZE);
  }, [activeCat, query, sort]);

  const cats = ["Todos", ...CATEGORIES.map((c) => c.name)];

  return (
    <section className="block" id="catalogo">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Catálogo</span>
            <h2>Todos nuestros productos</h2>
            <p className="sec-sub">
              Precios en CLP con IVA incluido. Busca por nombre o código SKU.
            </p>
          </div>
        </div>

        <div className="filters">
          <div className="search-box">
            <Icon d={ICONS.search} size={18} />
            <input
              type="text"
              placeholder="Buscar producto o SKU…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <select
            className="sort-sel"
            value={sort}
            onChange={(e) => setSort(e.target.value as SortKey)}
          >
            <option value="relevance">Orden: destacados</option>
            <option value="price-asc">Precio: menor a mayor</option>
            <option value="price-desc">Precio: mayor a menor</option>
            <option value="name">Nombre A–Z</option>
          </select>
        </div>
        <div className="chips" style={{ marginBottom: 28 }}>
          {cats.map((c) => (
            <button
              key={c}
              className={"chip" + (activeCat === c ? " on" : "")}
              onClick={() => setActiveCat(c)}
            >
              {c}
            </button>
          ))}
        </div>

        <p className="results-note">
          {filtered.length} producto{filtered.length === 1 ? "" : "s"}
          {activeCat !== "Todos" ? " en " + activeCat : ""}
        </p>

        <div className="prod-grid">
          {filtered.slice(0, shown).map((p) => (
            <ProductCard key={p.id} p={p} />
          ))}
        </div>
        {filtered.length === 0 && (
          <div className="empty-cart">
            <p>No encontramos productos para tu búsqueda.</p>
          </div>
        )}
        {shown < filtered.length && (
          <div className="load-more">
            <button className="btn btn-ghost" onClick={() => setShown(shown + PAGE_SIZE)}>
              Ver más productos ({filtered.length - shown} restantes)
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
