"use client";

import Image from "next/image";
import { useState } from "react";
import { useStore } from "@/lib/store-context";
import { tierForSpend } from "@/lib/pro";
import { Heart, Icon, ICONS } from "./Icon";

const LINKS = [
  { href: "#inicio", label: "Inicio" },
  { href: "#categorias", label: "Categorías" },
  { href: "#catalogo", label: "Catálogo" },
  { href: "#pro", label: "Trade Pro", accent: true },
  { href: "#nosotros", label: "Nosotros" },
  { href: "#contacto", label: "Contacto" },
];

export function Header() {
  const { cartCount, openCart, wishlistCount, openWishlist, pro } = useStore();
  const [menuOpen, setMenuOpen] = useState(false);
  const tier = pro ? tierForSpend(pro.spend) : null;

  return (
    <header className="hdr">
      <div className="wrap hdr-in">
        <a className="brand" href="#inicio" onClick={() => setMenuOpen(false)}>
          <Image src="/logo.png" alt="Logo Trade" width={59} height={44} priority />
          <span>
            <span className="brand-name">TRADE</span>
            <span className="brand-tag" style={{ display: "block" }}>
              Soluciones para tu hogar
            </span>
          </span>
        </a>

        <nav className="nav">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className={l.accent ? "nav-pro" : undefined}>
              {l.label}
            </a>
          ))}
        </nav>

        {tier && (
          <span className="pro-chip" title={"Programa Trade Pro — " + tier.name}>
            <span
              className="tdot"
              style={{ width: 10, height: 10, borderRadius: 99, background: tier.color, display: "inline-block" }}
            />
            {tier.name} · {tier.pct}%
          </span>
        )}

        <button
          className="hamburger"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={menuOpen}
        >
          <Icon d={menuOpen ? ICONS.close : ICONS.menu} size={22} />
        </button>

        <button className="wish-hdr" onClick={openWishlist} aria-label="Favoritos">
          <Heart size={20} />
          {wishlistCount > 0 && <span className="wish-count">{wishlistCount}</span>}
        </button>

        <button className="cart-btn" onClick={openCart}>
          <Icon d={ICONS.cart} size={18} />
          <span className="cart-btn-label">Carrito</span>
          <span className="cart-count">{cartCount}</span>
        </button>
      </div>

      {menuOpen && (
        <nav className="mobile-menu">
          <div className="wrap">
            {LINKS.map((l) => (
              <a key={l.href} href={l.href} onClick={() => setMenuOpen(false)}>
                {l.label}
              </a>
            ))}
          </div>
        </nav>
      )}
    </header>
  );
}
