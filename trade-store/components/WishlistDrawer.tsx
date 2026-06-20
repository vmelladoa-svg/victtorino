"use client";

import Image from "next/image";
import { useMemo } from "react";
import { PRODUCTS } from "@/lib/products";
import { formatCLP } from "@/lib/format";
import { useStore } from "@/lib/store-context";
import { Heart, Icon, ICONS } from "./Icon";

export function WishlistDrawer() {
  const {
    wishlistOpen,
    wishlist,
    closeWishlist,
    toggleWishlist,
    addToCart,
    setViewProduct,
  } = useStore();
  const byId = useMemo(() => new Map(PRODUCTS.map((p) => [p.id, p])), []);
  if (!wishlistOpen) return null;

  const rows = wishlist
    .map((id) => byId.get(id))
    .filter((p): p is (typeof PRODUCTS)[number] => Boolean(p));

  return (
    <div>
      <div className="overlay" onClick={closeWishlist} />
      <aside className="drawer">
        <div className="drawer-head">
          <h3>Mis favoritos</h3>
          <button className="icon-btn" onClick={closeWishlist} aria-label="Cerrar">
            ✕
          </button>
        </div>
        <div className="drawer-body">
          {rows.length === 0 && (
            <div className="empty-cart">
              <Heart size={48} />
              <p>Aún no tienes favoritos.</p>
              <p style={{ fontSize: 14, marginTop: 6 }}>
                Toca el corazón ♡ en un producto para guardarlo aquí.
              </p>
            </div>
          )}
          {rows.map((p) => (
            <div className="wish-row" key={p.id}>
              <span
                className={"cart-thumb" + (p.image ? " has-photo" : "")}
                onClick={() => {
                  closeWishlist();
                  setViewProduct(p);
                }}
                style={{ cursor: "pointer" }}
              >
                {p.image ? (
                  <Image src={p.image} alt={p.name} width={56} height={56} style={{ objectFit: "contain" }} />
                ) : (
                  p.name[0]
                )}
              </span>
              <div>
                <b>{p.name}</b>
                <span className="pr">{formatCLP(p.price)}</span>
                <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 6 }}>
                  <button className="btn-mini" onClick={() => addToCart(p)}>
                    <Icon d={ICONS.cart} size={14} /> Agregar
                  </button>
                  <button className="cart-remove" onClick={() => toggleWishlist(p.id)}>
                    Quitar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}
