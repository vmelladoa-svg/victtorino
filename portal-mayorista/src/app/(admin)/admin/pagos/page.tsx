import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import AccionesPago from "./acciones";

export const metadata = {
  title: "Pagos por validar | Admin · Trade Global",
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

function DocIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

function CheckBigIcon() {
  return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  );
}

export default async function PagosAdminPage() {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin") redirect("/login");

  const pedidos = await prisma.pedido.findMany({
    where: { estado: "pago_en_validacion" },
    include: {
      comerciante: true,
      items: {
        include: { producto: true },
      },
    },
    orderBy: { createdAt: "asc" },
  });

  return (
    <div className="adm-page">
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontSize: "20px", fontWeight: 800, display: "flex", alignItems: "center", gap: "9px" }}>
          <DocIcon />
          Pagos por validar
        </h2>
        <p style={{ fontSize: "13.5px", color: "var(--ink-2)", marginTop: "4px" }}>
          {pedidos.length > 0
            ? pedidos.length + " comprobante" + (pedidos.length !== 1 ? "s" : "") + " esperando revisión"
            : "No hay comprobantes pendientes"}
        </p>
      </div>

      {pedidos.length === 0 ? (
        <div className="panel panel-empty-big">
          <CheckBigIcon />
          <h3>Todo al día</h3>
          <p>No hay comprobantes pendientes de validación.</p>
        </div>
      ) : (
        <div className="pagos-grid">
          {pedidos.map((pedido) => {
            const nombreArchivo = pedido.comprobanteUrl
              ? pedido.comprobanteUrl.split("/").pop() ?? "comprobante"
              : null;

            return (
              <div className="pago-card" key={pedido.id}>
                {/* Cabecera: folio + empresa + total */}
                <div className="pago-card-head">
                  <div>
                    <span className="mono pago-folio">
                      {pedido.id.slice(0, 8).toUpperCase()}
                    </span>
                    <h3>{pedido.comerciante.nombre}</h3>
                    <small>
                      {fmtFecha(pedido.createdAt)} &middot; {pedido.comerciante.email}
                    </small>
                  </div>
                  <strong className="mono pago-amount">{fmtClp(pedido.total)}</strong>
                </div>

                {/* Datos del comerciante */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "6px 16px",
                    fontSize: "12.5px",
                    color: "var(--ink-2)",
                    marginBottom: "12px",
                    paddingBottom: "12px",
                    borderBottom: "1px solid var(--line-2)",
                  }}
                >
                  <span>
                    <strong style={{ color: "var(--ink-3)", fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: ".04em" }}>RUT</strong>
                    <br />
                    <span style={{ fontFamily: "var(--mono)", fontWeight: 600 }}>{pedido.comerciante.rutEmpresa}</span>
                  </span>
                  <span>
                    <strong style={{ color: "var(--ink-3)", fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: ".04em" }}>Teléfono</strong>
                    <br />
                    {pedido.comerciante.telefono}
                  </span>
                  <span style={{ gridColumn: "1 / -1" }}>
                    <strong style={{ color: "var(--ink-3)", fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: ".04em" }}>Región despacho</strong>
                    <br />
                    {pedido.region}
                  </span>
                </div>

                {/* Comprobante */}
                <div className="pago-comp">
                  <div className="pago-comp-thumb">
                    <DocIcon />
                  </div>
                  <div className="pago-comp-info">
                    {pedido.comprobanteUrl ? (
                      <>
                        <b>{nombreArchivo}</b>
                        <small>Comprobante de transferencia</small>
                      </>
                    ) : (
                      <>
                        <b style={{ color: "var(--ink-3)" }}>Sin comprobante</b>
                        <small>El comerciante no adjuntó imagen</small>
                      </>
                    )}
                  </div>
                  {pedido.comprobanteUrl && (
                    <a
                      href={pedido.comprobanteUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="pago-comp-view"
                      style={{ textDecoration: "none" }}
                    >
                      Ver
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
                        <path d="M5 12h14M12 5l7 7-7 7" />
                      </svg>
                    </a>
                  )}
                </div>

                {/* Resumen items */}
                <div
                  style={{
                    fontSize: "12.5px",
                    color: "var(--ink-2)",
                    marginBottom: "14px",
                    padding: "8px 10px",
                    background: "var(--surface-2)",
                    borderRadius: "7px",
                    border: "1px solid var(--line-2)",
                  }}
                >
                  <strong style={{ color: "var(--ink)", fontSize: "12px" }}>
                    {pedido.items.length} producto{pedido.items.length !== 1 ? "s" : ""}
                  </strong>
                  <span style={{ color: "var(--ink-3)", margin: "0 6px" }}>&middot;</span>
                  {pedido.items.slice(0, 2).map((it) => it.producto.nombre).join(", ")}
                  {pedido.items.length > 2 && " y " + (pedido.items.length - 2) + " más"}
                </div>

                {/* Botones Validar / Rechazar */}
                <AccionesPago
                  pedidoId={pedido.id}
                  folio={pedido.id.slice(0, 8).toUpperCase()}
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
