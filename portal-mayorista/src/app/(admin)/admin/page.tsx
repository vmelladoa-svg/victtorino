import Link from "next/link";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Resumen | Admin · Trade Global",
};

function fmtClp(n: number) {
  return "$" + n.toLocaleString("es-CL");
}

function IconBolt() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  );
}

function IconShield() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

function IconClock() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function IconTruck() {
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

function IconPackage() {
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

function IconGrid() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" />
      <rect x="14" y="3" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" />
    </svg>
  );
}

function IconChevRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 18l6-6-6-6" />
    </svg>
  );
}

function EstadoPill({ estado }: { estado: string }) {
  const mapa: Record<string, { cls: string; label: string }> = {
    pago_en_validacion: { cls: "adm-status adm-status-amber sm", label: "Pago en validación" },
    validado:           { cls: "adm-status adm-status-brand sm", label: "Validado"           },
    oc_generada:        { cls: "adm-status adm-status-blue  sm", label: "OC generada"        },
    despachado:         { cls: "adm-status adm-status-blue  sm", label: "Despachado"         },
    entregado:          { cls: "adm-status adm-status-ok    sm", label: "Entregado"          },
    rechazado:          { cls: "adm-status adm-status-out   sm", label: "Rechazado"          },
  };
  const cfg = mapa[estado] ?? { cls: "adm-status adm-status-amber sm", label: estado };
  return <span className={cfg.cls}>{cfg.label}</span>;
}

