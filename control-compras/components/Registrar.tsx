"use client";
import { useEffect, useState } from "react";
import { CATEGORIAS, METODOS, type Movimiento } from "@/lib/types";
import { formatCLP } from "@/lib/format";

export default function Registrar({
  value,
  onSave,
  onDelete,
  onClose,
}: {
  value: Movimiento | null;
  onSave: (m: Movimiento) => void;
  onDelete?: (id: string) => void;
  onClose: () => void;
}) {
  const [m, setM] = useState<Movimiento | null>(value);
  useEffect(() => setM(value), [value]);
  if (!m) return null;

  const isEdit = !!onDelete && value && value.descripcion !== "";
  const set = <K extends keyof Movimiento>(k: K, v: Movimiento[K]) => setM({ ...m, [k]: v });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!m.descripcion.trim() || !m.monto || m.monto <= 0) return;
    onSave(m);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <form
        onSubmit={submit}
        className="relative w-full max-w-lg rounded-t-3xl bg-white p-6 shadow-2xl sm:rounded-3xl"
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-xl font-bold">{value && value.id && isEdit ? "Editar movimiento" : "Nuevo movimiento"}</h2>
          <button type="button" onClick={onClose} className="grid h-9 w-9 place-items-center rounded-full hover:bg-slate-100">✕</button>
        </div>

        {/* categoría */}
        <div className="label">Categoría</div>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {CATEGORIAS.map((c) => (
            <button
              key={c.key}
              type="button"
              onClick={() => set("categoria", c.key)}
              className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium transition ${m.categoria === c.key ? "text-white" : "border-slate-200 text-slate-600 hover:border-slate-400"}`}
              style={m.categoria === c.key ? { background: c.color, borderColor: c.color } : {}}
            >
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: m.categoria === c.key ? "#fff" : c.color }} />
              {c.label}
            </button>
          ))}
        </div>

        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Monto (CLP)</label>
            <input
              type="number" min={0} inputMode="numeric"
              value={m.monto || ""}
              onChange={(e) => set("monto", Number(e.target.value))}
              placeholder="0" className="input text-lg font-semibold" autoFocus
            />
            {m.monto > 0 && <p className="mt-1 text-xs text-money">{formatCLP(m.monto)}</p>}
          </div>
          <div>
            <label className="label">Fecha</label>
            <input type="date" value={m.fecha} onChange={(e) => set("fecha", e.target.value)} className="input" />
          </div>
          <div className="sm:col-span-2">
            <label className="label">Descripción</label>
            <input value={m.descripcion} onChange={(e) => set("descripcion", e.target.value)} placeholder="Ej: Caja de guantes nitrilo" className="input" />
          </div>
          <div>
            <label className="label">Proveedor</label>
            <input value={m.proveedor} onChange={(e) => set("proveedor", e.target.value)} placeholder="Ej: Distribuidora X" className="input" />
          </div>
          <div>
            <label className="label">Método de pago</label>
            <select value={m.metodo} onChange={(e) => set("metodo", e.target.value)} className="input">
              {METODOS.map((x) => <option key={x} value={x}>{x}</option>)}
            </select>
          </div>
          <div className="sm:col-span-2">
            <label className="label">Nota (opcional)</label>
            <input value={m.nota} onChange={(e) => set("nota", e.target.value)} placeholder="Detalle adicional…" className="input" />
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          {isEdit && onDelete && (
            <button type="button" onClick={() => onDelete(m.id)} className="btn border border-rose-200 px-4 py-3 text-rose-600 hover:bg-rose-50">
              Eliminar
            </button>
          )}
          <button type="submit" className="btn-brand flex-1 py-3">Guardar</button>
        </div>
      </form>
    </div>
  );
}
