import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { puedeTransicionar, EstadoPedido } from "@/lib/pedido-estado";

// Error de stock que aborta la transacción y se traduce a 409.
class StockError extends Error {
  constructor(public nombre: string, public solicitado: number) {
    super("stock insuficiente");
  }
}

export async function POST(req: Request) {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin")
    return NextResponse.json({ error: "No autorizado" }, { status: 403 });

  const body = await req.json();
  const { id, a: estadoDestino, transportista, tracking } = body as {
    id: string;
    a: string;
    transportista?: string;
    tracking?: string;
  };

  if (!id || !estadoDestino)
    return NextResponse.json({ error: "Faltan parametros: id y a son obligatorios" }, { status: 400 });

  const pedido = await prisma.pedido.findUnique({
    where: { id },
    include: { items: true },
  });

  if (!pedido)
    return NextResponse.json({ error: "Pedido no encontrado" }, { status: 404 });

  if (!puedeTransicionar(pedido.estado as EstadoPedido, estadoDestino as EstadoPedido))
    return NextResponse.json(
      { error: "Transicion invalida: no se puede pasar de " + pedido.estado + " a " + estadoDestino },
      { status: 400 },
    );

  const datosPedido = {
    estado: estadoDestino as EstadoPedido,
    ...(transportista !== undefined && { transportista }),
    ...(tracking !== undefined && { tracking }),
  };

  try {
    await prisma.$transaction(async (tx) => {
      // validado: reservar stock de forma atómica y condicional. El UPDATE solo
      // afecta la fila si hay disponible (stock - reservado >= cantidad) o si
      // stock es null (sin tope). Dos validaciones concurrentes no sobre-reservan.
      if (estadoDestino === "validado") {
        for (const item of pedido.items) {
          const filas = await tx.$executeRaw`
            UPDATE "Producto"
            SET reservado = reservado + ${item.cantidad}
            WHERE id = ${item.productoId}
              AND (stock IS NULL OR stock - reservado >= ${item.cantidad})`;
          if (filas === 0) {
            const p = await tx.producto.findUnique({ where: { id: item.productoId } });
            throw new StockError(p?.nombre ?? item.productoId, item.cantidad);
          }
        }
      }

      // rechazar un pedido YA validado: liberar la reserva tomada.
      if (estadoDestino === "rechazado" && pedido.estado === "validado") {
        for (const item of pedido.items) {
          await tx.producto.update({
            where: { id: item.productoId },
            data: { reservado: { decrement: item.cantidad } },
          });
        }
      }

      await tx.pedido.update({ where: { id }, data: datosPedido });
    });
  } catch (e) {
    if (e instanceof StockError)
      return NextResponse.json(
        { error: `Stock insuficiente para "${e.nombre}" (solicitado ${e.solicitado})` },
        { status: 409 },
      );
    throw e;
  }

  return NextResponse.json({ ok: true });
}