export default async function AdminResumenPage() {
  const ahora = new Date();
  const inicioMes = new Date(ahora.getFullYear(), ahora.getMonth(), 1);

  const [
    pedidosMes,
    itemsMes,
    porValidarList,
    porComprarList,
    recientesList,
    countEnProceso,
  ] = await Promise.all([
    prisma.pedido.findMany({
      where: {
        createdAt: { gte: inicioMes },
        estado: { not: "rechazado" },
      },
      select: { total: true },
    }),

    prisma.pedidoItem.findMany({
      where: {
        pedido: {
          createdAt: { gte: inicioMes },
          estado: { not: "rechazado" },
        },
      },
      select: {
        cantidad: true,
        precioAplicado: true,
        producto: { select: { costo: true } },
      },
    }),

    prisma.pedido.findMany({
      where: { estado: "pago_en_validacion" },
      orderBy: { createdAt: "asc" },
      take: 8,
      select: {
        id: true,
        total: true,
        comerciante: { select: { nombre: true } },
      },
    }),

    prisma.pedido.findMany({
      where: { estado: "validado" },
      orderBy: { createdAt: "asc" },
      take: 8,
      select: {
        id: true,
        total: true,
        items: { select: { id: true } },
      },
    }),

    prisma.pedido.findMany({
      orderBy: { createdAt: "desc" },
      take: 5,
      select: {
        id: true,
        estado: true,
        total: true,
        createdAt: true,
        comerciante: { select: { nombre: true } },
      },
    }),

    prisma.pedido.count({
      where: { estado: { in: ["validado", "oc_generada", "despachado"] } },
    }),
  ]);

  const ventasMes = pedidosMes.reduce((s, p) => s + p.total, 0);

  const margenMes = itemsMes.reduce((s, item) => {
    const costo = item.producto.costo ?? 0;
    return s + (item.precioAplicado - costo) * item.cantidad;
  }, 0);

  const margenPct = ventasMes > 0 ? Math.round((margenMes / ventasMes) * 100) : 0;

  const totalEsperaPago = porValidarList.reduce((s, p) => s + p.total, 0);
  return (
    <div className="adm-page">

      <div className="stat-grid">

        <div className="stat stat-brand">
          <div className="stat-ico"><IconBolt /></div>
          <div className="stat-body">
            <span className="stat-label">Ventas del mes</span>
            <strong className="stat-value mono">{fmtClp(ventasMes)}</strong>
            <span className="stat-hint">pedidos activos del mes</span>
          </div>
        </div>

        <div className="stat stat-ok">
          <div className="stat-ico"><IconShield /></div>
          <div className="stat-body">
            <span className="stat-label">Margen estimado</span>
            <strong className="stat-value mono">{fmtClp(margenMes)}</strong>
            <span className="stat-hint">{margenPct}% sobre venta</span>
          </div>
        </div>

        <Link href="/admin/pagos" style={{ textDecoration: "none" }}>
          <div className="stat stat-amber" style={{ cursor: "pointer" }}>
            <div className="stat-ico"><IconClock /></div>
            <div className="stat-body">
              <span className="stat-label">Pagos por validar</span>
              <strong className="stat-value mono">{porValidarList.length}</strong>
              <span className="stat-hint">{fmtClp(totalEsperaPago)} en espera</span>
            </div>
          </div>
        </Link>

        <Link href="/admin/pedidos" style={{ textDecoration: "none" }}>
          <div className="stat stat-blue" style={{ cursor: "pointer" }}>
            <div className="stat-ico"><IconTruck /></div>
            <div className="stat-body">
              <span className="stat-label">En proceso / despacho</span>
              <strong className="stat-value mono">{countEnProceso}</strong>
              <span className="stat-hint">pedidos activos</span>
            </div>
          </div>
        </Link>

      </div>

      <div className="adm-cols">

        <section className="panel">
          <div className="panel-head">
            <h2>
              <IconClock />
              Pagos por validar
            </h2>
            <Link href="/admin/pagos" className="panel-link">
              Ver todos <IconChevRight />
            </Link>
          </div>

          {porValidarList.length === 0 ? (
            <div className="panel-empty">No hay pagos pendientes.</div>
          ) : (
            porValidarList.map((p) => {
              const folio = "#" + p.id.slice(0, 8).toUpperCase();
              return (
                <Link
                  key={p.id}
                  href="/admin/pagos"
                  className="prow"
                  style={{ textDecoration: "none" }}
                >
                  <div className="prow-main">
                    <span className="mono prow-folio">{folio}</span>
                    <span className="prow-cli">{p.comerciante.nombre}</span>
                  </div>
                  <span></span>
                  <strong className="mono">{fmtClp(p.total)}</strong>
                  <span className="prow-cta">Validar <IconChevRight /></span>
                </Link>
              );
            })
          )}
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>
              <IconPackage />
              Por comprar a AlilaTop
            </h2>
            <Link href="/admin/pedidos" className="panel-link">
              Gestionar <IconChevRight />
            </Link>
          </div>

          {porComprarList.length === 0 ? (
            <div className="panel-empty">Sin compras pendientes.</div>
          ) : (
            porComprarList.map((p) => {
              const folio = "#" + p.id.slice(0, 8).toUpperCase();
              return (
                <div key={p.id} className="prow static">
                  <div className="prow-main">
                    <span className="mono prow-folio">{folio}</span>
                    <span className="prow-cli">
                      {p.items.length} {p.items.length === 1 ? "producto" : "productos"}
                    </span>
                  </div>
                  <span></span>
                  <strong className="mono">{fmtClp(p.total)}</strong>
                  <span className="prow-tag">costo</span>
                </div>
              );
            })
          )}
        </section>

      </div>

      <section className="panel">
        <div className="panel-head">
          <h2><IconGrid />Actividad reciente</h2>
          <Link href="/admin/pedidos" className="panel-link">
            Ver todos <IconChevRight />
          </Link>
        </div>

        {recientesList.length === 0 ? (
          <div className="panel-empty">No hay pedidos registrados.</div>
        ) : (
          <div className="adm-table">
            <div className="adm-tr adm-thd">
              <span>Folio</span>
              <span>Comerciante</span>
              <span>Estado</span>
              <span className="ar">Total</span>
              <span className="ar">Fecha</span>
              <span></span>
            </div>

            {recientesList.map((p) => {
              const folio = "#" + p.id.slice(0, 8).toUpperCase();
              const fecha = p.createdAt.toLocaleDateString("es-CL", {
                day: "2-digit",
                month: "short",
              });
              return (
                <Link
                  key={p.id}
                  href="/admin/pedidos"
                  className="adm-tr"
                  style={{ textDecoration: "none" }}
                >
                  <span className="mono">{folio}</span>
                  <span className="td-cli">{p.comerciante.nombre}</span>
                  <span><EstadoPill estado={p.estado} /></span>
                  <span className="ar mono">{fmtClp(p.total)}</span>
                  <span className="ar" style={{ fontSize: "12.5px", color: "var(--ink-3)" }}>{fecha}</span>
                  <span className="ar" style={{ color: "var(--brand)" }}><IconChevRight /></span>
                </Link>
              );
            })}
          </div>
        )}
      </section>

    </div>
  );
}
