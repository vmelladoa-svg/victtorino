"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useCart, cartCount } from "@/lib/store";
import { categories, type Product } from "@/data/products";
import { searchProducts } from "@/lib/api";
import { formatCLP } from "@/lib/format";

export default function Header() {
  const count = useCart(cartCount);
  const openDrawer = useCart((s) => s.openDrawer);
  const [mounted, setMounted] = useState(false);
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Product[]>([]);
  const [focused, setFocused] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    let active = true;
    searchProducts(q).then((r) => active && setResults(r));
    return () => {
      active = false;
    };
  }, [q]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setFocused(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <header className="sticky top-0 z-40 border-b border-black/10 bg-white/90 backdrop-blur">
      {/* barra superior */}
      <div className="bg-grad-carbon text-center text-[12px] font-medium text-white/90">
        <div className="container-db py-2">
          🚚 Envío <b className="text-white">GRATIS</b> en compras sobre {formatCLP(39990)} · Despacho a todo Chile
        </div>
      </div>

      <div className="container-db flex items-center gap-4 py-3">
        {/* logo */}
        <Link href="/" className="flex shrink-0 items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-grad-balon text-lg shadow-cta">🏀</span>
          <span className="display text-2xl text-carbon">
            Don<span className="text-balon">Balón</span>
          </span>
        </Link>

        {/* buscador con autocompletado */}
        <div ref={boxRef} className="relative mx-auto hidden w-full max-w-xl md:block">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onFocus={() => setFocused(true)}
            placeholder="Busca pelotas, guantes, marcas…"
            className="w-full rounded-full border border-black/15 bg-neutral-50 px-5 py-2.5 text-sm outline-none transition focus:border-balon focus:bg-white"
          />
          <span className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400">🔍</span>
          {focused && results.length > 0 && (
            <div className="absolute left-0 right-0 top-12 overflow-hidden rounded-2xl border border-black/10 bg-white shadow-card">
              {results.map((p) => (
                <Link
                  key={p.id}
                  href={`/producto/${p.slug}`}
                  onClick={() => setFocused(false)}
                  className="flex items-center gap-3 px-4 py-2.5 hover:bg-balon-50"
                >
                  <span className="grid h-9 w-9 place-items-center rounded bg-neutral-100 text-base">{sportIcon(p.sport)}</span>
                  <span className="flex-1 text-sm font-medium">{p.name}</span>
                  <span className="text-sm font-bold text-balon">{formatCLP(p.price)}</span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* carrito */}
        <button
          onClick={openDrawer}
          className="relative ml-auto flex items-center gap-2 rounded-full bg-carbon px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-carbon-800 md:ml-0"
        >
          <span>🛒</span>
          <span className="hidden sm:inline">Carrito</span>
          {mounted && count > 0 && (
            <span className="grid h-5 min-w-5 place-items-center rounded-full bg-balon px-1 text-[11px] font-bold">
              {count}
            </span>
          )}
        </button>
      </div>

      {/* nav categorías */}
      <nav className="border-t border-black/5">
        <div className="container-db no-scrollbar flex items-center gap-1 overflow-x-auto py-1.5">
          <Link href="/catalogo" className="whitespace-nowrap rounded-full px-3 py-1.5 text-sm font-semibold text-carbon hover:bg-balon-50 hover:text-balon">
            Todo
          </Link>
          {categories.map((c) => (
            <Link
              key={c.slug}
              href={`/catalogo?sport=${c.slug}`}
              className="flex items-center gap-1.5 whitespace-nowrap rounded-full px-3 py-1.5 text-sm font-medium text-neutral-600 hover:bg-balon-50 hover:text-balon"
            >
              <span>{c.icon}</span>
              {c.name}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}

function sportIcon(s: string) {
  return { futbol: "⚽", basquetbol: "🏀", beisbol: "⚾", voleibol: "🏐", accesorios: "🎒" }[s] ?? "🏅";
}
