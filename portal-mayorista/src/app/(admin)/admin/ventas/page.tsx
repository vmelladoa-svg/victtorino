import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import Link from "next/link";
import ExportarCsvBtn from "./exportar-csv";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Ventas / Historial | Admin · Comercial Solutions",
};

/* ------------------------------------------------------------------ */
/* Utilidades                                                          */
/* ------------------------------------------------------------------ */
function fmtClp(n: number) {
  return "$" + n.toLocaleString("es-CL");
}

function fmtFecha(d: Date) {
  return d.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

/* ------------------------------------------------------------------ */
/* Estado → etiqueta y clase CSS                                       */
/* ------------------------------------------------------------------ */
const ESTADOS_MAPA: Record<string, { cls: string; label: string }> = {
  pago_en_validacion: { cls: "adm-status adm-status-amber", label: "Pago en validación" },
  validado:           { cls: "adm-status adm-status-brand", label: "Validado"            },
  oc_generada:        { cls: "adm-status adm-status-brand", label: "OC generada"         },
  despachado:         { cls: "adm-status adm-status-ok",   label: "Despachado"           },
  entregado:          { cls: "adm-status adm-status-ok",   label: "Entregado"            },
  rechazado:          { cls: "adm-status adm-status-out",  label: "Rechazado"            },
};

function EstadoPill({ estado }: { estado: string }) {
  const cfg = ESTADOS_MAPA[estado] ?? {
    cls: "adm-status adm-status-amber",
    label: estado,
  };
  return <span className={`${cfg.cls} sm`}>{cfg.label}</span>;
}

const FILTROS_ESTADO = [
  { id: "todos",              label: "Todos"               },
  { id: "pago_en_validacion", label: "Pago en validación"  },
  { id: "validado",           label: "Validado"            },
  { id: "oc_generada",        label: "OC generada"         },
  { id: "despachado",         label: "Despachado"          },
  { id: "entregado",          label: "Entregado"           },
  { id: "rechazado",          label: "Rechazado"           },
] as const;

/* ------------------------------------------------------------------ */
/* Iconos                                                              */
/* ------------------------------------------------------------------ */
function IconoVentas() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="1" x2="12" y2="23" />
      <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
    </svg>
  );
}

function IconoTicket() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
  );
}

function IconoPedidos() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/* Tipos                                                               */
/* ------------------------------------------------------------------ */
interface PedidoFila {
  id: string;
  createdAt: Date;
  estado: string;
  total: number;
  comerciante: { nombre: string; email: string };
  items: { id: string }[];
}

/* ------------------------------------------------------------------ */
/* Props de página (Next.js 16: searchParams es Promise)               */
/* ------------------------------------------------------------------ */
interface PageProps {
  searchParams: Promise<{
    estado?: string;
    desde?: string;
    hasta?: string;
    comercianteId?: string;
  }>;
}

