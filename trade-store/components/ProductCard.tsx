"use client";

import Image from "next/image";
import { cuotaText, formatCLP } from "@/lib/format";
import type { Product } from "@/lib/types";
import { useStore } from "@/lib/store-context";
import { Heart, Icon, ICONS } from "./Icon";

export function ProductCard({ p }: { p: Product }) {
  const { addToCart, setViewProduct, justAdded, isWished, toggleWishlist } = useStore();
  const added = justAdded === p.id;
  const wished = isWished(p.id);
  return (
    <div className="prod-card">
      <div
        className={"prod-img" + (p.image ? " has-photo" : "")}
        onClick={() => setViewProduct(p)}
      >
        {p.image ? (
          <Image
            src={p.image}
            alt={p.name}
            fill
            sizes="(max-width: 820px) 50vw, (max-width: 1100px) 33vw, 25vw"
            style={{ objectFit: "contain" }}
          />
        ) : (
          <span className="ph-letter">{p.name[0]}</span>
        )}
        <span className="ph-cat">{p.category}</span>
        {p.priceOriginal && <span className="badge sale">Oferta</span>}
        {p.lowStock && <span className="badge low">Últimas unidades</span>}
        <button
          className={"wish-btn" + (wished ? " on" : "")}
          onClick={(e) => {
            e.stopPropagation();
            toggleWishlist(p.id);
          }}
          aria-label={wished ? "Quitar de favoritos" : "Agregar a favoritos"}
          aria-pressed={wished}
        >
          <Heart filled={wished} size={18} />
        </button>
      </div>
      <div className="prod-body">
        <span className="prod-name" onClick={() => setViewProduct(p)}>
          {p.name}
        </span>
        <div className="prod-price-row">
          <span className="prod-price">{formatCLP(p.price)}</span>
          {p.priceOriginal && (
            <span className="prod-price-old">{formatCLP(p.priceOriginal)}</span>
          )}
        </div>
        {cuotaText(p.price) && <span className="prod-cuotas">{cuotaText(p.price)}</span>}
        <button
          className={"add-btn" + (added ? " added" : "")}
          onClick={() => addToCart(p)}
        >
          {added ? <Icon d={ICONS.check} size={16} /> : <Icon d={ICONS.cart} size={16} />}
          {added ? "Agregado" : "Agregar al carrito"}
        </button>
      </div>
    </div>
  );
}
