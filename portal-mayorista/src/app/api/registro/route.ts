import { NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/db";
import { avisarWhatsApp } from "@/lib/whatsapp";

export async function POST(req: Request) {
  const b = await req.json();
  for (const f of ["nombre", "email", "clave", "rutEmpresa", "giro", "region", "comuna", "telefono"])
    if (!b?.[f]) return NextResponse.json({ error: `Falta ${f}` }, { status: 400 });

  const email = String(b.email).toLowerCase();
  if (await prisma.comerciante.findUnique({ where: { email } }))
    return NextResponse.json({ error: "Email ya registrado" }, { status: 409 });

  await prisma.comerciante.create({
    data: {
      nombre: b.nombre,
      email,
      clave: await bcrypt.hash(b.clave, 10),
      rutEmpresa: b.rutEmpresa,
      giro: b.giro,
      region: b.region,
      comuna: b.comuna,
      telefono: b.telefono,
    },
  });

  await avisarWhatsApp(`Nuevo comerciante ${b.nombre} por aprobar.`);

  return NextResponse.json({ ok: true });
}
