import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { precioPorCantidad, subtotalLinea } from "@/lib/precios";
import { avisarWhatsApp } from "@/lib/whatsapp";
import { folio } from "@/lib/folio";
import { texto, cantidadValida } from "@/lib/validar";

export async function POST(req: Request) {
  const s = await auth();
  const u = s?.user as any;
  if (!u || u.rol !== "comerciante" || u.estado !== "aprobado")
    return NextResponse.json({ error: "no autorizado" }, { status: 403 });

  const b = await req.json().catch(() => null); // { region, direccion, comprobanteUrl, items:[{productoId, cantidad}] }
  if (!b || !b.region || !b.direccion || !b.comprobanteUrl || !Array.isArray(b.items) || !b.items.length)
    return NextResponse.json({ error: "datos incompletos" }, { status: 400 });

  // El comprobante debe ser un Blob de nuestro store, no una URL arbitraria.
  if (!/^https:\/\/[a-z0-9]+\.public\.blob\.vercel-storage\.com\//.test(String(b.comprobanteUrl)))
    return NextResponse.json({ error: "comprobante inválido" }, { status: 400 });

  const ids = b.items.map((i: any) => i.productoId);
  const prods = await prisma.producto.findMany({ where: { id: { in: ids }, activo: true } });
  const map = new Map(prods.map(p => [p.id, p]));

  let total = 0;
  const items = [];
  for (const i of b.items) {
    const p = map.get(i.productoId);
    if (!p) return NextResponse.json({ error: "Hay un producto inválido o sin stock en tu carrito" }, { status: 400 });
    let cant = cantidadValida(i.cantidad);
    if (cant == null) return NextResponse.json({ error: `Cantidad inválida para ${p.nombre}` }, { status: 400 });
    // Respetar compra mínima y múltiplo de caja del producto.
    if (cant < p.minCompra) cant = p.minCompra;
    if (p.unidCaja && p.unidCaja > 1) cant = Math.ceil(cant / p.unidCaja) * p.unidCaja;
    if (p.precioT1 == null && p.precioT2 == null && p.precioT3 == null)
      return NextResponse.json({ error: `${p.nombre} no tiene precio disponible` }, { status: 400 });
    const precio = precioPorCantidad(p, cant);
    const sub = subtotalLinea(p, cant);
    total += sub;
    items.push({ productoId: p.id, cantidad: cant, precioAplicado: precio, subtotal: sub });
  }

  const pedido = await prisma.pedido.create({ data: {
    comercianteId: u.id, estado: "pago_en_validacion", total,
    region: texto(b.region, 60), direccion: texto(b.direccion, 300), comprobanteUrl: String(b.comprobanteUrl),
    items: { create: items },
  }});
  await avisarWhatsApp(`Nuevo pedido mayorista #${folio(pedido.id)} por ${u.name}. Total $${total.toLocaleString("es-CL")}. Revisar comprobante en el panel.`);
  return NextResponse.json({ ok: true, pedidoId: pedido.id });
}
