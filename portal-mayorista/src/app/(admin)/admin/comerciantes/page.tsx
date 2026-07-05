import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import Link from "next/link";
import AccionesComerciante from "./acciones";
import EvaluacionComerciante from "./evaluacion";
import {
  calcularScoreAuto,
  scoreFinal,
  tierEfectivo,
  type Tier,
} from "@/lib/evaluacion";

export const metadata = {
  title: "Comerciantes | Admin · Comercial Solutions",
};

const FILTROS = [
  { id: "todos",     label: "Todos"     },
  { id: "pendiente", label: "Pendiente" },
  { id: "aprobado",  label: "Aprobado"  },
  { id: "rechazado", label: "Rechazado" },
] as const;

type EstadoFiltro = "todos" | "pendiente" | "aprobado" | "rechazado";

// Estados de pedido que cuentan como pago aceptado (para el score de cliente).
const PEDIDOS_BUENOS = ["validado", "oc_generada", "despachado", "entregado"];

const TIER_COLOR: Record<Tier, string> = { A: "#1f9d57", B: "#c98a12", C: "#c4423f" };

function EstadoPill({ estado }: { estado: string }) {
  const mapa: Record<string, { cls: string; label: string }> = {
    pendiente: { cls: "adm-status adm-status-amber", label: "Pendiente" },
    aprobado:  { cls: "adm-status adm-status-ok",   label: "Aprobado"  },
    rechazado: { cls: "adm-status adm-status-out",   label: "Rechazado" },
  };
  const cfg = mapa[estado] ?? { cls: "adm-status adm-status-amber", label: estado };
  return <span className={cfg.cls}>{cfg.label}</span>;
}

