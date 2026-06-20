"use client";
import { useEffect, useState } from "react";
import { detectCloud, getStoredPin, isCloud, loadData, saveData } from "@/lib/storage";
import { emptyData, catMeta, type AppData, type CatKey, type Movimiento } from "@/lib/types";
import { todayISO, monthKey } from "@/lib/format";
import Gate from "@/components/Gate";
import Dashboard from "@/components/Dashboard";
import Historial from "@/components/Historial";
import Presupuestos from "@/components/Presupuestos";
import Registrar from "@/components/Registrar";

type Tab = "dashboard" | "historial" | "presupuestos";

export default function Page() {
  const [ready, setReady] = useState(false);
  const [firstTime, setFirstTime] = useState(false);
  const [unlocked, setUnlocked] = useState(false);
  const [data, setData] = useState<AppData>(emptyData());
  const [mes, setMes] = useState(monthKey(todayISO()));
  const [tab, setTab] = useState<Tab>("dashboard");
  const [editing, setEditing] = useState<Movimiento | null>(null);

  useEffect(() => {
    detectCloud().then((cloud) => {
      setFirstTime(!cloud && getStoredPin() === "");
      setReady(true);
    });
  }, []);

  async function handleUnlock(pin: string) {
    const d = await loadData(pin); // lanza si PIN incorrecto
    setData(d);
    setUnlocked(true);
  }

  function persist(next: AppData) {
    setData(next);
    saveData(next);
  }
  function upsert(m: Movimiento) {
    const exists = data.movimientos.some((x) => x.id === m.id);
    const movimientos = exists ? data.movimientos.map((x) => (x.id === m.id ? m : x)) : [...data.movimientos, m];
    persist({ ...data, movimientos });
    setEditing(null);
  }
  function del(id: string) {
    persist({ ...data, movimientos: data.movimientos.filter((x) => x.id !== id) });
    setEditing(null);
  }
  function setPres(cat: CatKey, monto: number) {
    persist({ ...data, presupuestos: { ...data.presupuestos, [cat]: monto } });
  }

  function nuevo() {
    setEditing({
      id: (globalThis.crypto?.randomUUID?.() ?? String(Date.now() + Math.random())),
      fecha: todayISO(), categoria: "productos", descripcion: "", proveedor: "", monto: 0, metodo: "Efectivo", nota: "",
    });
  }

  function exportarCSV() {
    const header = ["Fecha", "Categoría", "Descripción", "Proveedor", "Monto", "Método", "Nota"];
    const esc = (s: string) => `"${(s ?? "").replace(/"/g, '""')}"`;
    const rows = [...data.movimientos].sort((a, b) => (a.fecha < b.fecha ? 1 : -1))
      .map((m) => [m.fecha, catMeta(m.categoria).label, m.descripcion, m.proveedor, String(m.monto), m.metodo, m.nota]);
    const csv = "﻿" + [header, ...rows].map((r) => r.map(esc).join(";")).join("\r\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `control-compras-${todayISO()}.csv`; a.click();
    URL.revokeObjectURL(url);
  }

  if (!ready) return <div className="grid min-h-screen place-items-center text-slate-400">Cargando…</div>;
  if (!unlocked) return <Gate firstTime={firstTime} onUnlock={handleUnlock} />;

  return (
    <div className="mx-auto max-w-6xl px-4 pb-24 pt-5 sm:px-6">
      {/* header */}
      <header className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand text-lg text-white">📊</span>
          <h1 className="font-display text-xl font-bold">Control de Compras</h1>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-500">
          {isCloud() ? "🔒 Nube" : "💾 Local"}
        </span>
        <div className="ml-auto flex items-center gap-2">
          <button onClick={exportarCSV} className="btn-ghost px-3 py-2 text-sm">⬇ Exportar</button>
          <button onClick={() => setUnlocked(false)} className="btn-ghost px-3 py-2 text-sm" title="Bloquear">🔒</button>
          <button onClick={nuevo} className="btn-brand px-4 py-2 text-sm">＋ Registrar</button>
        </div>
      </header>

      {/* tabs */}
      <nav className="mt-5 flex gap-1 border-b border-slate-200">
        {([["dashboard", "Dashboard"], ["historial", "Historial"], ["presupuestos", "Presupuestos"]] as [Tab, string][]).map(([k, label]) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            className={`-mb-px border-b-2 px-4 py-2.5 text-sm font-semibold transition ${tab === k ? "border-brand text-brand" : "border-transparent text-slate-500 hover:text-ink"}`}
          >
            {label}
          </button>
        ))}
      </nav>

      <div className="mt-6">
        {tab === "dashboard" && <Dashboard data={data} mes={mes} setMes={setMes} />}
        {tab === "historial" && <Historial data={data} onEdit={(m) => setEditing(m)} />}
        {tab === "presupuestos" && <Presupuestos data={data} onChange={setPres} />}
      </div>

      {/* botón flotante registrar (móvil) */}
      <button onClick={nuevo} className="btn-brand fixed bottom-5 right-5 h-14 w-14 rounded-full text-2xl shadow-card sm:hidden">＋</button>

      <Registrar value={editing} onSave={upsert} onDelete={del} onClose={() => setEditing(null)} />
    </div>
  );
}
