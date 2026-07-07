import { NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/db";
import { avisarWhatsApp } from "@/lib/whatsapp";
import { sincronizarLeadHubSpot } from "@/lib/hubspot";
import { enviarBienvenida } from "@/lib/email";
import { esEmail, esRut, texto } from "@/lib/validar";
import { permitir, ipDe } from "@/lib/rate-limit";

export async function POST(req: Request) {
  if (!(await permitir(`registro:${ipDe(req)}`, 5, 60)))
    return NextResponse.json({ error: "Demasiados registros. Intenta más tarde." }, { status: 429 });

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
  const rutEmpresa = texto(b.rutEmpresa, 20);
  const giro = texto(b.giro, 120);
  const region = texto(b.region, 60);
  const comuna = texto(b.comuna, 60);
  const telefono = texto(b.telefono, 30);

  await prisma.comerciante.create({
    data: {
      nombre,
      email,
      clave: await bcrypt.hash(String(b.clave), 10),
      rutEmpresa,
      giro,
      region,
      comuna,
      telefono,
      estado: "pendiente", // requiere aprobación manual del admin (con evaluación)
    },
  });

  // Avisos externos en paralelo; ninguno bloquea ni falla el registro.
  await Promise.allSettled([
    avisarWhatsApp(`Nuevo comerciante registrado: ${nombre} — pendiente de aprobación. Revísalo en el panel.`),
    sincronizarLeadHubSpot({ email, nombre, telefono, giro, comuna, region, rutEmpresa }),
    enviarBienvenida({ email, nombre }),
  ]);

  return NextResponse.json({ ok: true });
}
