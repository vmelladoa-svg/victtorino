import { notFound, redirect } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import type { Metadata } from "next";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import CartBadge from "../cart-badge";
import AgregarDesdeDetalle from "./agregar-desde-detalle";
import GaleriaFotos from "./galeria-fotos";

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
      ? `${prod.nombre} | Comercial Solutions Mayorista`
      : "Producto | Comercial Solutions Mayorista",
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
              alt="Comercial Solutions"
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
              Comercial Solutions
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

  // 2. Cargar producto
  const params = await props.params;
  const prod = await prisma.producto.findUnique({
    where: { codigoAlila: params.codigo },
    select: {
      id: true,
      codigoAlila: true,
      nombre: true,
      categoria: true,
      descripcion: true,
      fotos: true,
      fotoUrl: true,
      dimensiones: true,
      embalaje: true,
      unidCaja: true,
      precioT1: true,
      precioT2: true,
      precioT3: true,
      link1688: true,
      stock: true,
      reservado: true,
    },
  });

  if (!prod) {
    notFound();
  }

  const sinStock = !prod.stock || prod.stock <= 0;

  // Compartir por WhatsApp (sin número => abre el selector de contactos)
  const shareUrl = `https://comercialsolutions.cl/catalogo/${prod.codigoAlila}`;
  const precioDesde = prod.precioT3 ?? prod.precioT2 ?? prod.precioT1;
  const waText =
    `${prod.nombre}` +
    (precioDesde ? `\nDesde ${clp(precioDesde)} c/u (precio mayorista)` : "") +
    `\n${shareUrl}`;
  const waHref = `https://wa.me/?text=${encodeURIComponent(waText)}`;

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
          {/* Columna izquierda: galería */}
          {prod.fotos && prod.fotos.length > 0 ? (
            <GaleriaFotos fotos={prod.fotos} nombre={prod.nombre} />
          ) : (
            <FotoPrincipal fotoUrl={prod.fotoUrl} nombre={prod.nombre} />
          )}

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

            {/* Descripción HTML */}
            {prod.descripcion && (
              <div
                className="pdp-desc"
                dangerouslySetInnerHTML={{ __html: prod.descripcion }}
              />
            )}

            {/* Datos adicionales: dimensiones, embalaje, unidCaja */}
            {(prod.dimensiones || prod.embalaje || prod.unidCaja) && (
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
                {prod.dimensiones && (
                  <span>
                    <strong style={{ color: "var(--ink)" }}>Dimensiones:</strong>{" "}
                    {prod.dimensiones}
                  </span>
                )}
                {prod.embalaje && (
                  <span>
                    <strong style={{ color: "var(--ink)" }}>Embalaje:</strong>{" "}
                    {prod.embalaje}
                  </span>
                )}
                {prod.unidCaja && (
                  <span>
                    <strong style={{ color: "var(--ink)" }}>
                      Unidades por caja:
                    </strong>{" "}
                    {prod.unidCaja}
                  </span>
                )}
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
                  Validación de pago en 24h
                </span>
              </div>
              <a
                href={waHref}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 9,
                  width: "100%",
                  marginTop: 12,
                  padding: "12px 18px",
                  borderRadius: "var(--rs)",
                  background: "#25D366",
                  color: "#fff",
                  fontWeight: 700,
                  fontSize: 14.5,
                  textDecoration: "none",
                  fontFamily: "inherit",
                }}
              >
                <svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M.057 24l1.687-6.163a11.867 11.867 0 01-1.587-5.945C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 018.413 3.488 11.824 11.824 0 013.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 01-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 001.51 5.26l-.999 3.648 3.737-.979.741.272zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z" />
                </svg>
                Compartir por WhatsApp
              </a>
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
