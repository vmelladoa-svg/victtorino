"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

/* ─────────────────────────────────────────────────────────────
   Banners de campañas/promos. EDITABLE: cambia/agrega aquí.
   - titulo / sub: texto
   - bg: fondo (gradiente o color)
   - href: a dónde lleva al hacer clic (categoría, oferta, etc.)
   ───────────────────────────────────────────────────────────── */
const BANNERS: { titulo: string; sub: string; bg: string; href: string }[] = [
  {
    titulo: "Precios mayoristas por volumen",
    sub: "Mientras más compras, mejor precio — 3 tramos por producto",
    bg: "linear-gradient(100deg, #083e62, #0e7cc4)",
    href: "/catalogo",
  },
  {
    titulo: "Despacho a todo Chile",
    sub: "Reposición semanal desde bodega · 16 regiones",
    bg: "linear-gradient(100deg, #0a5c4a, #16a34a)",
    href: "/catalogo",
  },
  {
    titulo: "Tecnología y Hogar en oferta",
    sub: "Explora las categorías destacadas del catálogo",
    bg: "linear-gradient(100deg, #6d28d9, #a855f7)",
    href: "/catalogo",
  },
];

export default function PromoCarousel() {
  const [i, setI] = useState(0);
  const n = BANNERS.length;

  useEffect(() => {
    if (n < 2) return;
    const t = setInterval(() => setI((x) => (x + 1) % n), 5000);
    return () => clearInterval(t);
  }, [n]);

  return (
    <div
      style={{
        position: "relative",
        borderRadius: "var(--radius)",
        overflow: "hidden",
        marginBottom: 24,
        boxShadow: "0 6px 20px -12px rgba(8,62,98,0.5)",
      }}
    >
      <div
        style={{
          display: "flex",
          transform: `translateX(${-i * 100}%)`,
          transition: "transform 0.5s ease",
        }}
      >
        {BANNERS.map((b, idx) => (
          <Link
            key={idx}
            href={b.href}
            style={{
              flex: "0 0 100%",
              minWidth: "100%",
              textDecoration: "none",
              background: b.bg,
              color: "#fff",
              padding: "22px 28px",
              minHeight: 96,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              gap: 4,
            }}
          >
            <strong style={{ fontSize: 20, fontWeight: 800, letterSpacing: "-0.01em" }}>
              {b.titulo}
            </strong>
            <span style={{ fontSize: 13.5, opacity: 0.92 }}>{b.sub}</span>
          </Link>
        ))}
      </div>

      {n > 1 && (
        <div
          style={{
            position: "absolute",
            bottom: 10,
            right: 14,
            display: "flex",
            gap: 6,
          }}
        >
          {BANNERS.map((_, idx) => (
            <button
              key={idx}
              aria-label={`Ir al banner ${idx + 1}`}
              onClick={() => setI(idx)}
              style={{
                width: idx === i ? 20 : 8,
                height: 8,
                borderRadius: 4,
                border: "none",
                padding: 0,
                cursor: "pointer",
                background: idx === i ? "#fff" : "rgba(255,255,255,0.5)",
                transition: "width 0.2s ease",
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
