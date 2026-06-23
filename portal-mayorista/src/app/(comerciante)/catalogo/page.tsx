import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import BuscarCatalogo, { type ProductoRow } from "./buscar";
import PortalHeader from "./portal-header";
import PromoCarousel from "./promo-carousel";

export const metadata = { title: "Catálogo | Comercial Solutions Mayorista" };

export default async function CatalogoPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const session = await auth();
  if (!session?.user) redirect("/login");
  const estado = (session.user as Record<string, unknown>).estado as string | undefined;
  if (estado !== "aprobado") redirect("/revision");

  const sp = await searchParams;
  const q = sp?.q ?? "";

  const productos = await prisma.producto.findMany({
    where: { activo: true },
    select: {
      id: true, codigoAlila: true, nombre: true, categoria: true,
      precioT1: true, precioT2: true, precioT3: true, fotoUrl: true, activo: true, stock: true,
    },
    orderBy: { nombre: "asc" },
  });
  const rows: ProductoRow[] = productos.map((p) => ({ ...p, stock: p.stock }));

  const categorias = [
    ...new Set(
      rows.map((p) => p.categoria).filter((c): c is string => c != null && c.trim() !== "")
    ),
  ].sort();

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", fontFamily: "var(--font)" }}>
      <PortalHeader nombre={session.user.name} />

      <main style={{ maxWidth: 1240, margin: "0 auto", padding: "22px 26px 60px" }}>
        {/* Franja de campañas/promos */}
        <PromoCarousel />

        {/* Hero compact */}
        <section
          style={{
            background: "linear-gradient(135deg, var(--brand-tint), var(--surface) 78%)",
            border: "1px solid var(--brand-line)",
            borderRadius: "var(--radius)",
            padding: "24px 30px",
            marginBottom: 26,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 20,
            flexWrap: "wrap",
          }}
        >
          <div>
            <span className="badge badge-brand" style={{ marginBottom: 10, display: "inline-flex" }}>
              Reposición semanal · {rows.length} SKUs activos
            </span>
            <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", color: "var(--ink)", margin: 0 }}>
              Catálogo Mayorista
            </h1>
            <p style={{ fontSize: 15, color: "var(--ink-2)", lineHeight: 1.55, marginTop: 8, marginBottom: 0 }}>
              Precios escalonados por volumen — a mayor cantidad, mejor precio.
            </p>
          </div>
          <div style={{ display: "flex", gap: 28, flexWrap: "wrap" }}>
            {[
              { val: "16", label: "regiones con despacho" },
              { val: "24h", label: "validación de pago" },
              { val: "1 día", label: "reposición desde bodega" },
            ].map(({ val, label }) => (
              <div key={label} style={{ display: "flex", flexDirection: "column" }}>
                <strong className="mono" style={{ fontSize: 22, fontWeight: 800, color: "var(--brand-deep)" }}>
                  {val}
                </strong>
                <small style={{ fontSize: 12, color: "var(--ink-2)", fontWeight: 600, marginTop: 2 }}>
                  {label}
                </small>
              </div>
            ))}
          </div>
        </section>

        {/* Catálogo (client) */}
        <BuscarCatalogo productos={rows} categorias={categorias} initialQuery={q} />
      </main>

      <footer
        style={{
          maxWidth: 1240, margin: "0 auto", padding: "20px 26px",
          display: "flex", alignItems: "center", borderTop: "1px solid var(--line)",
        }}
      >
        <span className="mono" style={{ fontSize: 12.5, color: "var(--ink-3)" }}>
          2026 Trade Global Solutions SpA · RUT 78.103.712-5
        </span>
      </footer>
    </div>
  );
}
