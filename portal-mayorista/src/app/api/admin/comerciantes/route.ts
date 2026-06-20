import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";

export async function POST(req: Request) {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin")
    return NextResponse.json({ error: "No autorizado" }, { status: 403 });

  const { id, accion } = await req.json();

  if (!id || !["aprobar", "rechazar"].includes(accion))
    return NextResponse.json({ error: "Datos inválidos" }, { status: 400 });

  const estado = accion === "aprobar" ? "aprobado" : "rechazado";

  await prisma.comerciante.update({
    where: { id },
    data: { estado },
  });

  return NextResponse.json({ ok: true });
}
