"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ProductCard, type ProductoRow } from "../catalogo/buscar";

export default function FavoritosClient({ productos }: { productos: ProductoRow[] }) {
  const [ids, setIds] = useState<string[] | null>(null);

  useEffect(() => {
    try {
      setIds(JSON.parse(localStorage.getItem("favoritos") || "[]"));
    } catch {
      setIds([]);
    }
  }, []);

  if (ids === null) return null; // evita parpadeo entre SSR y CSR

  const favs = productos.filter((p) => ids.includes(p.id));

  function quitar(id: string) {
    const next = ids!.filter((x) => x !== id);
    localStorage.setItem("favoritos", JSON.stringify(next));
    setIds(next);
    window.dispatchEvent(new Event("favoritos:cambio"));
  }

  if (favs.length === 0) {
    return (
      <div className="empty" style={{ textAlign: "center", padding: "60px 20px" }}>
        <p style={{ fontSize: 15, color: "var(--ink-2)", marginBottom: 14 }}>
          Aún no tienes favoritos. Toca el corazón ♥ en cualquier producto para guardarlo aquí.
        </p>
        <Link href="/catalogo" style={{ color: "var(--brand)", fontWeight: 700, textDecoration: "none" }}>
          Ir al catálogo
        </Link>
      </div>
    );
  }

  return (
    <div className="pgrid">
      {favs.map((p) => (
        <div key={p.id} style={{ position: "relative" }}>
          <button
            onClick={() => quitar(p.id)}
            aria-label="Quitar de favoritos"
            title="Quitar de favoritos"
            style={{
              position: "absolute", top: 8, right: 8, zIndex: 3,
              width: 32, height: 32, borderRadius: "50%", border: "none",
              background: "rgba(255,255,255,0.92)", boxShadow: "0 2px 6px rgba(0,0,0,0.18)",
              cursor: "pointer", display: "grid", placeItems: "center", padding: 0,
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#e0245e" stroke="#e0245e" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
          </button>
          <ProductCard prod={p} />
        </div>
      ))}
    </div>
  );
}
