"use client";
// ============================================================
//  ESTADO DEL CARRITO — Zustand + persistencia en localStorage
// ============================================================
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Product } from "@/data/products";

export interface CartLine {
  id: string; // clave única: product.id + variante
  product: Product;
  qty: number;
  color?: string;
  size?: string;
}

interface CartState {
  lines: CartLine[];
  drawerOpen: boolean;
  add: (product: Product, opts?: { qty?: number; color?: string; size?: string }) => void;
  remove: (id: string) => void;
  setQty: (id: string, qty: number) => void;
  clear: () => void;
  openDrawer: () => void;
  closeDrawer: () => void;
}

const lineKey = (p: Product, color?: string, size?: string) =>
  [p.id, color ?? "", size ?? ""].join("__");

export const useCart = create<CartState>()(
  persist(
    (set) => ({
      lines: [],
      drawerOpen: false,
      add: (product, opts) =>
        set((state) => {
          const qty = opts?.qty ?? 1;
          const id = lineKey(product, opts?.color, opts?.size);
          const existing = state.lines.find((l) => l.id === id);
          const lines = existing
            ? state.lines.map((l) =>
                l.id === id ? { ...l, qty: Math.min(l.qty + qty, product.stock) } : l
              )
            : [...state.lines, { id, product, qty, color: opts?.color, size: opts?.size }];
          return { lines, drawerOpen: true };
        }),
      remove: (id) => set((s) => ({ lines: s.lines.filter((l) => l.id !== id) })),
      setQty: (id, qty) =>
        set((s) => ({
          lines: s.lines
            .map((l) => (l.id === id ? { ...l, qty: Math.max(1, Math.min(qty, l.product.stock)) } : l))
            .filter((l) => l.qty > 0),
        })),
      clear: () => set({ lines: [] }),
      openDrawer: () => set({ drawerOpen: true }),
      closeDrawer: () => set({ drawerOpen: false }),
    }),
    {
      name: "donbalon-cart-v1",
      // Persistir SOLO los productos del carrito, no el estado del drawer.
      partialize: (s) => ({ lines: s.lines }),
    }
  )
);

// selectores derivados (helpers)
export const cartCount = (s: CartState) => s.lines.reduce((n, l) => n + l.qty, 0);
export const cartSubtotal = (s: CartState) =>
  s.lines.reduce((sum, l) => sum + l.product.price * l.qty, 0);
