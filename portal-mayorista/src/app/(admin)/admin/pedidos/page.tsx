import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import AccionesGenerarOc from "./acciones";

export const metadata = {
  title: "Pedidos | Admin · Trade Global",
};

function fmtClp(n: number) {
  return "$" + n.toLocaleString("es-CL");
}

function fmtFecha(d: Date) {
  return d.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function EstadoPill({ estado }: { estado: string }) {
  const mapa: Record<string, { cls: string; label: string }> = {
    pago_en_validacion: { cls: "adm-status adm-status-amber", label: "Pago en validación" },
    validado:           { cls: "adm-status adm-status-brand", label: "Validado"           },
    oc_generada:        { cls: "adm-status adm-status-brand", label: "OC generada"        },
    despachado:         { cls: "adm-status adm-status-ok",   label: "Despachado"          },
    entregado:          { cls: "adm-status adm-status-ok",   label: "Entregado"           },
    rechazado:          { cls: "adm-status adm-status-out",  label: "Rechazado"           },
  };
  const cfg = mapa[estado] ?? { cls: "adm-status adm-status-amber", label: estado };
  return <span className={cfg.cls}>{cfg.label}</span>;
}

function TruckIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="3" width="15" height="13" />
      <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
      <circle cx="5.5" cy="18.5" r="2.5" />
      <circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  );
}

function EmptyIcon() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" strokeLinejoin="round"
      style={{ opacity: 0.35 }}>
      <rect x="1" y="3" width="15" height="13" />
      <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
      <circle cx="5.5" cy="18.5" r="2.5" />
      <circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  );
}

export default async function PedidosAdminPage() {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin") redirect("/login");

  const pedidos = await prisma.pedido.findMany({
    where: { estado: "validado" },
    include: {
      comerciante: true,
      items: {
        include: { producto: true },
      },
      oc: true,
    },
    orderBy: { createdAt: "asc" },
  });

  return (
    <div className="adm-page">
      {/* Cabecera */}
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontSize: "20px", fontWeight: 800, display: "flex", alignItems: "center", gap: "9px" }}>
          <TruckIcon />
          Pedidos — Generar OC a AlilaTop
        </h2>
        <p style={{ fontSize: "13.5px", color: "var(--ink-2)", marginTop: "4px" }}>
          {pedidos.length > 0
            ? pedidos.length + " pedido" + (pedidos.length !== 1 ? "s" : "") + " validado" + (pedidos.length !== 1 ? "s" : "") + " esperando orden de compra"
            : "No hay pedidos validados pendientes"}
        </p>
      </div>

      {pedidos.length === 0 ? (
        <div className="panel panel-empty-big">
          <EmptyIcon />
          <h3>Sin pedidos validados</h3>
          <p>Cuando se valide el pago de un pedido, aparecerá aquí para generar la OC a AlilaTop.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {pedidos.map((pedido) => {
            const folio = pedido.id.slice(0, 8).toUpperCase();
            return (
              <div
                key={pedido.id}
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--line-2)",
                  borderRadius: "12px",
                  padding: "18px 20px",
                }}
              >
                {/* Cabecera del pedido */}
                <div style={{
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: "10px",
                  marginBottom: "14px",
                  paddingBottom: "14px",
                  borderBottom: "1px solid var(--line-2)",
                }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "3px" }}>
                      <span style={{
                        fontFamily: "var(--mono)",
                        fontWeight: 800,
                        fontSize: "15px",
                        color: "var(--ink)",
                      }}>
                        #{folio}
                      </span>
                      <EstadoPill estado={pedido.estado} />
                    </div>
                    <div style={{ fontSize: "12.5px", color: "var(--ink-2)" }}>
                      <strong>{pedido.comerciante.nombre}</strong>
                      {" · "}
                      {pedido.comerciante.email}
                      {" · "}
                      {fmtFecha(pedido.createdAt)}
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--ink-3)", marginTop: "2px" }}>
                      Región: {pedido.region}
                    </div>
                  </div>
                  <strong style={{
                    fontFamily: "var(--mono)",
                    fontSize: "17px",
                    color: "var(--ink)",
                  }}>
                    {fmtClp(pedido.total)}
                  </strong>
                </div>

                {/* Tabla de productos */}
                <div style={{ marginBottom: "14px" }}>
                  <p style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: ".06em",
                    color: "var(--ink-3)",
                    marginBottom: "8px",
                  }}>
                    Productos a comprar en AlilaTop
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
                    {pedido.items.map((it) => (
                      <div key={it.id} style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                        padding: "8px 10px",
                        background: "var(--surface-2)",
                        borderRadius: "8px",
                        border: "1px solid var(--line-2)",
                        fontSize: "13px",
                      }}>
                        <span style={{
                          fontFamily: "var(--mono)",
                          fontWeight: 700,
                          color: "var(--brand)",
                          minWidth: "90px",
                          fontSize: "12px",
                        }}>
                          {it.producto.codigoAlila ?? "—"}
                        </span>
                        <span style={{ flex: 1, color: "var(--ink)", fontWeight: 600 }}>
                          {it.producto.nombre}
                        </span>
                        <span style={{
                          fontFamily: "var(--mono)",
                          fontWeight: 700,
                          color: "var(--ink)",
                          fontSize: "13px",
                        }}>
                          ×{it.cantidad}
                        </span>
                        <span style={{
                          fontFamily: "var(--mono)",
                          fontSize: "12.5px",
                          color: "var(--ink-2)",
                        }}>
                          {fmtClp(it.subtotal)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Botón generar OC */}
                <AccionesGenerarOc
                  pedidoId={pedido.id}
                  folio={folio}
                  empresa={pedido.comerciante.nombre}
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
