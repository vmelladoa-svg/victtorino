import { notFound, redirect } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import type { Metadata } from "next";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import CartBadge from "../cart-badge";
import AgregarDesdeDetalle from "./agregar-desde-detalle";

/* ------------------------------------------------------------------ */
/*  Metadata dinámica                                                   */
/* ------------------------------------------------------------------ */
export async function generateMetadata(props: {
  params: Promise<{ codigo: string }>;
}): Promise<Metadata> {
  const params = await props.params;
  const prod = await prisma.producto.findUnique({
    where: { codigoAlila: params.codigo },
    select: { nombre: true },
  });
  return {
    title: prod
      ? `${prod.nombre} | Trade Global Mayorista`
      : "Producto | Trade Global Mayorista",
  };
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                             */
/* ------------------------------------------------------------------ */
function clp(n: number | null | undefined): string {
  if (n == null) return "Consultar";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(n);
}

/* ------------------------------------------------------------------ */
/*  Header del portal (mismo estilo que catalogo/page.tsx)             */
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
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
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
              alt="Trade Global Solutions"
              width={42}
              height={42}
              style={{ objectFit: "contain" }}
            />
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              lineHeight: 1.05,
            }}
          >
            <strong
              style={{ fontSize: 16, fontWeight: 800, color: "var(--ink)" }}
            >
              Trade Global
            </strong>
            <small
              style={{ fontSize: 11, color: "var(--ink-3)", fontWeight: 600 }}
            >
              Portal Mayorista
            </small>
          </div>
        </div>

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Carrito */}
        <CartBadge />

        {/* Usuario + cerrar sesión */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {nombre && (
            <span
              style={{ fontSize: 13.5, fontWeight: 600, color: "var(--ink-2)" }}
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
/*  Componente de foto principal (Server)                               */
/* ------------------------------------------------------------------ */
function FotoPrincipal({
  fotoUrl,
  nombre,
}: {
  fotoUrl: string | null;
  nombre: string;
}) {
  return (
    <div className="pdp-media">
      <div
        style={{
          height: 380,
          position: "relative",
          borderRadius: "var(--radius)",
          overflow: "hidden",
          border: "1px solid var(--line)",
          background: "#0e7cc414",
        }}
      >
        {fotoUrl ? (
          <Image
            src={fotoUrl}
            alt={nombre}
            fill
            sizes="(max-width: 768px) 100vw, 50vw"
            style={{ objectFit: "contain" }}
            unoptimized
          />
        ) : (
          <div
            style={{
              height: "100%",
              display: "grid",
              placeItems: "center",
            }}
          >
            <span
              style={{
                fontFamily: "var(--mono)",
                fontSize: "10.5px",
                fontWeight: 700,
                opacity: 0.55,
                letterSpacing: ".02em",
                color: "#0e7cc4",
              }}
            >
              sin foto
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Page (Server Component)                                             */
/* ------------------------------------------------------------------ */
type Props = { params: Promise<{ codigo: string }> };

export default async function ProductoDetallePage(props: Props) {
  // 1. Verificar sesión
  const session = await auth();
  if (!session?.user) {
    redirect("/login");
  }
  const estado = (session.user as Record<string, unknown>).estado as
    | string
    | undefined;
  if (estado !== "aprobado") {
    redirect("/revision");
  }

  // 2. Cargar producto (solo campos disponibles en el cliente generado actual)
  const params = await props.params;
  const prod = await prisma.producto.findUnique({
    where: { codigoAlila: params.codigo },
    select: {
      id: true,
      codigoAlila: true,
      nombre: true,
      categoria: true,
      precioT1: true,
      precioT2: true,
      precioT3: true,
      unidCaja: true,
      fotoUrl: true,
      link1688: true,
      stock: true,
      reservado: true,
    },
  });

  if (!prod) {
    notFound();
  }

  const sinStock = !prod.stock || prod.stock <= 0;

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
        {/* Botón volver */}
        <Link
          href="/catalogo"
          className="back"
          style={{ textDecoration: "none" }}
        >
          <svg
            width={16}
            height={16}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
          Volver al catálogo
        </Link>

        {/* Grid principal */}
        <div className="pdp-grid">
          {/* Columna izquierda: foto */}
          <FotoPrincipal fotoUrl={prod.fotoUrl} nombre={prod.nombre} />

          {/* Columna derecha: info */}
          <div className="pdp-info">
            {/* Tags: SKU + categoría + stock */}
            <div className="pdp-tags">
              <span className="pcard-sku mono">{prod.codigoAlila}</span>
              {prod.categoria && (
                <span className="badge badge-neutral">{prod.categoria}</span>
              )}
              {prod.stock != null && (
                <span
                  className={`badge ${sinStock ? "badge-out" : "badge-ok"}`}
                >
                  {sinStock ? "Sin stock" : "Stock disponible"}
                </span>
              )}
            </div>

            {/* Nombre */}
            <h1>{prod.nombre}</h1>

            {/* Datos adicionales */}
            {prod.unidCaja && (
              <div
                style={{
                  display: "flex",
                  gap: 20,
                  flexWrap: "wrap",
                  marginBottom: 4,
                  padding: "11px 14px",
                  background: "var(--surface-2)",
                  border: "1px solid var(--line)",
                  borderRadius: "var(--rs)",
                  fontSize: 13,
                  color: "var(--ink-2)",
                }}
              >
                <span>
                  <strong style={{ color: "var(--ink)" }}>
                    Unidades por caja:
                  </strong>{" "}
                  {prod.unidCaja}
                </span>
              </div>
            )}

            {/* Tabla de precios por volumen */}
            <div className="vol" style={{ margin: "20px 0" }}>
              <div className="vol-head">
                <svg
                  width={15}
                  height={15}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10" />
                </svg>
                <span>Precio por volumen (unitario)</span>
              </div>
              <div className="vol-tiers">
                <div className="vol-tier">
                  <small>1–5 unid.</small>
                  <strong className="mono">{clp(prod.precioT1)}</strong>
                </div>
                <div className="vol-tier">
                  <small>6–20 unid.</small>
                  <strong className="mono">{clp(prod.precioT2)}</strong>
                  {prod.precioT1 &&
                    prod.precioT2 &&
                    prod.precioT2 < prod.precioT1 && (
                      <span className="vol-save">
                        −
                        {Math.round(
                          (1 - prod.precioT2 / prod.precioT1) * 100
                        )}
                        %
                      </span>
                    )}
                </div>
                <div className="vol-tier" style={{ borderRight: 0 }}>
                  <small>21+ unid.</small>
                  <strong className="mono">{clp(prod.precioT3)}</strong>
                  {prod.precioT1 &&
                    prod.precioT3 &&
                    prod.precioT3 < prod.precioT1 && (
                      <span className="vol-save">
                        −
                        {Math.round(
                          (1 - prod.precioT3 / prod.precioT1) * 100
                        )}
                        %
                      </span>
                    )}
                </div>
              </div>
            </div>

            {/* Caja de compra */}
            <div className="pdp-buy">
              <AgregarDesdeDetalle
                prod={{
                  id: prod.id,
                  nombre: prod.nombre,
                  precioT1: prod.precioT1,
                  precioT2: prod.precioT2,
                  precioT3: prod.precioT3,
                  fotoUrl: prod.fotoUrl,
                  stock: prod.stock,
                }}
              />
              <div className="pdp-buy-notes">
                <span>
                  <svg
                    width={15}
                    height={15}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.8}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <rect x="1" y="3" width="15" height="13" />
                    <path d="M16 8h4l3 5v3h-7V8z" />
                    <circle cx="5.5" cy="18.5" r="2.5" />
                    <circle cx="18.5" cy="18.5" r="2.5" />
                  </svg>
                  Despacho a todo Chile
                </span>
                <span>
                  <svg
                    width={15}
                    height={15}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.8}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v6l4 2" />
                  </svg>
                  Validación de pago en 24–48h
                </span>
              </div>
            </div>
          </div>
        </div>
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
