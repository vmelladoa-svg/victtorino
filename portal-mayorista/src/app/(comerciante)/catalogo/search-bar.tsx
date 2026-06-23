"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SearchBar() {
  const router = useRouter();
  const [q, setQ] = useState("");

  function buscar(e: React.FormEvent) {
    e.preventDefault();
    const t = q.trim();
    router.push(t ? `/catalogo?q=${encodeURIComponent(t)}` : "/catalogo");
  }

  return (
    <form
      onSubmit={buscar}
      style={{
        flex: "1 1 240px",
        maxWidth: 620,
        display: "flex",
        alignItems: "center",
        background: "#fff",
        border: "1px solid var(--line)",
        borderRadius: "var(--rs)",
        overflow: "hidden",
        height: 40,
      }}
    >
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Buscar productos, categorías…"
        aria-label="Buscar"
        style={{
          flex: 1,
          height: "100%",
          border: "none",
          outline: "none",
          padding: "0 14px",
          fontSize: 14,
          color: "var(--ink)",
          background: "transparent",
          fontFamily: "inherit",
        }}
      />
      <button
        type="submit"
        aria-label="Buscar"
        style={{
          height: "100%",
          width: 46,
          border: "none",
          background: "var(--brand)",
          color: "#fff",
          cursor: "pointer",
          display: "grid",
          placeItems: "center",
        }}
      >
        <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.9} strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-3.5-3.5" />
        </svg>
      </button>
    </form>
  );
}
