"use client";

import { useCart } from "@/lib/cart-context";
import type { ProductoRow } from "./buscar";

export default function AgregarAlCarrito({ prod }: { prod: ProductoRow }) {
  const { addItem, items } = useCart();
  const enCarrito = items.find((i) => i.productoId === prod.id);

  function handleClick(e: React.MouseEvent) {
    e.stopPropagation();
    addItem({
      productoId: prod.id,
      nombre: prod.nombre,
      precioT1: prod.precioT1,
      precioT2: prod.precioT2,
      precioT3: prod.precioT3,
      fotoUrl: prod.fotoUrl,
    });
  }

  return (
    <button
      onClick={handleClick}
      style={{
        marginTop: 10,
        width: "100%",
        padding: "9px 0",
        background: enCarrito ? "var(--brand-soft)" : "var(--brand)",
        color: enCarrito ? "var(--brand-deep)" : "#fff",
        border: "none",
        borderRadius: "var(--rs)",
        fontSize: 13,
        fontWeight: 700,
        cursor: "pointer",
        transition: "background .15s",
      }}
    >
      {enCarrito ? `En carrito (${enCarrito.cantidad})` : "Agregar al carrito"}
    </button>
  );
}
