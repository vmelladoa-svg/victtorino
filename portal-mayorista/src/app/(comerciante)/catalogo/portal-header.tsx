import Link from "next/link";
import Image from "next/image";
import CartBadge from "./cart-badge";
import FavoritosLink from "./favoritos-link";
import SearchBar from "./search-bar";

export default function PortalHeader({ nombre }: { nombre?: string | null }) {
  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 40,
        background: "rgba(255,255,255,0.97)",
        backdropFilter: "blur(10px)",
        borderBottom: "1px solid var(--line)",
      }}
    >
      <div
        style={{
          maxWidth: 1240,
          margin: "0 auto",
          padding: "10px 26px",
          display: "flex",
          alignItems: "center",
          gap: 14,
          flexWrap: "wrap",
        }}
      >
        {/* Logo (al inicio) */}
        <Link
          href="/catalogo"
          style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none", flexShrink: 0 }}
        >
          <div style={{ width: 40, height: 40, borderRadius: "50%", overflow: "hidden", flexShrink: 0, display: "grid", placeItems: "center" }}>
            <Image src="/logo-clean.png" alt="Comercial Solutions" width={40} height={40} style={{ objectFit: "contain" }} />
          </div>
          <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.05 }}>
            <strong style={{ fontSize: 15, fontWeight: 800, color: "var(--ink)" }}>Comercial Solutions</strong>
            <small style={{ fontSize: 10.5, color: "var(--ink-3)", fontWeight: 600 }}>Portal Mayorista</small>
          </div>
        </Link>

        {/* Buscador grande (estilo ML) */}
        <SearchBar />

        {/* Acciones */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
          <FavoritosLink />
          <CartBadge />
          <Link
            href="/api/auth/signout"
            aria-label="Cerrar sesión"
            title={nombre ? `Cerrar sesión (${nombre})` : "Cerrar sesión"}
            style={{ display: "inline-flex", alignItems: "center", padding: "8px 10px", border: "1px solid var(--line)", borderRadius: "var(--rs)", color: "var(--ink-2)", textDecoration: "none" }}
          >
            <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </Link>
        </div>
      </div>
    </header>
  );
}