function formatFecha(d: Date) {
  return d.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

interface PageProps {
  searchParams: Promise<{ estado?: string }>;
}

export default async function ComerciantesAdminPage({ searchParams }: PageProps) {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin") redirect("/login");

  const params = await searchParams;
  const filtro: EstadoFiltro =
    (FILTROS.map((f) => f.id) as string[]).includes(params.estado ?? "")
      ? (params.estado as EstadoFiltro)
      : "todos";

  const comerciantes = await prisma.comerciante.findMany({
    where: filtro !== "todos" ? { estado: filtro } : undefined,
    orderBy: [{ estado: "asc" }, { createdAt: "desc" }],
  });

  const conteos = await prisma.comerciante.groupBy({
    by: ["estado"],
    _count: { _all: true },
  });
  const total = conteos.reduce((a, b) => a + b._count._all, 0);
  const conteoMap: Record<string, number> = {};
  for (const c of conteos) conteoMap[c.estado] = c._count._all;

  const pendientesCount = conteoMap["pendiente"] ?? 0;

  // Agregados de pedidos por comerciante, para el score automático en vivo.
  const agg = await prisma.pedido.groupBy({
    by: ["comercianteId", "estado"],
    _count: { _all: true },
    _sum: { total: true },
  });
  const porCom: Record<
    string,
    { totalComprado: number; nPedidos: number; nBuenos: number; nRechazados: number }
  > = {};
  for (const g of agg) {
    const m = (porCom[g.comercianteId] ??= {
      totalComprado: 0,
      nPedidos: 0,
      nBuenos: 0,
      nRechazados: 0,
    });
    const cnt = g._count._all;
    m.nPedidos += cnt;
    if (PEDIDOS_BUENOS.includes(g.estado)) {
      m.nBuenos += cnt;
      m.totalComprado += g._sum.total ?? 0;
    }
    if (g.estado === "rechazado") m.nRechazados += cnt;
  }

  const ahora = Date.now();
  function evaluar(c: (typeof comerciantes)[number]) {
    const d =
      porCom[c.id] ?? { totalComprado: 0, nPedidos: 0, nBuenos: 0, nRechazados: 0 };
    const antiguedadDias = Math.max(0, (ahora - c.createdAt.getTime()) / 86_400_000);
    const { scoreAuto, componentes } = calcularScoreAuto({ ...d, antiguedadDias });
    const finalVal = scoreFinal(scoreAuto, c.scoreAjuste);
    const tier = tierEfectivo(finalVal, c.tierManual);
    return { scoreAuto, componentes, finalVal, tier };
  }

  return (
    <div className="adm-page">
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "16px",
          marginBottom: "22px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: 800, display: "flex", alignItems: "center", gap: "9px" }}>
            <PeopleIcon />
            Validación y evaluación de comerciantes
          </h2>
          <p style={{ fontSize: "13.5px", color: "var(--ink-2)", marginTop: "4px" }}>
            {pendientesCount > 0
              ? pendientesCount + " solicitud" + (pendientesCount !== 1 ? "es" : "") + " pendiente" + (pendientesCount !== 1 ? "s" : "") + " de aprobación"
              : "No hay solicitudes pendientes"}
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", justifyContent: "flex-end" }}>
          <StatMini label="Total" value={total} tone="brand" />
          <StatMini label="Pendientes" value={pendientesCount} tone="amber" />
          <StatMini label="Aprobados" value={conteoMap["aprobado"] ?? 0} tone="ok" />
          <StatMini label="Rechazados" value={conteoMap["rechazado"] ?? 0} tone="out" />
        </div>
      </div>

      <div className="adm-filters">
        {FILTROS.map((f) => {
          const count = f.id === "todos" ? total : (conteoMap[f.id] ?? 0);
          const isOn = filtro === f.id;
          return (
            <Link
              key={f.id}
              href={f.id === "todos" ? "/admin/comerciantes" : "/admin/comerciantes?estado=" + f.id}
              className={"chip" + (isOn ? " is-on" : "")}
              style={{ textDecoration: "none" }}
            >
              {f.label}
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 800,
                  background: isOn ? "rgba(255,255,255,0.25)" : "var(--line-2)",
                  color: isOn ? "#fff" : "var(--ink-3)",
                  padding: "1px 6px",
                  borderRadius: "100px",
                  minWidth: "20px",
                  textAlign: "center",
                }}
              >
                {count}
              </span>
            </Link>
          );
        })}
      </div>

      <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
        {comerciantes.length === 0 ? (
          <div className="panel-empty-big">
            <PeopleIcon size={40} color="var(--ink-3)" />
            <h3 style={{ color: "var(--ink-2)" }}>
              {filtro === "todos"
                ? "Aún no hay comerciantes registrados"
                : "No hay comerciantes con estado " + (FILTROS.find((f) => f.id === filtro)?.label ?? filtro)}
            </h3>
            <p>Cuando alguien se registre aparecerá aquí para su revisión.</p>
          </div>
        ) : (
          comerciantes.map((c, i) => {
            const ev = evaluar(c);
            return (
              <div
                key={c.id}
                style={{
                  padding: "16px",
                  borderTop: i === 0 ? "none" : "1px solid var(--line-2)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "16px",
                    flexWrap: "wrap",
                    alignItems: "flex-start",
                  }}
                >
                  <div style={{ display: "flex", flexDirection: "column", gap: "2px", minWidth: 0 }}>
                    <span style={{ fontWeight: 700, fontSize: "14px" }}>{c.nombre}</span>
                    <span style={{ fontSize: "12px", color: "var(--ink-2)" }}>{c.email}</span>
                    <span style={{ fontSize: "11px", color: "var(--ink-3)" }}>
                      {c.giro} · Registrado {formatFecha(c.createdAt)}
                    </span>
                    {(c.comuna || c.region) && (
                      <span style={{ fontSize: "11px", color: "var(--ink-3)" }}>
                        {[c.comuna, c.region].filter(Boolean).join(", ")}
                      </span>
                    )}
                  </div>

                  <div style={{ display: "flex", gap: "18px", alignItems: "center", flexWrap: "wrap" }}>
                    <MetaDato label="RUT empresa" valor={c.rutEmpresa} mono />
                    <MetaDato label="Teléfono" valor={c.telefono || "-"} />
                    <div style={{ display: "flex", flexDirection: "column", gap: "5px", alignItems: "flex-start" }}>
                      <EstadoPill estado={c.estado} />
                      <ScoreTier score={ev.finalVal} tier={ev.tier} />
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "12px" }}>
                  {c.estado === "pendiente" && (
                    <AccionesComerciante id={c.id} nombre={c.nombre} />
                  )}
                  <EvaluacionComerciante
                    id={c.id}
                    scoreAuto={ev.scoreAuto}
                    componentes={ev.componentes}
                    scoreAjuste={c.scoreAjuste}
                    tierManual={c.tierManual}
                    notaEval={c.notaEval}
                  />
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

function MetaDato({ label, valor, mono }: { label: string; valor: string; mono?: boolean }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
      <span style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--ink-3)", textTransform: "uppercase", letterSpacing: "0.03em" }}>
        {label}
      </span>
      <span
        style={{
          fontSize: "13px",
          color: "var(--ink-2)",
          fontWeight: 600,
          fontFamily: mono ? "var(--mono)" : "inherit",
        }}
      >
        {valor}
      </span>
    </div>
  );
}

function ScoreTier({ score, tier }: { score: number; tier: Tier }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "7px" }}>
      <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--ink-2)" }}>{score}/100</span>
      <span
        style={{
          display: "inline-block",
          padding: "2px 9px",
          borderRadius: "100px",
          background: TIER_COLOR[tier] + "22",
          color: TIER_COLOR[tier],
          fontWeight: 800,
          fontSize: "12px",
        }}
      >
        Tier {tier}
      </span>
    </div>
  );
}

function StatMini({ label, value, tone }: { label: string; value: number; tone: "brand" | "amber" | "ok" | "out" }) {
  const colors: Record<string, { bg: string; color: string }> = {
    brand: { bg: "var(--brand-soft)", color: "var(--brand-ink)" },
    amber: { bg: "var(--amber-t)",    color: "var(--amber)"     },
    ok:    { bg: "var(--ok-t)",       color: "var(--ok)"        },
    out:   { bg: "var(--out-t)",      color: "var(--out)"       },
  };
  const c = colors[tone];
  return (
    <div style={{ background: c.bg, color: c.color, padding: "8px 14px", borderRadius: "9px", display: "flex", flexDirection: "column", alignItems: "center", minWidth: "64px" }}>
      <strong style={{ fontSize: "20px", fontWeight: 800, lineHeight: 1.1 }}>{value}</strong>
      <span style={{ fontSize: "11px", fontWeight: 700, marginTop: "2px" }}>{label}</span>
    </div>
  );
}

function PeopleIcon({ size = 18, color = "var(--brand)" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}
