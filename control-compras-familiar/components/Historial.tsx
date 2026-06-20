"use client";
import { useState } from "react";
import { CATEGORIAS, catMeta, type AppData, type Movimiento, type CatKey } from "@/lib/types";
import { formatCLP, fmtFecha, monthKey, monthLabelLong } from "@/lib/format";

export default function Historial({ data, onEdit }: { data: AppData; onEdit: (m: Movimiento) => void }) {
  const [mes, setMes] = useState<string>("todos");
  const [cat, setCat] = useState<CatKey | "todas">("todas");
  const [q, setQ] = useState("");

  const months = [...new Set(data.movimientos.map((m) => monthKey(m.fecha)))].sort().reverse();

  const rows = data.movimientos
    .filter((m) => (mes === "todos" ? true : monthKey(m.fecha) === mes))
    .filter((m) => (cat === "todas" ? true : m.categoria === cat))
    .filter((m) => {
      const t = q.trim().toLowerCase();
      return !t || m.descripcion.toLowerCase().includes(t) || m.proveedor.toLowerCase().includes(t);
    })
    .sort((a, b) => (a.fecha < b.fecha ? 1 : -1));

  const total = rows.reduce((s, m) => s + m.monto, 0);

  return (
    <div className="card overflow-hidden">
      {/* filtros */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 p-4">
        <select value={mes} onChange={(e) => setMes(e.target.value)} className="input w-auto">
          <option value="todos">Todos los meses</option>
          {months.map((mk) => <option key={mk} value={mk}>{monthLabelLong(mk)}</option>)}
        </select>
        <select value={cat} onChange={(e) => setCat(e.target.value as CatKey | "todas")} className="input w-auto">
          <option value="todas">Todas las categorías</option>
          {CATEGORIAS.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
        </select>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar descripción o proveedor…" className="input flex-1 min-w-[180px]" />
        <span className="ml-auto text-sm text-slate-500">{rows.length} mov. · <b className="text-ink">{formatCLP(total)}</b></span>
      </div>

      {rows.length === 0 ? (
        <p className="p-10 text-center text-sm text-slate-400">No hay movimientos con estos filtros.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-400">
                <th className="px-4 py-3">Fecha</th>
                <th className="px-4 py-3">Categoría</th>
                <th className="px-4 py-3">Descripción</th>
                <th className="hidden px-4 py-3 sm:table-cell">Proveedor</th>
                <th className="hidden px-4 py-3 md:table-cell">Método</th>
                <th className="px-4 py-3 text-right">Monto</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((m) => {
                const c = catMeta(m.categoria);
                return (
                  <tr key={m.id} onClick={() => onEdit(m)} className="cursor-pointer border-b border-slate-50 hover:bg-slate-50">
                    <td className="whitespace-nowrap px-4 py-3 text-slate-500">{fmtFecha(m.fecha)}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium text-white" style={{ background: c.color }}>
                        {c.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium">{m.descripcion}{m.nota && <span className="block text-xs font-normal text-slate-400">{m.nota}</span>}</td>
                    <td className="hidden px-4 py-3 text-slate-500 sm:table-cell">{m.proveedor || "—"}</td>
                    <td className="hidden px-4 py-3 text-slate-500 md:table-cell">{m.metodo}</td>
                    <td className="px-4 py-3 text-right font-semibold">{formatCLP(m.monto)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
