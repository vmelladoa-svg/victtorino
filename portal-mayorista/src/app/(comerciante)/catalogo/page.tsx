import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import BuscarCatalogo, { type ProductoRow } from "./buscar";
import CartBadge from "./cart-badge";
import FavoritosLink from "./favoritos-link";
import Image from "next/image";
import Link from "next/link";

export const metadata = { title: "Catálogo | Comercial Solutions Mayorista" };

/* ------------------------------------------------------------------ */
/*  Header del portal                                                    */
/* ------------------------------------------------------------------ */
function PortalHeader({ nombre }: { nombre: string | null | undefined }) {
  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 40,
        background: "rgba(255,255,255,0.96)",
        backdropFilter: "blur(10px)",
        borderBottom: "1px solid var(--line)",
      }}
    >
      <div
        style={{
          maxWidth: 1240,
          margin: "0 auto",
          padding: "13px 26px",
          display: "flex",
          alignItems: "center",
          gap: 20,
        }}
      >
        {/* Logo (al inicio) */}
        <Link href="/catalogo" style={{ display: "flex", alignItems: "center", gap: 11, textDecoration: "none" }}>
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: "50%",
              overflow: "hidden",
              flexShrink: 0,
              display: "grid",
              placeItems: "center",
            }}
          >
            <Image
              src="/logo-clean.png"
              alt="Comercial Solutions"
              width={42}
              height={42}
              style={{ objectFit: "contain" }}
            />
          </div>
          <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.05 }}>
            <strong style={{ fontSize: 16, fontWeight: 800, color: "var(--ink)" }}>
              Comercial Solutions
            </strong>
            <small style={{ fontSize: 11, color: "var(--ink-3)", fontWeight: 600 }}>
              Portal Mayorista
            </small>
          </div>
        </Link>

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Favoritos + Carrito */}
        <FavoritosLink />
        <CartBadge />

        {/* Usuario + cerrar sesión */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {nombre && (
            <span
              style={{
                fontSize: 13.5,
                fontWeight: 600,
                color: "var(--ink-2)",
              }}
            >
              {nombre}
            </span>
          )}
          <Link
            href="/api/auth/signout"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "8px 14px",
              border: "1px solid var(--line)",
              borderRadius: "var(--rs)",
              fontSize: 13,
              fontWeight: 600,
              color: "var(--ink-2)",
              textDecoration: "none",
            }}
          >
            Cerrar sesión
          </Link>
        </div>
      </div>
    </header>
  );
}

/* ------------------------------------------------------------------ */
/*  Page (Server Component)                                             */
/* ------------------------------------------------------------------ */
export default async function CatalogoPage() {
  // 1. Verificar sesión
  const session = await auth();

  if (!session?.user) {
    redirect("/login");
  }

  const estado = (session.user as Record<string, unknown>).estado as string | undefined;

  if (estado !== "aprobado") {
    redirect("/revision");
  }

  // 2. Cargar productos activos
  const productos = await prisma.producto.findMany({
    where: { activo: true },
    select: {
      id: true,
      codigoAlila: true,
      nombre: true,
      categoria: true,
      precioT1: true,
      precioT2: true,
      precioT3: true,
      fotoUrl: true,
      activo: true,
      stock: true,
    },
    orderBy: { nombre: "asc" },
  });

  // Adaptar al tipo ProductoRow (stock real, descontando lo reservado se hace en backend)
  const rows: ProductoRow[] = productos.map((p) => ({
    ...p,
    stock: p.stock,
  }));

  // 3. Obtener categorías únicas (ordenadas, sin null)
  const categorias = [
    ...new Set(
      rows
        .map((p) => p.categoria)
        .filter((c): c is string => c != null && c.trim() !== "")
    ),
  ].sort();

  // 4. Renderizar
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg)",
        fontFamily: "var(--font)",
      }}
    >
      <PortalHeader nombre={session.user.name} />

      <main
        style={{
          maxWidth: 1240,
          margin: "0 auto",
          padding: "26px 26px 60px",
        }}
      >
        {/* Hero compact */}
        <section
          style={{
            background: "linear-gradient(135deg, var(--brand-tint), var(--surface) 78%)",
            border: "1px solid var(--brand-line)",
            borderRadius: "var(--radius)",
            padding: "28px 32px",
            marginBottom: 28,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 20,
            flexWrap: "wrap",
          }}
        >
          <div>
            <span
              className="badge badge-brand"
              style={{ marginBottom: 10, display: "inline-flex" }}
            >
              Reposición semanal · {rows.length} SKUs activos
            </span>
            <h1
              style={{
                fontSize: 28,
                fontWeight: 800,
                letterSpacing: "-0.02em",
                color: "var(--ink)",
                margin: 0,
              }}
            >
              Catálogo Mayorista
            </h1>
            <p
              style={{
                fontSize: 15,
                color: "var(--ink-2)",
                lineHeight: 1.55,
                marginTop: 8,
                marginBottom: 0,
              }}
            >
              Precios escalonados por volumen — a mayor cantidad, mejor precio.
            </p>
          </div>
          <div
            style={{
              display: "flex",
              gap: 28,
              flexWrap: "wrap",
            }}
          >
            {[
              { val: "16", label: "regiones con despacho" },
              { val: "24h", label: "validación de pago" },
              { val: "1 día", label: "reposición desde bodega" },
            ].map(({ val, label }) => (
              <div
                key={label}
                style={{ display: "flex", flexDirection: "column" }}
              >
                <strong
                  className="mono"
                  style={{
                    fontSize: 22,
                    fontWeight: 800,
                    color: "var(--brand-deep)",
                  }}
                >
                  {val}
                </strong>
                <small
                  style={{
                    fontSize: 12,
                    color: "var(--ink-2)",
                    fontWeight: 600,
                    marginTop: 2,
                  }}
                >
                  {label}
                </small>
              </div>
            ))}
          </div>
        </section>

        {/* Catálogo con buscador (client) */}
        <BuscarCatalogo productos={rows} categorias={categorias} />
      </main>

      <footer
        style={{
          maxWidth: 1240,
          margin: "0 auto",
          padding: "20px 26px",
          display: "flex",
          alignItems: "center",
          borderTop: "1px solid var(--line)",
        }}
      >
        <span
          className="mono"
          style={{ fontSize: 12.5, color: "var(--ink-3)" }}
        >
          2026 Trade Global Solutions SpA · RUT 78.103.712-5
        </span>
      </footer>
    </div>
  );
}
