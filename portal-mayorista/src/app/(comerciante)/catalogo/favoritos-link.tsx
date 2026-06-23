"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function FavoritosLink() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const leer = () => {
      try {
        const favs: string[] = JSON.parse(localStorage.getItem("favoritos") || "[]");
        setCount(favs.length);
      } catch {
        setCount(0);
      }
    };
    leer();
    window.addEventListener("focus", leer);
    window.addEventListener("favoritos:cambio", leer);
    return () => {
      window.removeEventListener("focus", leer);
      window.removeEventListener("favoritos:cambio", leer);
    };
  }, []);

  return (
    <Link
      href="/favoritos"
      aria-label="Favoritos"
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 7,
        padding: "8px 12px",
        background: count > 0 ? "var(--brand-tint)" : "var(--surface)",
        border: "1px solid " + (count > 0 ? "var(--brand-line)" : "var(--line)"),
        borderRadius: "var(--rs)",
        fontSize: 13,
        fontWeight: 700,
        color: count > 0 ? "var(--brand-deep)" : "var(--ink-2)",
        textDecoration: "none",
      }}
    >
      <svg
        width={16}
        height={16}
        viewBox="0 0 24 24"
        fill={count > 0 ? "#e0245e" : "none"}
        stroke={count > 0 ? "#e0245e" : "currentColor"}
        strokeWidth={1.9}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
      {count > 0 ? count : ""}
    </Link>
  );
}
