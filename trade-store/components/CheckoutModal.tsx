"use client";

import { useEffect, useMemo, useState } from "react";
import { PRODUCTS } from "@/lib/products";
import { INSTALLATION_SERVICES } from "@/lib/installation";
import { formatCLP } from "@/lib/format";
import { ZONES, zoneById, shippingFor } from "@/lib/shipping";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

interface Form {
  nombre: string;
  email: string;
  telefono: string;
  region: string;
  comuna: string;
  direccion: string;
  pago: "webpay" | "transfer";
}

const EMPTY: Form = {
  nombre: "",
  email: "",
  telefono: "",
  region: "",
  comuna: "",
  direccion: "",
  pago: "webpay",
};

export function CheckoutModal() {
  const {
    checkoutOpen,
    cart,
    closeCheckout,
    clearCart,
    proDiscountPct,
    addProSpend,
    shipZone,
    setShipZone,
  } = useStore();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<Form>(EMPTY);
  const byId = useMemo(
    () => new Map([...PRODUCTS, ...INSTALLATION_SERVICES].map((p) => [p.id, p])),
    []
  );

  useEffect(() => {
    if (checkoutOpen) setStep(0);
  }, [checkoutOpen]);

  if (!checkoutOpen) return null;

  const rows = cart
    .map((it) => ({ ...it, p: byId.get(it.id) }))
    .filter((r): r is { id: string; qty: number; p: (typeof PRODUCTS)[number] } =>
      Boolean(r.p)
    );
  const subtotal = rows.reduce((s, r) => s + r.p.price * r.qty, 0);
  const discount = Math.round((subtotal * proDiscountPct) / 100);
  const afterDiscount = subtotal - discount;
  const zone = zoneById(shipZone);
  const isPickup = zone.id === "retiro";
  const shipping = shippingFor(shipZone, afterDiscount);
  const total = afterDiscount + shipping;
  const set = (k: keyof Form, v: string) => setForm({ ...form, [k]: v });
  const canNext =
    step === 0
      ? Boolean(form.nombre && form.email && form.telefono)
      : step === 1
      ? isPickup || Boolean(form.region && form.comuna && form.direccion)
      : true;

  return (
    <div>
      <div className="overlay" />
      <div className="modal">
        <div className="modal-card" style={{ maxWidth: 560 }}>
          <button
            className="icon-btn"
            style={{ position: "absolute", top: 16, right: 16, zIndex: 2 }}
            onClick={closeCheckout}
            aria-label="Cerrar"
          >
            ✕
          </button>
          <div style={{ padding: "36px 36px 32px" }}>
            {step < 3 && (
              <div>
                <h3 style={{ fontSize: 22, marginBottom: 6 }}>Finalizar compra</h3>
                <p
                  style={{
                    color: "var(--ink-soft)",
                    fontSize: 14.5,
                    marginBottom: 20,
                  }}
                >
                  {step === 0
                    ? "Paso 1 de 3 — Tus datos"
                    : step === 1
                    ? "Paso 2 de 3 — Dirección de despacho"
                    : "Paso 3 de 3 — Pago"}
                </p>
                <div className="co-steps">
                  {[0, 1, 2].map((i) => (
                    <span key={i} className={"co-step" + (i <= step ? " on" : "")} />
                  ))}
                </div>
              </div>
            )}

            {step === 0 && (
              <div style={{ display: "grid", gap: 16 }}>
                <div className="field">
                  <label>Nombre completo</label>
                  <input
                    value={form.nombre}
                    onChange={(e) => set("nombre", e.target.value)}
                    placeholder="Ej: María González"
                  />
                </div>
                <div className="field">
                  <label>Correo electrónico</label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    placeholder="tucorreo@ejemplo.cl"
                  />
                </div>
                <div className="field">
                  <label>Teléfono</label>
                  <input
                    value={form.telefono}
                    onChange={(e) => set("telefono", e.target.value)}
                    placeholder="+56 9 …"
                  />
                </div>
              </div>
            )}

            {step === 1 && (
              <div style={{ display: "grid", gap: 16 }}>
                <div className="field">
                  <label>Zona de despacho</label>
                  <select value={shipZone} onChange={(e) => setShipZone(e.target.value)}>
                    {ZONES.map((z) => (
                      <option key={z.id} value={z.id}>
                        {z.name} —{" "}
                        {shippingFor(z.id, afterDiscount) === 0
                          ? "Gratis"
                          : formatCLP(shippingFor(z.id, afterDiscount))}
                      </option>
                    ))}
                  </select>
                </div>
                {isPickup ? (
                  <div className="demo-note">
                    Retiro en bodega — Madame Adriana Bolland 430, La Cisterna. Coordinamos día y
                    hora contigo por WhatsApp una vez confirmado el pago.
                  </div>
                ) : (
                  <>
                    <div className="field-row">
                      <div className="field">
                        <label>Región</label>
                        <input
                          value={form.region}
                          onChange={(e) => set("region", e.target.value)}
                          placeholder="Ej: Metropolitana"
                        />
                      </div>
                      <div className="field">
                        <label>Comuna</label>
                        <input
                          value={form.comuna}
                          onChange={(e) => set("comuna", e.target.value)}
                          placeholder="Ej: Ñuñoa"
                        />
                      </div>
                    </div>
                    <div className="field">
                      <label>Dirección</label>
                      <input
                        value={form.direccion}
                        onChange={(e) => set("direccion", e.target.value)}
                        placeholder="Calle, número, depto…"
                      />
                    </div>
                  </>
                )}
              </div>
            )}

            {step === 2 && (
              <div style={{ display: "grid", gap: 12 }}>
                {[
                  {
                    id: "webpay" as const,
                    b: "Webpay (crédito / débito)",
                    s: "Pago inmediato con tarjetas chilenas",
                  },
                  {
                    id: "transfer" as const,
                    b: "Transferencia bancaria",
                    s: "Te enviamos los datos al confirmar el pedido",
                  },
                ].map((o) => (
                  <div
                    key={o.id}
                    className={"pay-opt" + (form.pago === o.id ? " on" : "")}
                    onClick={() => set("pago", o.id)}
                  >
                    <Icon d={form.pago === o.id ? ICONS.check : ICONS.lock} size={20} />
                    <div>
                      <b>{o.b}</b>
                      <span>{o.s}</span>
                    </div>
                  </div>
                ))}
                <div
                  style={{
                    borderTop: "1px solid var(--line)",
                    paddingTop: 14,
                    display: "grid",
                    gap: 6,
                  }}
                >
                  <div className="total-row">
                    <span>
                      Subtotal ({rows.length} producto{rows.length === 1 ? "" : "s"})
                    </span>
                    <span>{formatCLP(subtotal)}</span>
                  </div>
                  {discount > 0 && (
                    <div className="total-row discount-row">
                      <span>Descuento Trade Pro ({proDiscountPct}%)</span>
                      <span>−{formatCLP(discount)}</span>
                    </div>
                  )}
                  <div className="total-row">
                    <span>Despacho</span>
                    <span>{shipping === 0 ? "Gratis" : formatCLP(shipping)}</span>
                  </div>
                  <div className="total-row grand">
                    <span>Total</span>
                    <span>{formatCLP(total)}</span>
                  </div>
                </div>
                <div className="demo-note">
                  Demo: el pago en línea se conectará a tu pasarela (Webpay / Mercado Pago) al
                  publicar el sitio. Este paso es una simulación.
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="co-success">
                <span className="ok-circle">
                  <Icon d={ICONS.check} size={34} stroke={2.4} />
                </span>
                <h3 style={{ fontSize: 24, marginBottom: 8 }}>¡Pedido confirmado!</h3>
                <p
                  style={{
                    color: "var(--ink-soft)",
                    maxWidth: 360,
                    margin: "0 auto 24px",
                  }}
                >
                  Gracias {form.nombre.split(" ")[0] || ""}. Te enviamos el detalle de tu compra
                  a {form.email || "tu correo"} y te avisaremos cuando el pedido esté en camino.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    clearCart();
                    closeCheckout();
                  }}
                >
                  Seguir explorando
                </button>
              </div>
            )}

            {step < 3 && (
              <div
                style={{ display: "flex", justifyContent: "space-between", marginTop: 26 }}
              >
                <button
                  className="btn btn-ghost"
                  onClick={() => (step === 0 ? closeCheckout() : setStep(step - 1))}
                >
                  {step === 0 ? "Cancelar" : "Atrás"}
                </button>
                <button
                  className="btn btn-primary"
                  disabled={!canNext}
                  style={{ opacity: canNext ? 1 : 0.45 }}
                  onClick={() => {
                    if (step === 2) addProSpend(total);
                    setStep(step + 1);
                  }}
                >
                  {step === 2 ? "Pagar " + formatCLP(total) : "Continuar"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
