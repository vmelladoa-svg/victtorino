"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useCart, cartSubtotal } from "@/lib/store";
import { formatCLP } from "@/lib/format";
import { commitWebpayTransaction } from "@/lib/payments/transbank";

export default function ConfirmacionPage() {
  const clear = useCart((s) => s.clear);
  const subtotalNow = useCart(cartSubtotal);
  const [order, setOrder] = useState<{ total: number; code: string; auth?: string; last4?: string } | null>(null);

  useEffect(() => {
    // capturamos el total antes de vaciar el carrito
    const total = subtotalNow;
    (async () => {
      // En producción: leer el token del query (?token_ws=) y confirmar:
      const res = await commitWebpayTransaction("MOCK_TOKEN");
      setOrder({ total, code: res.buyOrder, auth: res.authorizationCode, last4: res.cardLast4 });
      clear();
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="container-db grid place-items-center py-20 text-center">
      <div className="w-full max-w-lg rounded-3xl border border-black/10 p-10 shadow-card">
        <div className="mx-auto grid h-20 w-20 place-items-center rounded-full bg-cancha/10 text-5xl">✅</div>
        <h1 className="display mt-5 text-4xl">¡Pago confirmado!</h1>
        <p className="mt-2 text-neutral-500">Gracias por tu compra en Don Balón. Te enviamos el detalle a tu correo.</p>

        <div className="mt-7 space-y-2 rounded-2xl bg-neutral-50 p-5 text-left text-sm">
          <Row label="N° de orden" value={order?.code ?? "—"} />
          <Row label="Total pagado" value={order ? formatCLP(order.total) : "—"} />
          <Row label="Medio de pago" value="Webpay · Transbank" />
          {order?.auth && <Row label="Cód. autorización" value={order.auth} />}
          {order?.last4 && <Row label="Tarjeta" value={`•••• ${order.last4}`} />}
          <Row label="Estado" value="Aprobado ✓" />
        </div>

        <div className="mt-4 rounded-xl bg-balon-50 p-3 text-xs text-carbon">
          🧪 Esto es una <b>maqueta</b>: el pago fue simulado, no se realizó ningún cobro real.
        </div>

        <Link href="/" className="btn-primary mt-7 w-full py-3.5">Volver al inicio</Link>
        <Link href="/catalogo" className="mt-2 block text-sm text-neutral-500 hover:text-carbon">Seguir comprando</Link>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return <div className="flex justify-between"><span className="text-neutral-500">{label}</span><span className="font-semibold">{value}</span></div>;
}
