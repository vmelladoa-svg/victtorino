"use client";

import { useState } from "react";
import { CATEGORIES, type CategoryDef } from "@/lib/categories";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

function CategoryCard({
  c,
  count,
  onPick,
}: {
  c: CategoryDef;
  count: number;
  onPick: (name: string) => void;
}) {
  const [imgOk, setImgOk] = useState(true);
  return (
    <button className="cat-card2" onClick={() => onPick(c.name)}>
      <span className="cat-top">
        {imgOk ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`/categories/${c.slug}.webp`}
            alt={c.name}
            loading="lazy"
            decoding="async"
            onError={() => setImgOk(false)}
          />
        ) : (
          <Icon d={ICONS[c.icon]} size={34} stroke={1.5} />
        )}
      </span>
      <span className="cat-text">
        <b>{c.name}</b>
        <span className="cat-desc">{c.desc}</span>
        <span className="cat-count">{count} productos →</span>
      </span>
    </button>
  );
}

export function CategoryGrid({ counts }: { counts: Record<string, number> }) {
  const { pickCategory } = useStore();
  return (
    <section className="block" id="categorias">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Explora</span>
            <h2>Compra por categoría</h2>
          </div>
        </div>
        <div className="cat-grid">
          {CATEGORIES.map((c) => (
            <CategoryCard key={c.name} c={c} count={counts[c.name] || 0} onPick={pickCategory} />
          ))}
          <button
            className="cat-card"
            onClick={() => pickCategory("Todos")}
            style={{ background: "var(--navy)", borderColor: "var(--navy)" }}
          >
            <span
              className="cat-icon"
              style={{ background: "rgba(255,255,255,.12)", color: "#fff" }}
            >
              <Icon d={ICONS.box} size={22} stroke={1.6} />
            </span>
            <span>
              <b style={{ display: "block", color: "#fff" }}>Todo el catálogo</b>
              <span style={{ color: "rgba(255,255,255,.7)" }}>Explora todos los productos</span>
            </span>
            <span style={{ fontSize: 13, fontWeight: 700, color: "#56D6F5" }}>Ver todo →</span>
          </button>
        </div>
      </div>
    </section>
  );
}
