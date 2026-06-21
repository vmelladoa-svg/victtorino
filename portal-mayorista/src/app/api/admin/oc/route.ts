import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { puedeTransicionar, EstadoPedido } from "@/lib/pedido-estado";

export async function POST(req: Request) {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin")
    return NextResponse.json({ error: "No autorizado" }, { status: 403 });

  const body = await req.json();
  const { pedidoId } = body as { pedidoId: string };

  if (!pedidoId)
    return NextResponse.json({ error: "Falta pedidoId" }, { status: 400 });

  const pedido = await prisma.pedido.findUnique({ where: { id: pedidoId } });

  if (!pedido)
    return NextResponse.json({ error: "Pedido no encontrado" }, { status: 404 });

  if (!puedeTransicionar(pedido.estado as EstadoPedido, "oc_generada"))
    return NextResponse.json(
      { error: "Transición inválida: el pedido no está en estado válido para generar OC" },
      { status: 400 },
    );

  const numeroOc = `OC-${Date.now().toString(36).toUpperCase()}`;

  // Leer los items con datos del producto para saber cuáles tienen stock null
  const items = await prisma.pedidoItem.findMany({
    where: { pedidoId },
    include: { producto: true },
  });

  // Construir las operaciones de actualización de stock diferenciadas
  const stockOps = items.map((it) => {
    if (it.producto.stock !== null) {
      // Tiene stock registrado: descontar stock y liberar reserva
      return prisma.producto.update({
        where: { id: it.productoId },
        data: {
          reservado: { decrement: it.cantidad },
          stock: { decrement: it.cantidad },
        },
      });
    } else {
      // Sin stock registrado (null): solo liberar la reserva
      return prisma.producto.update({
        where: { id: it.productoId },
        data: {
          reservado: { decrement: it.cantidad },
        },
      });
    }
  });

  await prisma.$transaction([
    prisma.oC.create({
      data: {
        pedidoId,
        numeroOc,
        proveedor: "AlilaTop",
      },
    }),
    prisma.pedido.update({
      where: { id: pedidoId },
      data: { estado: "oc_generada" },
    }),
    ...stockOps,
  ]);

  // Devolver el número de OC y el detalle de items para comprar en AlilaTop
  const lineasOc = items.map((it) => ({
    codigoAlila: it.producto.codigoAlila,
    codigoProveedor: it.producto.codigoProveedor ?? null,
    nombre: it.producto.nombre,
    cantidad: it.cantidad,
    link1688: it.producto.link1688,
  }));

  return NextResponse.json({ ok: true, numeroOc, lineasOc });
}
