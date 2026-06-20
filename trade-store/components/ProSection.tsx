"use client";

import { PRO_TIERS, tierForSpend, nextTier } from "@/lib/pro";
import { formatCLP } from "@/lib/format";
import { useStore } from "@/lib/store-context";

export function ProSection() {
  const { pro, openProModal } = useStore();
  const tier = pro ? tierForSpend(pro.spend) : null;
  const next = pro ? nextTier(pro.spend) : null;
  return (
    <section className="block" id="pro">
      <div className="wrap">
        <div className="pro-band">
          <span className="sec-kicker">Para maestros, técnicos e instaladores</span>
          <h2>Programa Trade Pro</h2>
          <p>
            Si trabajas instalando o reparando, tus compras valen más. Acumula compras durante
            cada período de 3 meses y sube de nivel: mientras más alto, mayor descuento y mejores
            beneficios.
          </p>
          <div className="pro-tiers">
            {PRO_TIERS.map((t) => (
              <div
                className={"pro-tier" + (tier && tier.id === t.id ? " current" : "")}
                key={t.id}
              >
                {tier && tier.id === t.id && <span className="you">Tu nivel</span>}
                <span className="tname">
                  <span className="tdot" style={{ background: t.color }} />
                  {t.name}
                </span>
                <span className="tpct">{t.pct}%</span>
                <span className="treq">
                  {t.min === 0
                    ? "Desde tu registro como Pro"
                    : "Compras sobre " + formatCLP(t.min) + " en 3 meses"}
                </span>
                <div className="tperks">
                  {t.perks.map((pk) => (
                    <span key={pk}>✓ {pk}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {pro && tier ? (
            <div className="pro-status-card">
              <b>
                Hola {pro.name.split(" ")[0]} — {tier.name} · {tier.pct}% de descuento activo
              </b>
              <span className="meta">
                Compras del período actual: {formatCLP(pro.spend)}
                {next
                  ? " · Te faltan " +
                    formatCLP(next.min - pro.spend) +
                    " para " +
                    next.name +
                    " (" +
                    next.pct +
                    "%)"
                  : " · ¡Estás en el nivel máximo!"}
              </span>
              {next && (
                <div className="pro-progress">
                  <i
                    style={{
                      width: Math.min(100, Math.round((pro.spend / next.min) * 100)) + "%",
                    }}
                  />
                </div>
              )}
              <span className="meta">
                El período se renueva cada 3 meses. Tu nivel se recalcula con las compras del
                nuevo período.
              </span>
            </div>
          ) : (
            <div className="pro-cta-row">
              <button className="btn btn-accent" onClick={openProModal}>
                Registrarme como Pro
              </button>
              <span className="pro-note">
                Registro gratuito · Validamos tu rubro y activamos tu descuento en menos de 24
                horas
              </span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
