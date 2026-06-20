"use client";
import { CATEGORIAS, type AppData, type CatKey } from "@/lib/types";
import { formatCLP, monthKey, monthLabel, monthLabelLong, prevMonthKey } from "@/lib/format";
import Donut from "./Donut";

export default function Dashboard({ data, mes, setMes }: { data: AppData; mes: string; setMes: (m: string) => void }) {
  const movsMes = data.movimientos.filter((m) => monthKey(m.fecha) === mes);
  const byCat = (key: CatKey, month = mes) =>
    data.movimientos.filter((m) => m.categoria === key && monthKey(m.fecha) === month).reduce((s, m) => s + m.monto, 0);

  const totalMes = movsMes.reduce((s, m) => s + m.monto, 0);
  const totalGastos = CATEGORIAS.filter((c) => c.grupo === "gasto").reduce((s, c) => s + byCat(c.key), 0);
  const totalRetiros = byCat("retiros");

  const prevKey = prevMonthKey(mes);
  const prevTotal = data.movimientos.filter((m) => monthKey(m.fecha) === prevKey).reduce((s, m) => s + m.monto, 0);
  const delta = prevTotal > 0 ? Math.round(((totalMes - prevTotal) / prevTotal) * 100) : null;

  // últimos 6 meses
  let k = mes;
  const last6: { key: string; total: number }[] = [];
  for (let i = 0; i < 6; i++) {
    const t = data.movimientos.filter((m) => monthKey(m.fecha) === k).reduce((s, m) => s + m.monto, 0);
    last6.unshift({ key: k, total: t });
    k = prevMonthKey(k);
  }
  const maxBar = Math.max(...last6.map((x) => x.total), 1);

  const segments = CATEGORIAS.map((c) => ({ label: c.label, value: byCat(c.key), color: c.color })).filter((s) => s.value > 0);

  // selector de meses disponibles (incluye el actual aunque esté vacío)
  const monthsSet = new Set(data.movimientos.map((m) => monthKey(m.fecha)));
  monthsSet.add(mes);
  const months = [...monthsSet].sort().reverse();

  return (
    <div className="space-y-6">
      {/* encabezado mes + total */}
      <div className="card p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-sm text-slate-500">Total del mes</div>
            <div className="font-display text-4xl font-extrabold">{formatCLP(totalMes)}</div>
            {delta !== null && (
              <div className={`mt-1 text-sm ${delta > 0 ? "text-rose-600" : "text-money"}`}>
                {delta > 0 ? "▲" : "▼"} {Math.abs(delta)}% vs. {monthLabel(prevKey)}
              </div>
            )}
          </div>
          <select value={mes} onChange={(e) => setMes(e.target.value)} className="input w-auto font-semibold capitalize">
            {months.map((mk) => <option key={mk} value={mk}>{monthLabelLong(mk)}</option>)}
          </select>
        </div>
        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2 border-t border-slate-100 pt-4 text-sm">
          <div><span className="text-slate-500">Gastos operativos: </span><b>{formatCLP(totalGastos)}</b></div>
          <div><span className="text-slate-500">Retiros: </span><b>{formatCLP(totalRetiros)}</b></div>
          <div><span className="text-slate-500">Movimientos: </span><b>{movsMes.length}</b></div>
        </div>
      </div>

      {/* tarjetas por categoría */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        {CATEGORIAS.map((c) => {
          const v = byCat(c.key);
          const n = movsMes.filter((m) => m.categoria === c.key).length;
          return (
            <div key={c.key} className="card p-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full" style={{ background: c.color }} />
                <span className="text-xs font-medium text-slate-500">{c.label}</span>
              </div>
              <div className="mt-2 font-display text-xl font-bold">{formatCLP(v)}</div>
              <div className="text-xs text-slate-400">{n} mov.</div>
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* donut distribución */}
        <div className="card p-6">
          <h3 className="font-display font-bold">Distribución del gasto</h3>
          {totalMes > 0 ? (
            <div className="mt-4 flex flex-wrap items-center gap-6">
              <div className="relative shrink-0">
                <Donut segments={segments} />
                <div className="absolute inset-0 grid place-content-center text-center">
                  <div className="text-xs text-slate-400">Total</div>
                  <div className="font-display text-lg font-bold">{formatCLP(totalMes)}</div>
                </div>
              </div>
              <ul className="flex-1 space-y-2 text-sm">
                {CATEGORIAS.map((c) => {
                  const v = byCat(c.key);
                  const pct = totalMes ? Math.round((v / totalMes) * 100) : 0;
                  return (
                    <li key={c.key} className="flex items-center gap-2">
                      <span className="h-3 w-3 rounded-full" style={{ background: c.color }} />
                      <span className="flex-1 text-slate-600">{c.label}</span>
                      <span className="font-semibold">{formatCLP(v)}</span>
                      <span className="w-9 text-right text-slate-400">{pct}%</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : (
            <p className="mt-6 text-sm text-slate-400">Sin movimientos este mes. Registra el primero con el botón “＋ Registrar”.</p>
          )}
        </div>

        {/* presupuesto vs real */}
        <div className="card p-6">
          <h3 className="font-display font-bold">Presupuesto vs. real</h3>
          <div className="mt-4 space-y-3">
            {CATEGORIAS.map((c) => {
              const real = byCat(c.key);
              const pres = data.presupuestos[c.key] || 0;
              const pct = pres > 0 ? Math.min(100, Math.round((real / pres) * 100)) : 0;
              const over = pres > 0 && real > pres;
              return (
                <div key={c.key}>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">{c.label}</span>
                    <span className={over ? "font-semibold text-rose-600" : "text-slate-500"}>
                      {formatCLP(real)} {pres > 0 && <span className="text-slate-400">/ {formatCLP(pres)}</span>}
                    </span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full transition-all" style={{ width: `${pres > 0 ? pct : 0}%`, background: over ? "#e11d48" : c.color }} />
                  </div>
                  {over && <div className="mt-0.5 text-xs text-rose-600">Excedido {formatCLP(real - pres)}</div>}
                </div>
              );
            })}
            {CATEGORIAS.every((c) => !data.presupuestos[c.key]) && (
              <p className="text-sm text-slate-400">Define presupuestos en la pestaña “Presupuestos” para ver el avance.</p>
            )}
          </div>
        </div>
      </div>

      {/* comparación últimos 6 meses */}
      <div className="card p-6">
        <h3 className="font-display font-bold">Últimos 6 meses</h3>
        <div className="mt-5 flex items-end justify-between gap-2" style={{ height: 160 }}>
          {last6.map((b) => (
            <div key={b.key} className="flex flex-1 flex-col items-center gap-2">
              <div className="text-[11px] font-semibold text-slate-500">{b.total > 0 ? formatCLP(b.total) : ""}</div>
              <div className="flex w-full items-end justify-center" style={{ height: 110 }}>
                <div
                  className={`w-8 rounded-t-lg ${b.key === mes ? "bg-brand" : "bg-slate-300"}`}
                  style={{ height: `${Math.max(4, (b.total / maxBar) * 100)}%` }}
                />
              </div>
              <div className="text-[11px] capitalize text-slate-400">{monthLabel(b.key)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
