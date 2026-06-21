"use client";

import { useCart } from "@/lib/cart-context";

interface ProdDetalle {
  id: string;
  nombre: string;
  precioT1: number | null;
  precioT2: number | null;
  precioT3: number | null;
  fotoUrl: string | null;
  stock: number | null;
}

interface AgregarDesdeDetalleProps {
  prod: ProdDetalle;
}

export default function AgregarDesdeDetalle({ prod }: AgregarDesdeDetalleProps) {
  const { addItem, items } = useCart();
  const enCarrito = items.find((i) => i.productoId === prod.id);
  const sinStock = !prod.stock || prod.stock <= 0;

  function handleClick() {
    if (sinStock) return;
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
      disabled={sinStock}
      style={{
        width: "100%",
        padding: "13px 0",
        background: sinStock
          ? "var(--line)"
          : enCarrito
          ? "var(--brand-soft)"
          : "var(--brand)",
        color: sinStock
          ? "var(--ink-3)"
          : enCarrito
          ? "var(--brand-deep)"
          : "#fff",
        border: "none",
        borderRadius: "var(--rs)",
        fontSize: 15,
        fontWeight: 700,
        cursor: sinStock ? "not-allowed" : "pointer",
        transition: "background .15s",
        letterSpacing: "-.01em",
      }}
    >
      {sinStock
        ? "Sin stock disponible"
        : enCarrito
        ? `En carrito (${enCarrito.cantidad})`
        : "Agregar al carrito"}
    </button>
  );
}
