import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";

// Guarda la evaluación manual de un comerciante: ajuste de score, tier fijado a
// mano (opcional) y notas. Solo admin. El score automático NO se guarda: se
// recalcula en vivo desde los pedidos.
export async function POST(req: Request) {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin")
    return NextResponse.json({ error: "No autorizado" }, { status: 403 });

  const b = await req.json().catch(() => null);
  if (!b?.id) return NextResponse.json({ error: "Falta id" }, { status: 400 });

  // Ajuste de score: entero acotado a -100..100.
  const ajusteRaw = Number(b.scoreAjuste);
  const scoreAjuste = Number.isFinite(ajusteRaw)
    ? Math.max(-100, Math.min(100, Math.round(ajusteRaw)))
    : 0;

  // Tier manual: solo A/B/C, o null para volver al derivado del score.
  const tierManual = ["A", "B", "C"].includes(b.tierManual) ? b.tierManual : null;

  // Notas: texto libre acotado.
  const notaEval =
    typeof b.notaEval === "string" ? b.notaEval.trim().slice(0, 500) || null : null;

  const existe = await prisma.comerciante.findUnique({ where: { id: b.id }, select: { id: true } });
  if (!existe) return NextResponse.json({ error: "Comerciante no encontrado" }, { status: 404 });

  await prisma.comerciante.update({
    where: { id: b.id },
    data: { scoreAjuste, tierManual, notaEval, evaluadoAt: new Date() },
  });

  return NextResponse.json({ ok: true });
}
