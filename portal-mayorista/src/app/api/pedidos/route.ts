import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { precioPorCantidad, subtotalLinea } from "@/lib/precios";
import { avisarWhatsApp } from "@/lib/whatsapp";

export async function POST(req: Request) {
  const s = await auth();
  const u = s?.user as any;
  if (!u || u.rol !== "comerciante" || u.estado !== "aprobado")
    return NextResponse.json({ error: "no autorizado" }, { status: 403 });
  const b = await req.json(); // { region, direccion, comprobanteUrl, items:[{productoId, cantidad}] }
  if (!b.region || !b.direccion || !b.comprobanteUrl || !b.items?.length)
    return NextResponse.json({ error: "datos incompletos" }, { status: 400 });

  const ids = b.items.map((i: any) => i.productoId);
  const prods = await prisma.producto.findMany({ where: { id: { in: ids }, activo: true } });
  const map = new Map(prods.map(p => [p.id, p]));
  let total = 0;
  const items = b.items.map((i: any) => {
    const p = map.get(i.productoId); if (!p) throw new Error("producto inválido");
    const cant = Math.max(1, Math.floor(i.cantidad));
    const precio = precioPorCantidad(p, cant);
    const sub = subtotalLinea(p, cant);
    total += sub;
    return { productoId: p.id, cantidad: cant, precioAplicado: precio, subtotal: sub };
  });

  const pedido = await prisma.pedido.create({ data: {
    comercianteId: u.id, estado: "pago_en_validacion", total,
    region: b.region, direccion: b.direccion, comprobanteUrl: b.comprobanteUrl,
    items: { create: items },
  }});
  avisarWhatsApp(`Nuevo pedido mayorista #${pedido.id.slice(-6)} por ${u.name}. Total ${total}. Revisar comprobante en el panel.`);
  return NextResponse.json({ ok: true, pedidoId: pedido.id });
}
