import { redirect } from "next/navigation";
import Link from "next/link";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import type { ProductoRow } from "../catalogo/buscar";
import PortalHeader from "../catalogo/portal-header";
import FavoritosClient from "./favoritos-client";

export const metadata = { title: "Favoritos | Comercial Solutions Mayorista" };

export default async function FavoritosPage() {
  const session = await auth();
  if (!session?.user) redirect("/login");
  const estado = (session.user as Record<string, unknown>).estado as string | undefined;
  if (estado !== "aprobado") redirect("/revision");

  const productos = await prisma.producto.findMany({
    where: { activo: true },
    select: {
      id: true, codigoAlila: true, nombre: true, categoria: true,
      precioT1: true, precioT2: true, precioT3: true, fotoUrl: true, activo: true, stock: true,
    },
    orderBy: { nombre: "asc" },
  });
  const rows: ProductoRow[] = productos.map((p) => ({ ...p, stock: p.stock }));

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", fontFamily: "var(--font)" }}>
      <PortalHeader nombre={session.user.name} />

      <main style={{ maxWidth: 1240, margin: "0 auto", padding: "26px 26px 60px" }}>
        <Link href="/catalogo" className="back" style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 18, color: "var(--ink-2)", fontWeight: 600, fontSize: 14 }}>
          <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6" /></svg>
          Volver al catálogo
        </Link>
        <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", color: "var(--ink)", margin: "0 0 22px" }}>
          Mis favoritos
        </h1>
        <FavoritosClient productos={rows} />
      </main>
    </div>
  );
}
