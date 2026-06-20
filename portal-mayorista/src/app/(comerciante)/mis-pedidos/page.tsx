import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import Link from "next/link";
import Image from "next/image";

export const metadata = { title: "Mis pedidos | Trade Global Mayorista" };

/* -- Types -- */
type EstadoPedido =
  | "pago_en_validacion"
  | "validado"
  | "oc_generada"
  | "despachado"
  | "entregado"
  | "rechazado";

/* -- Helpers -- */
function clp(n: number): string {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(n);
}

function formatDate(d: Date): string {
  return new Intl.DateTimeFormat("es-CL", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(d);
}

/* -- Estado config -- */
type EstadoCfg = { label: string; bg: string; color: string };

const ESTADOS: Record<EstadoPedido, EstadoCfg> = {
  pago_en_validacion: { label: "Pago en validacion", bg: "var(--amber-t)", color: "var(--amber)" },
  validado:           { label: "Validado",            bg: "var(--brand-soft)", color: "var(--brand-ink)" },
  oc_generada:        { label: "OC generada",         bg: "var(--blue-t)", color: "var(--blue)" },
  despachado:         { label: "Despachado",          bg: "var(--blue-t)", color: "var(--blue)" },
  entregado:          { label: "Entregado",           bg: "var(--ok-t)", color: "var(--ok)" },
  rechazado:          { label: "Rechazado",           bg: "var(--out-t)", color: "var(--out)" },
};

// Human-readable with tildes (display only)
const ESTADO_LABEL: Record<EstadoPedido, string> = {
  pago_en_validacion: "Pago en validacion",
  validado:           "Validado",
  oc_generada:        "OC generada",
  despachado:         "Despachado",
  entregado:          "Entregado",
  rechazado:          "Rechazado",
};

/* -- Timeline steps -- */
const TL_STEPS: EstadoPedido[] = [
  "pago_en_validacion",
  "validado",
  "oc_generada",
  "despachado",
  "entregado",
];

/* -- Icons (inline SVG) -- */
function IconClock({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" />
    </svg>
  );
}
function IconCheck({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
function IconDoc({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}
function IconTruck({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="3" width="15" height="13" /><path d="M16 8h4l3 5v4h-7z" />
      <circle cx="5.5" cy="18.5" r="2.5" /><circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  );
}
function IconPackage({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10" />
    </svg>
  );
}
function IconX({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
function IconGrid() {
  return (
    <svg width={15} height={15} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
    </svg>
  );
}
function IconPin({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11z" />
      <circle cx="12" cy="10" r="2" />
    </svg>
  );
}

/* -- Step icon by estado -- */
function StepIcon({ estado, size = 14 }: { estado: EstadoPedido; size?: number }) {
  switch (estado) {
    case "pago_en_validacion": return <IconClock size={size} />;
    case "validado":           return <IconCheck size={size} />;
    case "oc_generada":        return <IconDoc   size={size} />;
    case "despachado":         return <IconTruck size={size} />;
    case "entregado":          return <IconPackage size={size} />;
    case "rechazado":          return <IconX size={size} />;
  }
}

/* -- Badge -- */
function Badge({ estado }: { estado: EstadoPedido }) {
  const cfg = ESTADOS[estado];
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      fontSize: 11.5, fontWeight: 700,
      padding: "4px 9px", borderRadius: 100, lineHeight: 1, whiteSpace: "nowrap",
      background: cfg.bg, color: cfg.color,
    }}>
      <StepIcon estado={estado} size={12} />
      {ESTADO_LABEL[estado]}
    </span>
  );
}

/* -- Timeline -- */
function OrderTimeline({ estado }: { estado: EstadoPedido }) {
  if (estado === "rechazado") {
    return (
      <div style={{
        display: "flex", alignItems: "center", gap: 10,
        padding: "14px 16px", borderRadius: "var(--rs)",
        background: "var(--out-t)", color: "var(--out)",
        fontSize: 13.5, fontWeight: 600,
      }}>
        <IconX size={16} />
        Este pedido fue rechazado. Contacta a soporte si tienes consultas.
      </div>
    );
  }

  const currentIdx = TL_STEPS.indexOf(estado);

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      {TL_STEPS.map((step, i) => {
        const cfg = ESTADOS[step];
        const done    = i < currentIdx;
        const current = i === currentIdx;
        const isLast  = i === TL_STEPS.length - 1;

        const markerBg     = done ? "var(--ok)" : current ? "var(--brand)" : "var(--surface)";
        const markerBorder = done ? "var(--ok)" : current ? "var(--brand)" : "var(--line)";
        const markerColor  = (done || current) ? "#fff" : "var(--ink-3)";

        const stepDescriptions: Record<EstadoPedido, string> = {
          pago_en_validacion: "Recibimos tu comprobante. Estamos verificando la transferencia.",
          validado:           "Transferencia validada. Compramos al importador y preparamos tu pedido.",
          oc_generada:        "Orden de compra emitida al importador. Tu pedido esta en preparacion.",
          despachado:         "Tu pedido salio a ruta con el transportista hacia tu region.",
          entregado:          "Pedido entregado en la direccion indicada.",
          rechazado:          "",
        };

        return (
          <div key={step} style={{
            display: "grid", gridTemplateColumns: "34px 1fr",
            gap: 14, paddingBottom: isLast ? 0 : 22, position: "relative",
          }}>
            {!isLast && (
              <div style={{
                position: "absolute", left: 16, top: 34, bottom: 0, width: 2,
                background: done ? "var(--ok)" : "var(--line)",
              }} />
            )}

            <div style={{
              width: 34, height: 34, borderRadius: "50%",
              display: "grid", placeItems: "center", zIndex: 1,
              background: markerBg, border: `2px solid ${markerBorder}`,
              color: markerColor,
              boxShadow: current ? "0 0 0 5px var(--brand-tint)" : "none",
            }}>
              <StepIcon estado={step} size={14} />
            </div>

            <div style={{ paddingTop: 5 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <strong style={{
                  fontSize: 14.5,
                  fontWeight: (current || done) ? 700 : 600,
                  color: (current || done) ? "var(--ink)" : "var(--ink-3)",
                }}>
                  {ESTADO_LABEL[step]}
                </strong>
                {current && (
                  <span style={{
                    display: "inline-flex", alignItems: "center", gap: 5,
                    fontSize: 11.5, fontWeight: 700, padding: "3px 8px",
                    borderRadius: 100, background: cfg.bg, color: cfg.color,
                  }}>
                    Estado actual
                  </span>
                )}
                {done && (
                  <span style={{ fontSize: 12, color: "var(--ink-3)" }}>&#10003;</span>
                )}
              </div>
              {(current || done) && (
                <p style={{ fontSize: 13, color: "var(--ink-2)", lineHeight: 1.5, margin: "5px 0 0" }}>
                  {stepDescriptions[step]}
                </p>
              )}
              {current && step === "pago_en_validacion" && (
                <span style={{
                  display: "inline-flex", alignItems: "center", gap: 6,
                  fontSize: 12, fontWeight: 600, color: "var(--brand-deep)", marginTop: 7,
                }}>
                  <IconClock size={13} /> Validacion estimada: 24-48h habiles
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* -- Order Card -- */
type PedidoConItems = Awaited<ReturnType<typeof fetchPedidos>>[number];

function OrderCard({ pedido }: { pedido: PedidoConItems }) {
  const estado = pedido.estado as EstadoPedido;
  const showTracking = estado === "despachado" || estado === "entregado";

  return (
    <details style={{
      background: "var(--surface)", border: "1px solid var(--line)",
      borderRadius: "var(--radius)", overflow: "hidden",
    }}>
      <summary style={{
        width: "100%", display: "flex", alignItems: "center",
        justifyContent: "space-between", gap: 16, padding: "16px 20px",
        cursor: "pointer", listStyle: "none", userSelect: "none",
      }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
          <span style={{
            fontSize: 15, fontWeight: 700, color: "var(--ink)",
            fontFamily: "var(--mono)", letterSpacing: "-0.02em",
          }}>
            {pedido.id.slice(0, 8).toUpperCase()}
          </span>
          <small style={{ fontSize: 12, color: "var(--ink-3)" }}>
            {formatDate(pedido.createdAt)} &middot; {pedido.items.length}{" "}
            {pedido.items.length === 1 ? "producto" : "productos"}
          </small>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <Badge estado={estado} />
          <strong style={{
            fontSize: 16, fontWeight: 800, minWidth: 90, textAlign: "right",
            fontFamily: "var(--mono)", letterSpacing: "-0.02em",
          }}>
            {clp(pedido.total)}
          </strong>
          <svg width={18} height={18} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
            style={{ color: "var(--ink-3)", flexShrink: 0 }}>
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </summary>

      <div style={{ padding: "6px 20px 22px", borderTop: "1px solid var(--line)" }}>
        <div style={{
          display: "grid", gridTemplateColumns: "1fr 320px",
          gap: 28, paddingTop: 18,
        }}>
          {/* Timeline */}
          <div>
            <OrderTimeline estado={estado} />
          </div>

          {/* Sidebar */}
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

            {/* Productos */}
            <div style={{
              background: "var(--surface-2)", border: "1px solid var(--line)",
              borderRadius: "var(--rs)", padding: 14,
            }}>
              <span style={{
                fontSize: 11.5, fontWeight: 800, textTransform: "uppercase",
                letterSpacing: "0.04em", color: "var(--ink-3)", display: "block", marginBottom: 11,
              }}>
                Productos
              </span>
              {pedido.items.map((item) => (
                <div key={item.id} style={{
                  display: "grid", gridTemplateColumns: "1fr auto",
                  gap: 11, alignItems: "start", marginBottom: 10,
                }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "var(--ink)" }}>
                      {item.producto.nombre}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--ink-3)", marginTop: 2 }}>
                      {item.cantidad} u. &middot; {clp(item.precioAplicado)} c/u
                    </div>
                  </div>
                  <span style={{
                    fontSize: 13, fontWeight: 700, color: "var(--ink)", fontFamily: "var(--mono)",
                  }}>
                    {clp(item.subtotal)}
                  </span>
                </div>
              ))}
            </div>

            {/* Despacho + tracking */}
            <div style={{
              background: "var(--surface-2)", border: "1px solid var(--line)",
              borderRadius: "var(--rs)", padding: 14,
            }}>
              <span style={{
                fontSize: 11.5, fontWeight: 800, textTransform: "uppercase",
                letterSpacing: "0.04em", color: "var(--ink-3)", display: "block", marginBottom: 11,
              }}>
                Despacho
              </span>

              <div style={{
                display: "flex", alignItems: "center",
                fontSize: 13, color: "var(--ink-2)", marginBottom: 7,
              }}>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 7 }}>
                  <IconPin /> {pedido.region}
                </span>
              </div>

              <div style={{
                display: "flex", alignItems: "flex-start", justifyContent: "space-between",
                fontSize: 13, color: "var(--ink-2)", marginBottom: 7,
              }}>
                <span style={{ color: "var(--ink-3)", flexShrink: 0, marginRight: 8 }}>Direccion</span>
                <span style={{ textAlign: "right" }}>{pedido.direccion}</span>
              </div>

              {showTracking && (
                <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--line)" }}>
                  {pedido.transportista && (
                    <div style={{
                      display: "flex", justifyContent: "space-between",
                      fontSize: 13, color: "var(--ink-2)", marginBottom: 7,
                    }}>
                      <span style={{ color: "var(--ink-3)" }}>Transportista</span>
                      <strong style={{ color: "var(--ink)" }}>{pedido.transportista}</strong>
                    </div>
                  )}
                  {pedido.tracking && (
                    <div style={{
                      display: "flex", justifyContent: "space-between",
                      fontSize: 13, color: "var(--ink-2)",
                    }}>
                      <span style={{ color: "var(--ink-3)" }}>N de seguimiento</span>
                      <strong style={{
                        color: "var(--brand-deep)", fontFamily: "var(--mono)",
                        letterSpacing: "-0.02em",
                      }}>
                        {pedido.tracking}
                      </strong>
                    </div>
                  )}
                  {!pedido.transportista && !pedido.tracking && (
                    <p style={{ fontSize: 12.5, color: "var(--ink-3)", margin: 0 }}>
                      Informacion de seguimiento pendiente.
                    </p>
                  )}
                </div>
              )}

              <div style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                paddingTop: 10, borderTop: "1px solid var(--line)", marginTop: 10,
                fontWeight: 700, fontSize: 13, color: "var(--ink)",
              }}>
                <span>Total pagado</span>
                <strong style={{ fontFamily: "var(--mono)", letterSpacing: "-0.02em" }}>
                  {clp(pedido.total)}
                </strong>
              </div>
            </div>

          </div>
        </div>
      </div>
    </details>
  );
}

/* -- Data -- */
async function fetchPedidos(comercianteId: string) {
  return prisma.pedido.findMany({
    where: { comercianteId },
    orderBy: { createdAt: "desc" },
    include: {
      items: {
        include: { producto: true },
      },
    },
  });
}

/* -- Page -- */
export default async function MisPedidosPage() {
  const session = await auth();
  if (!session?.user) redirect("/login");

  const uid = (session.user as any).id as string;
  const pedidos = await fetchPedidos(uid);

  return (
    <div style={{
      minHeight: "100vh", background: "var(--bg)",
      fontFamily: "var(--font, 'Plus Jakarta Sans', system-ui, sans-serif)",
    }}>
      {/* Header */}
      <header style={{
        position: "sticky", top: 0, zIndex: 40,
        background: "rgba(255,255,255,0.96)", backdropFilter: "blur(10px)",
        borderBottom: "1px solid var(--line)",
      }}>
        <div style={{
          maxWidth: 1240, margin: "0 auto", padding: "13px 26px",
          display: "flex", alignItems: "center", gap: 20,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
            <div style={{
              width: 42, height: 42, borderRadius: "50%", overflow: "hidden",
              flexShrink: 0, display: "grid", placeItems: "center",
            }}>
              <Image src="/logo-clean.png" alt="Trade Global Solutions" width={42} height={42}
                style={{ objectFit: "contain" }} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.05 }}>
              <strong style={{ fontSize: 16, fontWeight: 800, color: "var(--ink)" }}>Trade Global</strong>
              <small style={{ fontSize: 11, color: "var(--ink-3)", fontWeight: 600 }}>Solutions &middot; Mayorista</small>
            </div>
          </div>
          <div style={{ flex: 1 }} />
          <Link href="/catalogo" style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            color: "var(--ink-2)", fontWeight: 600,
            fontSize: 13.5, padding: "9px 11px", borderRadius: "var(--rs)",
            textDecoration: "none",
          }}>
            <IconGrid /> Catalogo
          </Link>
        </div>
      </header>

      {/* Main */}
      <main style={{ maxWidth: 1240, margin: "0 auto", padding: "30px 26px 60px" }}>
        <div style={{ marginBottom: 22 }}>
          <h1 style={{
            fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em",
            color: "var(--ink)", margin: "6px 0 0",
          }}>
            Mis pedidos
          </h1>
        </div>

        {pedidos.length === 0 ? (
          <div style={{
            textAlign: "center", padding: "90px 20px",
            display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
          }}>
            <div style={{ color: "var(--ink-3)", marginBottom: 12 }}>
              <IconTruck size={34} />
            </div>
            <h2 style={{ fontSize: 22, fontWeight: 800, color: "var(--ink)", marginTop: 8 }}>
              Aun no tienes pedidos
            </h2>
            <p style={{
              fontSize: 14.5, maxWidth: 380, marginBottom: 14,
              color: "var(--ink-2)", lineHeight: 1.6,
            }}>
              Cuando completes una compra, aqui podras seguir su estado: validacion, despacho y entrega.
            </p>
            <Link href="/catalogo" style={{
              display: "inline-flex", alignItems: "center", gap: 7,
              padding: "11px 20px", background: "var(--brand)", color: "#fff",
              borderRadius: "var(--rs)", fontWeight: 700, fontSize: 14,
              textDecoration: "none",
            }}>
              <IconGrid /> Ir al catalogo
            </Link>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {pedidos.map((pedido) => (
              <OrderCard key={pedido.id} pedido={pedido} />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        maxWidth: 1240, margin: "0 auto", padding: 26,
        display: "flex", alignItems: "center", gap: 18,
        borderTop: "1px solid var(--line)", flexWrap: "wrap",
      }}>
        <span style={{ fontSize: 12.5, color: "var(--ink-3)" }}>
          Trade Global Solutions SpA &middot; Portal Mayorista
        </span>
        <span style={{
          fontSize: 12.5, color: "var(--ink-3)", marginLeft: "auto",
          fontFamily: "var(--mono)",
        }}>
          {new Date().getFullYear()}
        </span>
      </footer>
    </div>
  );
}
