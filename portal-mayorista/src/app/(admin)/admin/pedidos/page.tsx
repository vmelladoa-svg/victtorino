import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import AccionesGenerarOc from "./acciones";
import AccionesDespacho from "./acciones-despacho";

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

function PackageIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l10 6.5v7L12 22 2 15.5v-7L12 2z" />
      <path d="M12 22V12" />
      <path d="M2 8.5l10 3.5 10-3.5" />
      <path d="M7 5.5l5 2 5-2" />
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

interface PedidoConRelaciones {
  id: string;
  estado: string;
  total: number;
  region: string;
  direccion: string;
  transportista: string | null;
  tracking: string | null;
  createdAt: Date;
  comerciante: {
    nombre: string;
    email: string;
  };
  items: Array<{
    id: string;
    cantidad: number;
    subtotal: number;
    producto: {
      codigoAlila: string;
      nombre: string;
      codigoProveedor: string | null;
    };
  }>;
  oc: { numeroOc: string } | null;
}

function TarjetaPedido({
  pedido,
  accionSlot,
}: {
  pedido: PedidoConRelaciones;
  accionSlot: React.ReactNode;
}) {
  const folio = pedido.id.slice(0, 8).toUpperCase();

  return (
    <div
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
            {pedido.oc && (
              <span style={{
                fontSize: "11px",
                fontFamily: "var(--mono)",
                color: "var(--ink-2)",
                background: "var(--surface-2)",
                border: "1px solid var(--line-2)",
                borderRadius: "5px",
                padding: "1px 6px",
              }}>
                OC {pedido.oc.numeroOc}
              </span>
            )}
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
            {pedido.direccion && (
              <span style={{ marginLeft: "8px" }}>· {pedido.direccion}</span>
            )}
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
          Productos
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
              <span style={{
                fontFamily: "var(--mono)",
                fontSize: "12px",
                color: "var(--ink-3)",
                minWidth: "90px",
              }}>
                {it.producto.codigoProveedor
                  ? <><span style={{ fontSize: "10px" }}>Prov:</span> {it.producto.codigoProveedor}</>
                  : "—"}
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

      {/* Slot de acción */}
      {accionSlot}
    </div>
  );
}

function SeccionPedidos({
  titulo,
  descripcion,
  icono,
  pedidos,
  vacio,
  renderAccion,
}: {
  titulo: string;
  descripcion: string;
  icono: React.ReactNode;
  pedidos: PedidoConRelaciones[];
  vacio: string;
  renderAccion: (pedido: PedidoConRelaciones) => React.ReactNode;
}) {
  return (
    <section style={{ marginBottom: "36px" }}>
      {/* Cabecera de sección */}
      <div style={{
        marginBottom: "16px",
        paddingBottom: "12px",
        borderBottom: "2px solid var(--line-2)",
      }}>
        <h2 style={{ fontSize: "18px", fontWeight: 800, display: "flex", alignItems: "center", gap: "9px", marginBottom: "4px" }}>
          {icono}
          {titulo}
        </h2>
        <p style={{ fontSize: "13px", color: "var(--ink-2)" }}>{descripcion}</p>
      </div>

      {pedidos.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: "28px 20px",
          borderRadius: "12px",
          border: "1.5px dashed var(--line-2)",
          color: "var(--ink-3)",
          fontSize: "13px",
        }}>
          {vacio}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {pedidos.map((pedido) => (
            <TarjetaPedido
              key={pedido.id}
              pedido={pedido}
              accionSlot={renderAccion(pedido)}
            />
          ))}
        </div>
      )}
    </section>
  );
}

