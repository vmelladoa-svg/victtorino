import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { puedeTransicionar, EstadoPedido } from "@/lib/pedido-estado";
import { puedeReservar } from "@/lib/reserva";
import { enviarCorreo, tplPagoValidado, tplDespachado } from "@/lib/email";

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
    include: {
      items: {
        include: { producto: true },
      },
      comerciante: true,
    },
  });

  if (!pedido)
    return NextResponse.json({ error: "Pedido no encontrado" }, { status: 404 });

  if (!puedeTransicionar(pedido.estado as EstadoPedido, estadoDestino as EstadoPedido))
    return NextResponse.json(
      {
        error: "Transicion invalida: no se puede pasar de " + pedido.estado + " a " + estadoDestino,
      },
      { status: 400 },
    );

  // Si la transicion es hacia "validado", verificar stock y reservar en la misma transaccion
  if (estadoDestino === "validado") {
    const sinStock: Array<{ nombre: string; disponible: number; solicitado: number }> = [];

    for (const item of pedido.items) {
      const p = item.producto;
      const puedeRes = puedeReservar(p.stock, p.reservado, item.cantidad);
      if (!puedeRes) {
        const disponible = p.stock != null ? Math.max(0, p.stock - p.reservado) : 0;
        sinStock.push({
          nombre: p.nombre,
          disponible,
          solicitado: item.cantidad,
        });
      }
    }

    if (sinStock.length > 0) {
      return NextResponse.json(
        {
          error: "Stock insuficiente para validar el pago",
          detalle: sinStock,
        },
        { status: 409 },
      );
    }

    // Ejecutar transicion y reservas en la misma transaccion Prisma
    await prisma.$transaction([
      prisma.pedido.update({
        where: { id },
        data: {
          estado: estadoDestino as EstadoPedido,
          ...(transportista !== undefined && { transportista }),
          ...(tracking !== undefined && { tracking }),
        },
      }),
      ...pedido.items.map((item) =>
        prisma.producto.update({
          where: { id: item.productoId },
          data: { reservado: { increment: item.cantidad } },
        }),
      ),
    ]);
  } else {
    await prisma.pedido.update({
      where: { id },
      data: {
        estado: estadoDestino as EstadoPedido,
        ...(transportista !== undefined && { transportista }),
        ...(tracking !== undefined && { tracking }),
      },
    });
  }

  // Aviso por correo al comerciante (no bloquea ni rompe el flujo si falla)
  const email = pedido.comerciante.email;
  const nombre = pedido.comerciante.nombre;
  if (estadoDestino === "validado") {
    await enviarCorreo(email, "Pago confirmado — Comercial Solutions", tplPagoValidado(nombre, pedido.id, pedido.total));
  } else if (estadoDestino === "despachado") {
    await enviarCorreo(
      email,
      "Tu pedido fue despachado — Comercial Solutions",
      tplDespachado(nombre, pedido.id, transportista ?? pedido.transportista, tracking ?? pedido.tracking),
    );
  }

  return NextResponse.json({ ok: true });
}