/* ------------------------------------------------------------------ */
/* Página                                                              */
/* ------------------------------------------------------------------ */
export default async function VentasAdminPage({ searchParams }: PageProps) {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin") redirect("/login");

  const params = await searchParams;

  /* ---------- Filtros ---------- */
  const estadosValidos = FILTROS_ESTADO.map((f) => f.id) as string[];
  const estadoFiltro =
    estadosValidos.includes(params.estado ?? "") && params.estado !== "todos"
      ? params.estado!
      : undefined;

  const desdeStr = params.desde ?? "";
  const hastaStr = params.hasta ?? "";
  const comercianteIdFiltro = params.comercianteId && params.comercianteId !== "todos"
    ? params.comercianteId
    : undefined;

  /* ---------- Where Prisma ---------- */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const where: Record<string, any> = {};

  if (estadoFiltro) {
    where.estado = estadoFiltro;
  }
  if (desdeStr || hastaStr) {
    where.createdAt = {};
    if (desdeStr) where.createdAt.gte = new Date(desdeStr);
    if (hastaStr) {
      const hasta = new Date(hastaStr);
      hasta.setHours(23, 59, 59, 999);
      where.createdAt.lte = hasta;
    }
  }
  if (comercianteIdFiltro) {
    where.comercianteId = comercianteIdFiltro;
  }

  /* ---------- Consultas paralelas ---------- */
  const [pedidos, comerciantes] = await Promise.all([
    prisma.pedido.findMany({
      where,
      include: {
        comerciante: { select: { nombre: true, email: true } },
        items: { select: { id: true } },
      },
      orderBy: { createdAt: "desc" },
    }),
    prisma.comerciante.findMany({
      where: { estado: "aprobado" },
      select: { id: true, nombre: true },
      orderBy: { nombre: "asc" },
    }),
  ]);

  /* ---------- KPIs (excluye rechazado) ---------- */
  const pedidosContar = pedidos.filter((p) => p.estado !== "rechazado");
  const totalVendido = pedidosContar.reduce((sum, p) => sum + p.total, 0);
  const nPedidos = pedidosContar.length;
  const ticketPromedio = nPedidos > 0 ? Math.round(totalVendido / nPedidos) : 0;

  /* ---------- Datos para CSV (serializados) ---------- */
  const filasCsv = pedidos.map((p) => ({
    folio: "#" + p.id.slice(0, 8).toUpperCase(),
    fecha: fmtFecha(p.createdAt),
    comerciante: p.comerciante.nombre,
    email: p.comerciante.email,
    estado: ESTADOS_MAPA[p.estado]?.label ?? p.estado,
    total: p.total,
  }));

  /* ---------- URL base para filtros (links GET) ---------- */
  function buildUrl(overrides: Record<string, string>) {
    const sp = new URLSearchParams();
    const current = {
      estado: params.estado ?? "todos",
      desde: desdeStr,
      hasta: hastaStr,
      comercianteId: params.comercianteId ?? "todos",
      ...overrides,
    };
    if (current.estado && current.estado !== "todos") sp.set("estado", current.estado);
    if (current.desde) sp.set("desde", current.desde);
    if (current.hasta) sp.set("hasta", current.hasta);
    if (current.comercianteId && current.comercianteId !== "todos")
      sp.set("comercianteId", current.comercianteId);
    const q = sp.toString();
    return "/admin/ventas" + (q ? "?" + q : "");
  }

  const estadoActual = params.estado ?? "todos";

  return (
    <div className="adm-page">
      {/* ── Cabecera ── */}
      <div style={{ marginBottom: "28px", display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h1 style={{ fontSize: "22px", fontWeight: 900, display: "flex", alignItems: "center", gap: "10px" }}>
            <IconoVentas />
            Ventas / Historial
          </h1>
          <p style={{ fontSize: "13.5px", color: "var(--ink-2)", marginTop: "5px" }}>
            Todos los pedidos del portal mayorista
          </p>
        </div>
        <ExportarCsvBtn filas={filasCsv} />
      </div>

      {/* ── KPIs ── */}
      <div className="stat-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: "24px" }}>
        <div className="stat stat-ok">
          <div className="stat-ico"><IconoVentas /></div>
          <div className="stat-body">
            <span className="stat-label">Total vendido</span>
            <span className="stat-value" style={{ fontSize: "22px" }}>{fmtClp(totalVendido)}</span>
            <span className="stat-hint">sin rechazados</span>
          </div>
        </div>
        <div className="stat stat-brand">
          <div className="stat-ico"><IconoPedidos /></div>
          <div className="stat-body">
            <span className="stat-label">N° de pedidos</span>
            <span className="stat-value">{nPedidos}</span>
            <span className="stat-hint">sin rechazados</span>
          </div>
        </div>
        <div className="stat stat-amber">
          <div className="stat-ico"><IconoTicket /></div>
          <div className="stat-body">
            <span className="stat-label">Ticket promedio</span>
            <span className="stat-value" style={{ fontSize: "20px" }}>{fmtClp(ticketPromedio)}</span>
            <span className="stat-hint">por pedido</span>
          </div>
        </div>
      </div>

      {/* ── Filtros ── */}
      <div className="panel" style={{ marginBottom: "20px" }}>
        {/* Filtro estado: chips */}
        <div style={{ marginBottom: "14px" }}>
          <p style={{ fontSize: "11.5px", fontWeight: 800, textTransform: "uppercase", letterSpacing: ".05em", color: "var(--ink-3)", marginBottom: "8px" }}>
            Estado
          </p>
          <div className="adm-filters">
            {FILTROS_ESTADO.map((f) => (
              <Link
                key={f.id}
                href={buildUrl({ estado: f.id })}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  padding: "6px 14px",
                  borderRadius: "100px",
                  fontSize: "13px",
                  fontWeight: 700,
                  textDecoration: "none",
                  background: estadoActual === f.id ? "var(--brand)" : "var(--surface-2)",
                  color: estadoActual === f.id ? "#fff" : "var(--ink-2)",
                  border: estadoActual === f.id ? "1px solid var(--brand)" : "1px solid var(--line)",
                  transition: "all .15s",
                }}
              >
                {f.label}
              </Link>
            ))}
          </div>
        </div>

        {/* Filtros fecha + comerciante: form GET */}
        <form method="GET" action="/admin/ventas" style={{ display: "flex", flexWrap: "wrap", gap: "12px", alignItems: "flex-end" }}>
          {/* Mantener filtro de estado al enviar el form */}
          {estadoActual !== "todos" && (
            <input type="hidden" name="estado" value={estadoActual} />
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <label style={{ fontSize: "11.5px", fontWeight: 700, color: "var(--ink-3)", textTransform: "uppercase", letterSpacing: ".04em" }}>
              Desde
            </label>
            <input
              type="date"
              name="desde"
              defaultValue={desdeStr}
              style={{
                padding: "8px 12px",
                borderRadius: "var(--rs)",
                border: "1px solid var(--line)",
                background: "var(--surface)",
                color: "var(--ink)",
                fontSize: "13.5px",
                fontFamily: "var(--font)",
              }}
            />
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <label style={{ fontSize: "11.5px", fontWeight: 700, color: "var(--ink-3)", textTransform: "uppercase", letterSpacing: ".04em" }}>
              Hasta
            </label>
            <input
              type="date"
              name="hasta"
              defaultValue={hastaStr}
              style={{
                padding: "8px 12px",
                borderRadius: "var(--rs)",
                border: "1px solid var(--line)",
                background: "var(--surface)",
                color: "var(--ink)",
                fontSize: "13.5px",
                fontFamily: "var(--font)",
              }}
            />
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <label style={{ fontSize: "11.5px", fontWeight: 700, color: "var(--ink-3)", textTransform: "uppercase", letterSpacing: ".04em" }}>
              Comerciante
            </label>
            <select
              name="comercianteId"
              defaultValue={params.comercianteId ?? "todos"}
              style={{
                padding: "8px 12px",
                borderRadius: "var(--rs)",
                border: "1px solid var(--line)",
                background: "var(--surface)",
                color: "var(--ink)",
                fontSize: "13.5px",
                fontFamily: "var(--font)",
                minWidth: "180px",
              }}
            >
              <option value="todos">Todos los comerciantes</option>
              {comerciantes.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <button
              type="submit"
              style={{
                padding: "9px 18px",
                background: "var(--brand)",
                color: "#fff",
                border: 0,
                borderRadius: "var(--rs)",
                fontWeight: 700,
                fontSize: "13.5px",
                cursor: "pointer",
              }}
            >
              Filtrar
            </button>
            <Link
              href="/admin/ventas"
              style={{
                padding: "9px 14px",
                background: "var(--surface-2)",
                color: "var(--ink-2)",
                border: "1px solid var(--line)",
                borderRadius: "var(--rs)",
                fontWeight: 700,
                fontSize: "13.5px",
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
              }}
            >
              Limpiar
            </Link>
          </div>
        </form>
      </div>

      {/* ── Tabla de pedidos ── */}
      <div className="panel">
        <div className="panel-head">
          <h2>
            <IconoPedidos />
            {pedidos.length === 0
              ? "Sin pedidos"
              : `${pedidos.length} pedido${pedidos.length !== 1 ? "s" : ""}`}
          </h2>
          <span style={{ fontSize: "12.5px", color: "var(--ink-3)" }}>
            ordenados por fecha desc
          </span>
        </div>

        {pedidos.length === 0 ? (
          <div className="panel-empty-big">
            <IconoPedidos />
            <h3>Sin resultados</h3>
            <p>No hay pedidos que coincidan con los filtros aplicados.</p>
          </div>
        ) : (
          <div className="adm-table">
            {/* Cabecera */}
            <div
              className="adm-tr adm-thd"
              style={{ gridTemplateColumns: "110px 100px 1fr 90px 150px 110px" }}
            >
              <span>Folio</span>
              <span>Fecha</span>
              <span>Comerciante</span>
              <span style={{ textAlign: "center" }}>Productos</span>
              <span>Estado</span>
              <span style={{ textAlign: "right" }}>Total</span>
            </div>

            {/* Filas */}
            {pedidos.map((pedido) => {
              const folio = "#" + pedido.id.slice(0, 8).toUpperCase();
              return (
                <div
                  key={pedido.id}
                  className="adm-tr"
                  style={{ gridTemplateColumns: "110px 100px 1fr 90px 150px 110px" }}
                >
                  {/* Folio */}
                  <span style={{ fontFamily: "var(--mono)", fontWeight: 700, fontSize: "13px" }}>
                    {folio}
                  </span>

                  {/* Fecha */}
                  <span style={{ fontSize: "13px", color: "var(--ink-2)" }}>
                    {fmtFecha(pedido.createdAt)}
                  </span>

                  {/* Comerciante */}
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: "13.5px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {pedido.comerciante.nombre}
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--ink-3)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {pedido.comerciante.email}
                    </div>
                  </div>

                  {/* N° productos */}
                  <span style={{ textAlign: "center", fontSize: "13.5px", fontWeight: 700, color: "var(--ink-2)" }}>
                    {pedido.items.length}
                  </span>

                  {/* Estado */}
                  <span>
                    <EstadoPill estado={pedido.estado} />
                  </span>

                  {/* Total */}
                  <span style={{ textAlign: "right", fontFamily: "var(--mono)", fontWeight: 800, fontSize: "14px" }}>
                    {fmtClp(pedido.total)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
