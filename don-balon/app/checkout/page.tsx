"use client";
import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCart, cartSubtotal } from "@/lib/store";
import { formatCLP } from "@/lib/format";
import { createWebpayTransaction } from "@/lib/payments/transbank";

const FREE_SHIPPING = 39990;
const SHIPPING = 3990;

export default function CheckoutPage() {
  const router = useRouter();
  const lines = useCart((s) => s.lines);
  const subtotal = useCart(cartSubtotal);
  const [delivery, setDelivery] = useState<"domicilio" | "retiro">("domicilio");
  const [loading, setLoading] = useState(false);

  const shipping = delivery === "retiro" || subtotal >= FREE_SHIPPING ? 0 : SHIPPING;
  const total = subtotal + shipping;

  async function handlePay(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    // =========================================================
    //  PUNTO DE INTEGRACIÓN TRANSBANK WEBPAY PLUS
    //  En producción, esta llamada debe ir a un route handler
    //  del servidor (app/api/webpay/create) que use el SDK con
    //  las credenciales. Aquí usamos el STUB de lib/payments/transbank.ts
    //  que devuelve una URL mock. Con Webpay real, se recibe
    //  { token, url } y se hace POST-redirect al formulario de Transbank.
    // =========================================================
    const { url } = await createWebpayTransaction({
      buyOrder: "DB-" + Date.now(),
      sessionId: "sess-" + Math.random().toString(36).slice(2),
      amount: total,
      returnUrl: "/checkout/confirmacion",
    });
    router.push(url); // mock → pantalla de confirmación simulada
  }

  if (lines.length === 0) {
    return (
      <div className="container-db grid place-items-center py-24 text-center">
        <span className="text-5xl">🛒</span>
        <h1 className="display mt-4 text-3xl">Tu carrito está vacío</h1>
        <p className="mt-2 text-neutral-500">Agrega productos antes de ir al checkout.</p>
        <Link href="/catalogo" className="btn-primary mt-6 px-6 py-3">Ver productos</Link>
      </div>
    );
  }

  return (
    <div className="container-db py-10">
      <h1 className="display text-4xl md:text-5xl">Finalizar compra</h1>
      <form onSubmit={handlePay} className="mt-8 grid gap-10 lg:grid-cols-[1fr_380px]">
        {/* columna izquierda: datos */}
        <div className="space-y-8">
          {/* contacto + envío */}
          <section className="rounded-2xl border border-black/10 p-6">
            <h2 className="font-head text-lg font-bold">1 · Tus datos</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label="Nombre completo" required placeholder="Juan Pérez" />
              <Field label="RUT" required placeholder="12.345.678-9" />
              <Field label="Correo electrónico" type="email" required placeholder="juan@correo.cl" />
              <Field label="Teléfono" type="tel" required placeholder="+56 9 1234 5678" />
            </div>
          </section>

          {/* método de entrega */}
          <section className="rounded-2xl border border-black/10 p-6">
            <h2 className="font-head text-lg font-bold">2 · Método de entrega</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <DeliveryOpt active={delivery === "domicilio"} onClick={() => setDelivery("domicilio")}
                icon="🚚" title="Envío a domicilio" desc={subtotal >= FREE_SHIPPING ? "Gratis · 24–48h" : `${formatCLP(SHIPPING)} · 24–48h`} />
              <DeliveryOpt active={delivery === "retiro"} onClick={() => setDelivery("retiro")}
                icon="🏬" title="Retiro en tienda" desc="Gratis · listo hoy" />
            </div>

            {delivery === "domicilio" && (
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <Field label="Dirección" required placeholder="Av. Siempre Viva 742" className="sm:col-span-2" />
                <Field label="Comuna" required placeholder="Providencia" />
                <Field label="Región" required placeholder="Metropolitana" />
              </div>
            )}
            {delivery === "retiro" && (
              <p className="mt-4 rounded-xl bg-balon-50 p-4 text-sm text-carbon">
                📍 Retira en <b>Don Balón — Av. Deporte 1234, Santiago</b>. Te avisamos por correo cuando esté listo.
              </p>
            )}
          </section>

          {/* pago */}
          <section className="rounded-2xl border border-black/10 p-6">
            <h2 className="font-head text-lg font-bold">3 · Pago</h2>
            <div className="mt-4 flex items-center gap-3 rounded-xl border border-azulina/30 bg-azulina/5 p-4">
              <span className="rounded-md bg-white px-3 py-1.5 text-sm font-bold text-azulina shadow-sm">Webpay</span>
              <span className="text-sm text-neutral-600">Tarjetas de crédito y débito · Transbank</span>
              <span className="ml-auto text-sm">🔒 Seguro</span>
            </div>
            <p className="mt-3 text-xs text-neutral-400">
              * Maqueta: el pago es simulado. No se procesan cobros reales.
            </p>
          </section>
        </div>

        {/* columna derecha: resumen */}
        <aside className="h-fit rounded-2xl border border-black/10 bg-neutral-50 p-6 lg:sticky lg:top-28">
          <h2 className="font-head text-lg font-bold">Resumen de tu orden</h2>
          <div className="mt-4 space-y-3">
            {lines.map((l) => (
              <div key={l.id} className="flex gap-3">
                <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-lg bg-white">
                  <Image src={l.product.images[0]} alt={l.product.name} fill sizes="56px" className="object-cover" />
                  <span className="absolute -right-1 -top-1 grid h-5 min-w-5 place-items-center rounded-full bg-carbon px-1 text-[10px] font-bold text-white">{l.qty}</span>
                </div>
                <div className="flex flex-1 flex-col justify-center">
                  <span className="line-clamp-1 text-sm font-medium">{l.product.name}</span>
                  {(l.color || l.size) && <span className="text-xs text-neutral-500">{[l.color, l.size].filter(Boolean).join(" · ")}</span>}
                </div>
                <span className="self-center text-sm font-semibold">{formatCLP(l.product.price * l.qty)}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 space-y-1.5 border-t border-black/10 pt-4 text-sm">
            <Row label="Subtotal" value={formatCLP(subtotal)} />
            <Row label="Envío" value={shipping === 0 ? "Gratis" : formatCLP(shipping)} />
            <div className="flex justify-between border-t border-dashed border-black/15 pt-3 text-lg font-bold">
              <span>Total</span><span className="text-balon">{formatCLP(total)}</span>
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary mt-5 w-full py-4 text-base disabled:opacity-60">
            {loading ? "Redirigiendo a Webpay…" : `Pagar con Webpay · ${formatCLP(total)}`}
          </button>
          <p className="mt-3 text-center text-xs text-neutral-400">Compra protegida · 🔒 conexión segura</p>
        </aside>
      </form>
    </div>
  );
}

function Field({ label, className = "", ...rest }: { label: string; className?: string } & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className={`flex flex-col gap-1.5 ${className}`}>
      <span className="text-sm font-medium text-carbon">{label}</span>
      <input {...rest} className="rounded-xl border border-black/15 px-4 py-2.5 text-sm outline-none transition focus:border-balon" />
    </label>
  );
}
function DeliveryOpt({ active, onClick, icon, title, desc }: { active: boolean; onClick: () => void; icon: string; title: string; desc: string }) {
  return (
    <button type="button" onClick={onClick}
      className={`flex items-center gap-3 rounded-xl border p-4 text-left transition ${active ? "border-balon bg-balon-50" : "border-black/15 hover:border-carbon"}`}>
      <span className="text-2xl">{icon}</span>
      <div>
        <div className="font-semibold">{title}</div>
        <div className="text-xs text-neutral-500">{desc}</div>
      </div>
      <span className={`ml-auto h-4 w-4 rounded-full border-2 ${active ? "border-balon bg-balon" : "border-neutral-300"}`} />
    </button>
  );
}
function Row({ label, value }: { label: string; value: string }) {
  return <div className="flex justify-between text-neutral-600"><span>{label}</span><span>{value}</span></div>;
}
