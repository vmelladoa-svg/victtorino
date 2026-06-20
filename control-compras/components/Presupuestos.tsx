"use client";
import { CATEGORIAS, type AppData, type CatKey } from "@/lib/types";
import { formatCLP } from "@/lib/format";

export default function Presupuestos({
  data,
  onChange,
}: {
  data: AppData;
  onChange: (cat: CatKey, monto: number) => void;
}) {
  const total = CATEGORIAS.reduce((s, c) => s + (data.presupuestos[c.key] || 0), 0);

  return (
    <div className="card max-w-2xl p-6">
      <h2 className="font-display text-xl font-bold">Presupuesto mensual</h2>
      <p className="mt-1 text-sm text-slate-500">
        Define cuánto planeas gastar por categoría cada mes. El Dashboard mostrará tu avance (real vs. presupuesto).
      </p>

      <div className="mt-6 space-y-4">
        {CATEGORIAS.map((c) => (
          <div key={c.key} className="flex items-center gap-3">
            <span className="h-3 w-3 shrink-0 rounded-full" style={{ background: c.color }} />
            <label className="flex-1 text-sm font-medium text-slate-700">{c.label}</label>
            <div className="flex items-center gap-1">
              <span className="text-slate-400">$</span>
              <input
                type="number" min={0} inputMode="numeric"
                value={data.presupuestos[c.key] || ""}
                onChange={(e) => onChange(c.key, Number(e.target.value))}
                placeholder="0"
                className="input w-40 text-right"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-between border-t border-slate-100 pt-4">
        <span className="font-medium text-slate-600">Presupuesto total / mes</span>
        <span className="font-display text-lg font-bold">{formatCLP(total)}</span>
      </div>
    </div>
  );
}
