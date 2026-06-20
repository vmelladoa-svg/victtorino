"use client";

import { useStore } from "@/lib/store-context";
import { SITE, waLink } from "@/lib/site";
import { Heart, Icon, ICONS } from "./Icon";

export function MobileBar() {
  const { cartCount, openCart, openWishlist } = useStore();
  return (
    <nav className="mbar">
      <a href={`tel:+${SITE.whatsapp}`}>
        <Icon d={ICONS.phone} size={20} /> Llamar
      </a>
      <a href={waLink()} target="_blank" rel="noopener">
        <Icon d={ICONS.chat} size={20} /> WhatsApp
      </a>
      <button onClick={openWishlist}>
        <Heart size={20} /> Favoritos
      </button>
      <button onClick={openCart} style={{ color: "var(--navy)" }}>
        <Icon d={ICONS.cart} size={20} /> Carrito{cartCount > 0 ? ` (${cartCount})` : ""}
      </button>
    </nav>
  );
}
