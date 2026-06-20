"use client";

import { useState, useMemo } from "react";
import Image from "next/image";
import AgregarAlCarrito from "./agregar";

/* ------------------------------------------------------------------ */
/*  Tipos                                                               */
/* ------------------------------------------------------------------ */
export type ProductoRow = {
  id: string;
  codigoAlila: string;
  nombre: string;
  categoria: string | null;
  precioT1: number | null;
  precioT2: number | null;
  precioT3: number | null;
  fotoUrl: string | null;
  stock: number | null;
  activo: boolean;
};

/* ------------------------------------------------------------------ */
/*  Helpers                                                             */
/* ------------------------------------------------------------------ */
function clp(n: number | null): string {
  if (n == null) return "Consultar";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(n);
}

/* ------------------------------------------------------------------ */
/*  Icono simple SVG inline                                             */
/* ------------------------------------------------------------------ */
function SearchIcon() {
  return (
    <svg
      width={18}
      height={18}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </svg>
  );
}

function FilterIcon() {
  return (
    <svg
      width={16}
      height={16}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 5h18M6 12h12M10 19h4" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/*  Tarjeta de producto                                                  */
/* ------------------------------------------------------------------ */
function ProductCard({ prod }: { prod: ProductoRow }) {
  const sinStock = !prod.stock || prod.stock <= 0;
  const [imgError, setImgError] = useState(false);

  return (
    <article
      className={`pcard${sinStock ? " is-out" : ""}`}
      style={{ cursor: "default" }}
    >
      {/* Imagen */}
      <div className="pcard-media">
        {prod.fotoUrl && !imgError ? (
          <div
            style={{
              height: 168,
              position: "relative",
              borderRadius: "var(--rs)",
              overflow: "hidden",
            }}
          >
            <Image
              src={prod.fotoUrl}
              alt={prod.nombre}
              fill
              sizes="(max-width: 720px) 50vw, (max-width: 1080px) 33vw, 25vw"
              style={{ objectFit: "cover" }}
              unoptimized
              onError={() => setImgError(true)}
            />
          </div>
        ) : (
          /* Placeholder de rayas igual a la maqueta */
          <div
            style={{
              height: 168,
              background: "#0e7cc414",
              borderRadius: "var(--rs)",
              display: "grid",
              placeItems: "center",
              position: "relative",
            }}
          >
            <span
              style={{
                fontFamily: "var(--mono)",
                fontSize: "10.5px",
                fontWeight: 700,
                opacity: 0.55,
                letterSpacing: ".02em",
                color: "#0e7cc4",
              }}
            >
              sin foto
            </span>
          </div>
        )}

        {/* Badge sin stock */}
        {sinStock && (
          <div className="pcard-tags">
            <span className="badge badge-out">Sin stock</span>
          </div>
        )}
      </div>

      {/* Cuerpo */}
      <div className="pcard-body">
        <span className="pcard-sku mono">{prod.codigoAlila}</span>
        <h3>{prod.nombre}</h3>

        {/* Tramos de precio */}
        <div
          className="vol"
          style={{ margin: "8px 0 4px", border: "1px solid var(--line)", borderRadius: "var(--radius)", overflow: "hidden" }}
        >
          <div className="vol-head">
            <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10" />
            </svg>
            Precio por volumen
          </div>
          <div className="vol-tiers">
            <div className="vol-tier">
              <small>1–5 unid.</small>
              <strong className="mono">{clp(prod.precioT1)}</strong>
            </div>
            <div className="vol-tier">
              <small>6–20 unid.</small>
              <strong className="mono">{clp(prod.precioT2)}</strong>
            </div>
            <div className="vol-tier" style={{ borderRight: 0 }}>
              <small>21+ unid.</small>
              <strong className="mono">{clp(prod.precioT3)}</strong>
            </div>
          </div>
        </div>

        {prod.categoria && (
          <div className="pcard-meta">
            <span className="badge badge-neutral">{prod.categoria}</span>
          </div>
        )}

        <AgregarAlCarrito prod={prod} />
      </div>
    </article>
  );
}

/* ------------------------------------------------------------------ */
/*  Componente principal (client)                                        */
/* ------------------------------------------------------------------ */
export default function BuscarCatalogo({
  productos,
  categorias,
}: {
  productos: ProductoRow[];
  categorias: string[];
}) {
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState("todas");

  const lista = useMemo(() => {
    let l = productos;

    // Filtro por categoría
    if (cat !== "todas") {
      l = l.filter((p) => p.categoria === cat);
    }

    // Filtro por texto
    const q = query.trim().toLowerCase();
    if (q) {
      l = l.filter((p) =>
        (p.nombre + " " + p.codigoAlila + " " + (p.categoria ?? ""))
          .toLowerCase()
          .includes(q)
      );
    }

    return l;
  }, [productos, query, cat]);

  return (
    <div className="catalog">
      {/* Barra de búsqueda */}
      <div
        style={{
          display: "flex",
          gap: 12,
          marginBottom: 22,
          flexWrap: "wrap",
        }}
      >
        {/* Input búsqueda */}
        <div
          className="hdr-search"
          style={{ flex: "1 1 260px", maxWidth: 480 }}
        >
          <SearchIcon />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar por nombre, SKU o categoría…"
          />
        </div>

        {/* Select categoría */}
        <div
          className="cat-sort"
          style={{ display: "flex", alignItems: "center", gap: 8 }}
        >
          <FilterIcon />
          <select
            value={cat}
            onChange={(e) => setCat(e.target.value)}
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--rs)",
              padding: "9px 12px",
              background: "var(--surface)",
              fontSize: "13.5px",
              fontWeight: 600,
              color: "var(--ink)",
              cursor: "pointer",
              outline: "none",
              fontFamily: "inherit",
            }}
          >
            <option value="todas">Todas las categorías</option>
            {categorias.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Contador */}
      <div className="cat-head" style={{ marginBottom: 16 }}>
        <h2 style={{ fontSize: 21, fontWeight: 800 }}>
          {query
            ? `Resultados para "${query}"`
            : cat !== "todas"
            ? cat
            : "Catálogo mayorista"}
        </h2>
        <span className="mono" style={{ color: "var(--ink-3)", fontSize: 13 }}>
          {lista.length} producto{lista.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Chips de categoría */}
      <div className="cat-bar" style={{ marginBottom: 22 }}>
        <div className="cat-chips">
          <button
            className={`chip${cat === "todas" ? " is-on" : ""}`}
            onClick={() => setCat("todas")}
          >
            Todas
          </button>
          {categorias.map((c) => (
            <button
              key={c}
              className={`chip${cat === c ? " is-on" : ""}`}
              onClick={() => setCat(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Grilla */}
      {lista.length > 0 ? (
        <div className="pgrid">
          {lista.map((p) => (
            <ProductCard key={p.id} prod={p} />
          ))}
        </div>
      ) : (
        <div className="empty">
          <SearchIcon />
          <p>No encontramos productos para tu búsqueda.</p>
        </div>
      )}
    </div>
  );
}