export default async function PedidosAdminPage() {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin") redirect("/login");

  const includeRelaciones = {
    comerciante: true,
    items: {
      include: {
        producto: {
          select: {
            codigoAlila: true,
            nombre: true,
            codigoProveedor: true,
          }
        }
      },
    },
    oc: true,
  } as const;

  const [pedidosValidados, pedidosOcGenerada, pedidosDespachados] = await Promise.all([
    prisma.pedido.findMany({
      where: { estado: "validado" },
      include: includeRelaciones,
      orderBy: { createdAt: "asc" },
    }),
    prisma.pedido.findMany({
      where: { estado: "oc_generada" },
      include: includeRelaciones,
      orderBy: { createdAt: "asc" },
    }),
    prisma.pedido.findMany({
      where: { estado: "despachado" },
      include: includeRelaciones,
      orderBy: { createdAt: "asc" },
    }),
  ]);

  const totalActivos =
    pedidosValidados.length + pedidosOcGenerada.length + pedidosDespachados.length;

  return (
    <div className="adm-page">
      {/* Cabecera global */}
      <div style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "22px", fontWeight: 900, display: "flex", alignItems: "center", gap: "10px" }}>
          <TruckIcon />
          Pedidos — Fulfillment
        </h1>
        <p style={{ fontSize: "13.5px", color: "var(--ink-2)", marginTop: "5px" }}>
          {totalActivos > 0
            ? `${totalActivos} pedido${totalActivos !== 1 ? "s" : ""} activo${totalActivos !== 1 ? "s" : ""} en proceso`
            : "Sin pedidos activos en este momento"}
        </p>
      </div>

      {/* ── Sección 1: Generar OC (validado) ── */}
      <SeccionPedidos
        titulo="Generar OC a AlilaTop"
        descripcion={
          pedidosValidados.length > 0
            ? `${pedidosValidados.length} pedido${pedidosValidados.length !== 1 ? "s" : ""} validado${pedidosValidados.length !== 1 ? "s" : ""} esperando orden de compra`
            : "No hay pedidos validados pendientes"
        }
        icono={<PackageIcon />}
        pedidos={pedidosValidados as PedidoConRelaciones[]}
        vacio="Sin pedidos validados pendientes."
        renderAccion={(pedido) => (
          <AccionesGenerarOc
            pedidoId={pedido.id}
            folio={pedido.id.slice(0, 8).toUpperCase()}
            empresa={pedido.comerciante.nombre}
          />
        )}
      />

      {/* ── Sección 2: Despachar (oc_generada) ── */}
      <SeccionPedidos
        titulo="Registrar despacho"
        descripcion={
          pedidosOcGenerada.length > 0
            ? `${pedidosOcGenerada.length} pedido${pedidosOcGenerada.length !== 1 ? "s" : ""} con OC generada, listos para despachar`
            : "Sin pedidos listos para despachar"
        }
        icono={<TruckIcon />}
        pedidos={pedidosOcGenerada as PedidoConRelaciones[]}
        vacio="Sin pedidos listos para despachar."
        renderAccion={(pedido) => (
          <AccionesDespacho
            pedidoId={pedido.id}
            folio={pedido.id.slice(0, 8).toUpperCase()}
            empresa={pedido.comerciante.nombre}
            estado="oc_generada"
            transportistaActual={pedido.transportista}
            trackingActual={pedido.tracking}
          />
        )}
      />

      {/* ── Sección 3: Marcar entregado (despachado) ── */}
      <SeccionPedidos
        titulo="Confirmar entrega"
        descripcion={
          pedidosDespachados.length > 0
            ? `${pedidosDespachados.length} pedido${pedidosDespachados.length !== 1 ? "s" : ""} despachado${pedidosDespachados.length !== 1 ? "s" : ""}, en camino al comerciante`
            : "Sin pedidos en camino"
        }
        icono={<CheckCircleIcon />}
        pedidos={pedidosDespachados as PedidoConRelaciones[]}
        vacio="Sin pedidos en camino actualmente."
        renderAccion={(pedido) => (
          <AccionesDespacho
            pedidoId={pedido.id}
            folio={pedido.id.slice(0, 8).toUpperCase()}
            empresa={pedido.comerciante.nombre}
            estado="despachado"
            transportistaActual={pedido.transportista}
            trackingActual={pedido.tracking}
          />
        )}
      />
    </div>
  );
}

function CheckCircleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  );
}
