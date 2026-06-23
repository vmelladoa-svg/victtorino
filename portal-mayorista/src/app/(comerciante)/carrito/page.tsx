"use client";

import { useCart } from "@/lib/cart-context";
import { precioPorCantidad } from "@/lib/precios";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";

/* ── helpers ── */
function clp(n: number): string {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(n);
}

/* ── icons ── */
function TrashIcon() {
  return (
    <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14H6L5 6" /><path d="M10 11v6M14 11v6" /><path d="M9 6V4h6v2" />
    </svg>
  );
}
function ChevLeftIcon() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  );
}
function ChevRightIcon() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 18l6-6-6-6" />
    </svg>
  );
}
function CartIcon() {
  return (
    <svg width={34} height={34} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="21" r="1" /><circle cx="20" cy="21" r="1" />
      <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
    </svg>
  );
}
function TruckIcon() {
  return (
    <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="3" width="15" height="13" /><path d="M16 8h4l3 5v4h-7z" />
      <circle cx="5.5" cy="18.5" r="2.5" /><circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  );
}
function ShieldIcon() {
  return (
    <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}
function GridIcon() {
  return (
    <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
    </svg>
  );
}

export default function CarritoPage() {
  const { items, removeItem, setQty, total } = useCart();
  const router = useRouter();

  if (items.length === 0) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--bg)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 18, padding: 32 }}>
        <div style={{ color: "var(--ink-3)" }}><CartIcon /></div>
        <h2 style={{ fontSize: 22, fontWeight: 800, color: "var(--ink)" }}>Tu cotización está vacía</h2>
        <p style={{ color: "var(--ink-2)", fontSize: 15 }}>Agrega productos del catálogo para armar tu pedido mayorista.</p>
        <Link
          href="/catalogo"
          style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "11px 20px", background: "var(--brand)", color: "#fff", borderRadius: "var(--rs)", fontWeight: 700, fontSize: 14, textDecoration: "none" }}
        >
          <GridIcon /> Ir al catálogo
        </Link>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", fontFamily: "var(--font)" }}>
      {/* Header */}
      <header style={{ position: "sticky", top: 0, zIndex: 40, background: "rgba(255,255,255,0.96)", backdropFilter: "blur(10px)", borderBottom: "1px solid var(--line)" }}>
        <div style={{ maxWidth: 1240, margin: "0 auto", padding: "13px 26px", display: "flex", alignItems: "center", gap: 20 }}>
          <Link href="/catalogo" style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 600, color: "var(--ink-2)", textDecoration: "none" }}>
            <ChevLeftIcon /> Seguir comprando
          </Link>
          <div style={{ flex: 1 }} />
          <h1 style={{ fontSize: 18, fontWeight: 800, color: "var(--ink)" }}>Carrito / Cotización</h1>
        </div>
      </header>

      <main style={{ maxWidth: 1240, margin: "0 auto", padding: "30px 26px 60px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 28, alignItems: "start" }}>

          {/* Items */}
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {items.map((item) => {
              let precio: number;
              try { precio = precioPorCantidad(item, item.cantidad); } catch { precio = 0; }
              const sub = precio * item.cantidad;

              return (
                <div
                  key={item.productoId}
                  style={{ background: "var(--surface)", borderRadius: "var(--radius)", border: "1px solid var(--line)", padding: "18px 22px", display: "flex", gap: 18, alignItems: "center", flexWrap: "wrap" }}
                >
                  {/* Foto */}
                  <div style={{ width: 80, height: 80, borderRadius: "var(--rs)", overflow: "hidden", background: "var(--bg)", flexShrink: 0, display: "grid", placeItems: "center" }}>
                    {item.fotoUrl ? (
                      <Image src={item.fotoUrl} alt={item.nombre} width={80} height={80} style={{ objectFit: "cover" }} />
                    ) : (
                      <span style={{ fontSize: 10, fontFamily: "var(--mono)", color: "var(--ink-3)" }}>sin foto</span>
                    )}
                  </div>

                  {/* Info */}
                  <div style={{ flex: 1, minWidth: 160 }}>
                    <h3 style={{ fontSize: 14.5, fontWeight: 700, color: "var(--ink)", marginBottom: 4 }}>{item.nombre}</h3>
                    <div style={{ display: "flex", gap: 16, fontSize: 12, color: "var(--ink-2)", flexWrap: "wrap" }}>
                      {item.precioT1 && <span>1–5: <b className="mono">{clp(item.precioT1)}</b></span>}
                      {item.precioT2 && <span>6–20: <b className="mono">{clp(item.precioT2)}</b></span>}
                      {item.precioT3 && <span>21+: <b className="mono">{clp(item.precioT3)}</b></span>}
                    </div>
                    <div style={{ marginTop: 6, fontSize: 13, color: "var(--ink-2)" }}>
                      Precio aplicado: <strong className="mono" style={{ color: "var(--brand-deep)" }}>{clp(precio)}</strong> c/u
                    </div>
                  </div>

                  {/* Qty */}
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, border: "1px solid var(--line)", borderRadius: "var(--rs)", overflow: "hidden" }}>
                      <button
                        onClick={() => setQty(item.productoId, item.cantidad - 1)}
                        disabled={item.cantidad <= 1}
                        style={{ width: 34, height: 34, background: "none", border: "none", fontSize: 18, fontWeight: 700, color: item.cantidad <= 1 ? "var(--ink-3)" : "var(--ink)", cursor: item.cantidad <= 1 ? "default" : "pointer" }}
                      >
                        −
                      </button>
                      <input
                        type="number"
                        value={item.cantidad}
                        min={1}
                        onChange={(e) => setQty(item.productoId, parseInt(e.target.value) || 1)}
                        style={{ width: 48, textAlign: "center", border: "none", outline: "none", fontSize: 14, fontWeight: 700, background: "none", fontFamily: "var(--mono)" }}
                      />
                      <button
                        onClick={() => setQty(item.productoId, item.cantidad + 1)}
                        style={{ width: 34, height: 34, background: "none", border: "none", fontSize: 18, fontWeight: 700, color: "var(--ink)", cursor: "pointer" }}
                      >
                        +
                      </button>
                    </div>
                    <span style={{ fontSize: 11, color: "var(--ink-3)" }}>unidades</span>
                  </div>

                  {/* Subtotal + remove */}
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8, minWidth: 100 }}>
                    <strong className="mono" style={{ fontSize: 16, fontWeight: 800, color: "var(--ink)" }}>{clp(sub)}</strong>
                    <button
                      onClick={() => removeItem(item.productoId)}
                      style={{ display: "inline-flex", alignItems: "center", gap: 5, padding: "5px 10px", background: "none", border: "1px solid var(--line)", borderRadius: "var(--rs)", fontSize: 12, color: "var(--ink-3)", cursor: "pointer" }}
                    >
                      <TrashIcon /> Quitar
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Sidebar resumen */}
          <aside style={{ background: "var(--surface)", borderRadius: "var(--radius)", border: "1px solid var(--line)", padding: "24px 22px", display: "flex", flexDirection: "column", gap: 14, position: "sticky", top: 80 }}>
            <h3 style={{ fontSize: 17, fontWeight: 800, color: "var(--ink)" }}>Resumen</h3>

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, color: "var(--ink-2)" }}>
              <span>Productos ({items.length})</span>
              <span className="mono">{clp(total)}</span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5, color: "var(--ink-2)", background: "var(--bg)", padding: "10px 12px", borderRadius: "var(--rs)" }}>
              <TruckIcon />
              El costo de despacho se calcula según tu región.
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: 10, borderTop: "1px solid var(--line)", fontSize: 16, fontWeight: 800, color: "var(--ink)" }}>
              <span>Subtotal</span>
              <strong className="mono">{clp(total)}</strong>
            </div>

            <button
              onClick={() => router.push("/checkout")}
              style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, width: "100%", padding: "13px 0", background: "var(--brand)", color: "#fff", border: "none", borderRadius: "var(--rs)", fontSize: 15, fontWeight: 700, cursor: "pointer" }}
            >
              Continuar al pago <ChevRightIcon />
            </button>

            <div style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 12, color: "var(--ink-3)", justifyContent: "center" }}>
              <ShieldIcon />
              Pago por transferencia · validación 24h
            </div>
          </aside>

        </div>
      </main>
    </div>
  );
}
