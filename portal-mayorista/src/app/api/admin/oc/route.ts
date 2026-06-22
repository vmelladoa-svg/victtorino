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

  // numeroOc único: timestamp + sufijo aleatorio (evita colisión por milisegundo,
  // que con numeroOc @unique sería un error duro).
  const numeroOc = `OC-${Date.now().toString(36).toUpperCase()}-${crypto.randomUUID().slice(0, 4).toUpperCase()}`;

  // Leer los items con datos del producto (para las líneas de la OC)
  const items = await prisma.pedidoItem.findMany({
    where: { pedidoId },
    include: { producto: true },
  });

  await prisma.$transaction(async (tx) => {
    await tx.oC.create({ data: { pedidoId, numeroOc, proveedor: "AlilaTop" } });
    await tx.pedido.update({ where: { id: pedidoId }, data: { estado: "oc_generada" } });
    // Liberar reserva y descontar stock en una sola sentencia por ítem, fresca
    // contra la fila actual: si stock es null se mantiene null (sin tope);
    // si es número se descuenta. Los CHECK de BD impiden quedar negativo.
    for (const it of items) {
      await tx.$executeRaw`
        UPDATE "Producto"
        SET reservado = reservado - ${it.cantidad},
            stock = CASE WHEN stock IS NULL THEN stock ELSE stock - ${it.cantidad} END
        WHERE id = ${it.productoId}`;
    }
  });

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
