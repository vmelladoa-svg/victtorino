"use client";

import Image from "next/image";
import { useMemo } from "react";
import { PRODUCTS } from "@/lib/products";
import { INSTALLATION_SERVICES } from "@/lib/installation";
import { cuotaText, formatCLP } from "@/lib/format";
import { ZONES, zoneById, shippingFor } from "@/lib/shipping";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

export function CartDrawer() {
  const {
    cartOpen,
    cart,
    closeCart,
    setQty,
    removeItem,
    openCheckout,
    proDiscountPct,
    shipZone,
    setShipZone,
  } = useStore();
  const byId = useMemo(
    () => new Map([...PRODUCTS, ...INSTALLATION_SERVICES].map((p) => [p.id, p])),
    []
  );
  if (!cartOpen) return null;

  const rows = cart
    .map((it) => ({ ...it, p: byId.get(it.id) }))
    .filter((r): r is { id: string; qty: number; p: (typeof PRODUCTS)[number] } =>
      Boolean(r.p)
    );
  const subtotal = rows.reduce((s, r) => s + r.p.price * r.qty, 0);
  const discount = Math.round((subtotal * proDiscountPct) / 100);
  const afterDiscount = subtotal - discount;
  const zone = zoneById(shipZone);
  const shipping = shippingFor(shipZone, afterDiscount);

  return (
    <div>
      <div className="overlay" onClick={closeCart} />
      <aside className="drawer">
        <div className="drawer-head">
          <h3>Tu carrito</h3>
          <button className="icon-btn" onClick={closeCart} aria-label="Cerrar">
            ✕
          </button>
        </div>
        <div className="drawer-body">
          {rows.length === 0 && (
            <div className="empty-cart">
              <Icon d={ICONS.cart} size={48} stroke={1.2} />
              <p>Tu carrito está vacío.</p>
              <p style={{ fontSize: 14, marginTop: 6 }}>
                Explora el catálogo y agrega productos.
              </p>
            </div>
          )}
          {rows.map((r) => (
            <div className="cart-row" key={r.id}>
              <span className={"cart-thumb" + (r.p.image ? " has-photo" : "")}>
                {r.p.image ? (
                  <Image
                    src={r.p.image}
                    alt={r.p.name}
                    width={56}
                    height={56}
                    style={{ objectFit: "contain" }}
                  />
                ) : (
                  r.p.name[0]
                )}
              </span>
              <div>
                <b>{r.p.name}</b>
                <span className="pr">{formatCLP(r.p.price)}</span>
                <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <span className="qty">
                    <button onClick={() => setQty(r.id, r.qty - 1)} aria-label="Quitar uno">
                      −
                    </button>
                    <span>{r.qty}</span>
                    <button onClick={() => setQty(r.id, r.qty + 1)} aria-label="Agregar uno">
                      +
                    </button>
                  </span>
                  <button className="cart-remove" onClick={() => removeItem(r.id)}>
                    Quitar
                  </button>
                </div>
              </div>
              <b className="line-total">{formatCLP(r.p.price * r.qty)}</b>
            </div>
          ))}
        </div>
        {rows.length > 0 && (
          <div className="drawer-foot">
            <div className="total-row">
              <span>Subtotal</span>
              <span>{formatCLP(subtotal)}</span>
            </div>
            {discount > 0 && (
              <div className="total-row discount-row">
                <span>Descuento Trade Pro ({proDiscountPct}%)</span>
                <span>−{formatCLP(discount)}</span>
              </div>
            )}
            <div className="zone-select">
              <label htmlFor="cart-zone">Despacho a</label>
              <select
                id="cart-zone"
                value={shipZone}
                onChange={(e) => setShipZone(e.target.value)}
              >
                {ZONES.map((z) => (
                  <option key={z.id} value={z.id}>
                    {z.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="total-row">
              <span>Despacho</span>
              <span>{shipping === 0 ? "Gratis" : formatCLP(shipping)}</span>
            </div>
            {zone.id === "retiro" ? (
              <div className="ship-hint">Coordinamos la entrega contigo por WhatsApp.</div>
            ) : (
              shipping > 0 &&
              zone.freeMin && (
                <div className="ship-hint">
                  Te faltan {formatCLP(zone.freeMin - afterDiscount)} para despacho gratis
                </div>
              )
            )}
            <div className="total-row grand">
              <span>Total</span>
              <span>{formatCLP(afterDiscount + shipping)}</span>
            </div>
            {cuotaText(afterDiscount + shipping) && (
              <div className="cuotas-note">ó {cuotaText(afterDiscount + shipping)}</div>
            )}
            <button
              className="btn btn-primary"
              style={{ justifyContent: "center" }}
              onClick={openCheckout}
            >
              Ir a pagar <Icon d={ICONS.arrow} size={17} />
            </button>
          </div>
        )}
      </aside>
    </div>
  );
}
