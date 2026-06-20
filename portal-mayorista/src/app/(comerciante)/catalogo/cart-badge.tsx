"use client";

import { useCart } from "@/lib/cart-context";
import Link from "next/link";

export default function CartBadge() {
  const { count, total } = useCart();

  function clp(n: number) {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      minimumFractionDigits: 0,
    }).format(n);
  }

  return (
    <Link
      href="/carrito"
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        padding: "8px 14px",
        background: count > 0 ? "var(--brand)" : "var(--surface)",
        border: "1px solid " + (count > 0 ? "var(--brand)" : "var(--line)"),
        borderRadius: "var(--rs)",
        fontSize: 13,
        fontWeight: 700,
        color: count > 0 ? "#fff" : "var(--ink-2)",
        textDecoration: "none",
        transition: "all .15s",
        position: "relative",
      }}
    >
      <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
        <circle cx="9" cy="21" r="1" /><circle cx="20" cy="21" r="1" />
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
      </svg>
      {count > 0 ? (
        <>
          <span>{count} {count === 1 ? "item" : "items"}</span>
          <span className="mono" style={{ fontSize: 12 }}>{clp(total)}</span>
        </>
      ) : (
        "Carrito"
      )}
    </Link>
  );
}
