import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";

// Devuelve los datos de envío que el comerciante ya dio en el registro,
// para pre-llenar el checkout y no volver a pedírselos.
export async function GET() {
  const session = await auth();
  const uid = (session?.user as { id?: string } | undefined)?.id;
  if (!uid || uid === "admin") {
    return NextResponse.json({ region: "", comuna: "" });
  }
  const c = await prisma.comerciante.findUnique({
    where: { id: uid },
    select: { region: true, comuna: true },
  });
  return NextResponse.json({ region: c?.region ?? "", comuna: c?.comuna ?? "" });
}
