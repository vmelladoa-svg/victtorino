import { NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/db";
import { avisarWhatsApp } from "@/lib/whatsapp";
import { esEmail, esRut, texto } from "@/lib/validar";

export async function POST(req: Request) {
  const b = await req.json().catch(() => null);
  if (!b) return NextResponse.json({ error: "Datos inválidos" }, { status: 400 });

  for (const f of ["nombre", "email", "clave", "rutEmpresa", "giro", "region", "comuna", "telefono"])
    if (!b?.[f]) return NextResponse.json({ error: `Falta ${f}` }, { status: 400 });

  const email = texto(b.email, 120).toLowerCase();
  if (!esEmail(email)) return NextResponse.json({ error: "Email inválido" }, { status: 400 });
  if (!esRut(b.rutEmpresa)) return NextResponse.json({ error: "RUT de empresa inválido" }, { status: 400 });
  if (String(b.clave).length < 6) return NextResponse.json({ error: "La clave debe tener al menos 6 caracteres" }, { status: 400 });

  if (await prisma.comerciante.findUnique({ where: { email } }))
    return NextResponse.json({ error: "Ese email ya está registrado" }, { status: 409 });

  const nombre = texto(b.nombre, 120);
  await prisma.comerciante.create({
    data: {
      nombre,
      email,
      clave: await bcrypt.hash(String(b.clave), 10),
      rutEmpresa: texto(b.rutEmpresa, 20),
      giro: texto(b.giro, 120),
      region: texto(b.region, 60),
      comuna: texto(b.comuna, 60),
      telefono: texto(b.telefono, 30),
    },
  });

  await avisarWhatsApp(`Nuevo comerciante ${nombre} por aprobar.`);

  return NextResponse.json({ ok: true });
}
