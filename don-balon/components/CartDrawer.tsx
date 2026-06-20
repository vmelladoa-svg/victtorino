"use client";
import Image from "next/image";
import Link from "next/link";
import { useCart, cartSubtotal, cartCount } from "@/lib/store";
import { formatCLP } from "@/lib/format";

const FREE_SHIPPING = 39990;
const SHIPPING = 3990;

export default function CartDrawer() {
  const { lines, drawerOpen, closeDrawer, remove, setQty } = useCart();
  const subtotal = useCart(cartSubtotal);
  const count = useCart(cartCount);
  const shipping = subtotal >= FREE_SHIPPING || subtotal === 0 ? 0 : SHIPPING;
  const missing = Math.max(0, FREE_SHIPPING - subtotal);

  return (
    <>
      {/* overlay */}
      <div
        onClick={closeDrawer}
        className={`fixed inset-0 z-50 bg-black/50 transition-opacity ${drawerOpen ? "opacity-100" : "pointer-events-none opacity-0"}`}
      />
      {/* panel */}
      <aside
        className={`fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col bg-white shadow-2xl transition-transform duration-300 ${drawerOpen ? "translate-x-0" : "translate-x-full"}`}
      >
        <div className="flex items-center justify-between border-b border-black/10 p-5">
          <h2 className="font-display text-xl">Tu carrito ({count})</h2>
          <button onClick={closeDrawer} className="grid h-9 w-9 place-items-center rounded-full hover:bg-neutral-100">✕</button>
        </div>

        {lines.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
            <span className="text-5xl">🛒</span>
            <p className="text-neutral-500">Tu carrito está vacío.</p>
            <Link href="/catalogo" onClick={closeDrawer} className="btn-primary px-6 py-3">Ver productos</Link>
          </div>
        ) : (
          <>
            {/* barra envío gratis */}
            <div className="border-b border-black/5 bg-balon-50 px-5 py-3 text-sm">
              {missing > 0 ? (
                <>Te faltan <b className="text-balon">{formatCLP(missing)}</b> para el envío gratis 🚚</>
              ) : (
                <span className="font-semibold text-cancha">¡Tienes envío gratis! 🎉</span>
              )}
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white">
                <div className="h-full rounded-full bg-balon transition-all" style={{ width: `${Math.min(100, (subtotal / FREE_SHIPPING) * 100)}%` }} />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              {lines.map((l) => (
                <div key={l.id} className="flex gap-3 border-b border-black/5 py-3">
                  <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl bg-neutral-100">
                    <Image src={l.product.images[0]} alt={l.product.name} fill sizes="80px" className="object-cover" />
                  </div>
                  <div className="flex flex-1 flex-col">
                    <div className="flex justify-between gap-2">
                      <span className="line-clamp-2 text-sm font-semibold">{l.product.name}</span>
                      <button onClick={() => remove(l.id)} className="text-neutral-400 hover:text-balon">✕</button>
                    </div>
                    {(l.color || l.size) && (
                      <span className="text-xs text-neutral-500">{[l.color, l.size].filter(Boolean).join(" · ")}</span>
                    )}
                    <div className="mt-auto flex items-center justify-between">
                      <div className="flex items-center rounded-full border border-black/15">
                        <button onClick={() => setQty(l.id, l.qty - 1)} className="grid h-7 w-7 place-items-center">−</button>
                        <span className="w-6 text-center text-sm font-semibold">{l.qty}</span>
                        <button onClick={() => setQty(l.id, l.qty + 1)} className="grid h-7 w-7 place-items-center">+</button>
                      </div>
                      <span className="font-bold">{formatCLP(l.product.price * l.qty)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-black/10 p-5">
              <div className="flex justify-between text-sm text-neutral-600">
                <span>Subtotal</span><span>{formatCLP(subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm text-neutral-600">
                <span>Envío estimado</span><span>{shipping === 0 ? "Gratis" : formatCLP(shipping)}</span>
              </div>
              <div className="mt-2 flex justify-between border-t border-dashed border-black/10 pt-2 text-lg font-bold">
                <span>Total</span><span className="text-balon">{formatCLP(subtotal + shipping)}</span>
              </div>
              <Link href="/checkout" onClick={closeDrawer} className="btn-primary mt-4 w-full py-3.5">
                Finalizar compra →
              </Link>
              <button onClick={closeDrawer} className="mt-2 w-full text-center text-sm text-neutral-500 hover:text-carbon">
                Seguir comprando
              </button>
            </div>
          </>
        )}
      </aside>
    </>
  );
}
