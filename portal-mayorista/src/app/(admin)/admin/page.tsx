import Link from "next/link";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Resumen | Admin · Trade Global",
};

/* ── íconos inline ─────────────────────────────────────────── */

function IconPersonas() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function IconDoc() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  );
}

function IconCamion() {
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

function IconCheck() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  );
}

function IconFlecha() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14M12 5l7 7-7 7" />
    </svg>
  );
}

/* ── tarjeta KPI ────────────────────────────────────────────── */

function StatCard({
  label,
  value,
  hint,
  icon,
  tone = "brand",
  href,
}: {
  label: string;
  value: number;
  hint: string;
  icon: React.ReactNode;
  tone?: "brand" | "amber" | "ok" | "blue";
  href?: string;
}) {
  const card = (
    <div className={"stat stat-" + tone} style={{ cursor: href ? "pointer" : "default" }}>
      <div className="stat-ico">{icon}</div>
      <div className="stat-body">
        <span className="stat-label">{label}</span>
        <strong className="stat-value mono">{value}</strong>
        <span className="stat-hint">{hint}</span>
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} style={{ textDecoration: "none", display: "block" }}>
        {card}
      </Link>
    );
  }
  return card;
}

/* ── acceso rápido ──────────────────────────────────────────── */

function AccesoRapido({
  href,
  titulo,
  descripcion,
}: {
  href: string;
  titulo: string;
  descripcion: string;
}) {
  return (
    <Link
      href={href}
      className="panel"
      style={{
        textDecoration: "none",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "12px",
        padding: "16px 18px",
      }}
    >
      <div>
        <strong style={{ fontSize: "14px", fontWeight: 800, display: "block" }}>
          {titulo}
        </strong>
        <span style={{ fontSize: "12.5px", color: "var(--ink-2)", marginTop: "2px", display: "block" }}>
          {descripcion}
        </span>
      </div>
      <span style={{ color: "var(--brand)", flexShrink: 0 }}>
        <IconFlecha />
      </span>
    </Link>
  );
}

/* ── página principal ───────────────────────────────────────── */

export default async function AdminResumenPage() {
  // Conteos en paralelo
  const [
    comerciantesPendientes,
    pagosPorValidar,
    pedidosEnProceso,
    totalComerciantesAprobados,
  ] = await Promise.all([
    prisma.comerciante.count({ where: { estado: "pendiente" } }),
    prisma.pedido.count({ where: { estado: "pago_en_validacion" } }),
    prisma.pedido.count({
      where: { estado: { in: ["validado", "oc_generada", "despachado"] } },
    }),
    prisma.comerciante.count({ where: { estado: "aprobado" } }),
  ]);

  return (
    <div className="adm-page">
      {/* Encabezado */}
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "22px", fontWeight: 800 }}>Resumen</h1>
        <p style={{ fontSize: "13.5px", color: "var(--ink-2)", marginTop: "4px" }}>
          Estado general de la operación
        </p>
      </div>

      {/* KPIs */}
      <div className="stat-grid" style={{ marginBottom: "28px" }}>
        <StatCard
          label="Comerciantes pendientes"
          value={comerciantesPendientes}
          hint={comerciantesPendientes === 1 ? "solicitud sin revisar" : "solicitudes sin revisar"}
          icon={<IconPersonas />}
          tone="amber"
          href="/admin/comerciantes?estado=pendiente"
        />
        <StatCard
          label="Pagos por validar"
          value={pagosPorValidar}
          hint={pagosPorValidar === 1 ? "comprobante en espera" : "comprobantes en espera"}
          icon={<IconDoc />}
          tone="brand"
          href="/admin/pagos"
        />
        <StatCard
          label="Pedidos en proceso"
          value={pedidosEnProceso}
          hint="validado · OC generada · despachado"
          icon={<IconCamion />}
          tone="blue"
          href="/admin/pedidos"
        />
        <StatCard
          label="Comerciantes activos"
          value={totalComerciantesAprobados}
          hint="con acceso al portal"
          icon={<IconCheck />}
          tone="ok"
          href="/admin/comerciantes?estado=aprobado"
        />
      </div>

      {/* Accesos rápidos */}
      <div style={{ marginBottom: "14px" }}>
        <span
          style={{
            fontSize: "11.5px",
            fontWeight: 800,
            textTransform: "uppercase" as const,
            letterSpacing: ".04em",
            color: "var(--ink-3)",
          }}
        >
          Accesos rápidos
        </span>
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
          gap: "12px",
        }}
      >
        <AccesoRapido
          href="/admin/comerciantes"
          titulo="Comerciantes"
          descripcion="Aprobar o rechazar solicitudes de registro"
        />
        <AccesoRapido
          href="/admin/pagos"
          titulo="Pagos"
          descripcion="Revisar y validar comprobantes de transferencia"
        />
        <AccesoRapido
          href="/admin/pedidos"
          titulo="Pedidos"
          descripcion="Seguimiento y avance de cada pedido"
        />
      </div>
    </div>
  );
}
