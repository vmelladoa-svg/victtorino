"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { precioPorCantidad } from "@/lib/precios";

export type CartItem = {
  productoId: string;
  nombre: string;
  precioT1: number | null;
  precioT2: number | null;
  precioT3: number | null;
  fotoUrl: string | null;
  cantidad: number;
};

type CartCtx = {
  items: CartItem[];
  addItem: (item: Omit<CartItem, "cantidad">) => void;
  removeItem: (productoId: string) => void;
  setQty: (productoId: string, cantidad: number) => void;
  clearCart: () => void;
  total: number;
  count: number;
};

const KEY = "pm_carrito";

const Ctx = createContext<CartCtx | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [ready, setReady] = useState(false);

  // Hydrate from localStorage once on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) setItems(JSON.parse(raw));
    } catch {}
    setReady(true);
  }, []);

  // Persist to localStorage on change
  useEffect(() => {
    if (!ready) return;
    try {
      localStorage.setItem(KEY, JSON.stringify(items));
    } catch {}
  }, [items, ready]);

  const addItem = useCallback((item: Omit<CartItem, "cantidad">) => {
    setItems((prev) => {
      const idx = prev.findIndex((i) => i.productoId === item.productoId);
      if (idx >= 0) {
        const next = [...prev];
        next[idx] = { ...next[idx], cantidad: next[idx].cantidad + 1 };
        return next;
      }
      return [...prev, { ...item, cantidad: 1 }];
    });
  }, []);

  const removeItem = useCallback((productoId: string) => {
    setItems((prev) => prev.filter((i) => i.productoId !== productoId));
  }, []);

  const setQty = useCallback((productoId: string, cantidad: number) => {
    const q = Math.max(1, Math.floor(cantidad));
    setItems((prev) =>
      prev.map((i) => (i.productoId === productoId ? { ...i, cantidad: q } : i))
    );
  }, []);

  const clearCart = useCallback(() => {
    setItems([]);
  }, []);

  const total = items.reduce((acc, i) => {
    try {
      return acc + precioPorCantidad(i, i.cantidad) * i.cantidad;
    } catch {
      return acc;
    }
  }, 0);

  const count = items.reduce((acc, i) => acc + i.cantidad, 0);

  return (
    <Ctx.Provider value={{ items, addItem, removeItem, setQty, clearCart, total, count }}>
      {children}
    </Ctx.Provider>
  );
}

export function useCart(): CartCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useCart must be used inside CartProvider");
  return ctx;
}
