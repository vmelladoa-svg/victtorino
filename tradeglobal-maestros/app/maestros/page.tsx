"use client";
import { useState } from "react";
import { ESPECIALIDADES, TRABAJOS_MES, COMUNAS } from "@/lib/data";
import { validatePhone, formatPhone, cleanPhone } from "@/lib/validations";
import { submitCaptacion } from "@/lib/submit";

export default function CaptacionPage() {
  const [f, setF] = useState({ nombre: "", whatsapp: "", comuna: "", especialidad: "", trabajos: "", consent: false });
  const [err, setErr] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const set = (k: string, v: string | boolean) => setF((s) => ({ ...s, [k]: v }));

  function validate() {
    const e: Record<string, string> = {};
    if (!f.nombre.trim()) e.nombre = "Ingresa tu nombre.";
    if (!validatePhone(f.whatsapp)) e.whatsapp = "WhatsApp inválido (ej: 9 1234 5678).";
    if (!f.comuna.trim()) e.comuna = "Selecciona tu comuna.";
    if (!f.especialidad) e.especialidad = "Elige tu especialidad.";
    if (!f.consent) e.consent = "Marca la casilla para continuar.";
    setErr(e);
    return Object.keys(e).length === 0;
  }

  async function onSubmit(ev: React.FormEvent) {
    ev.preventDefault();
    if (!validate()) return;
    setLoading(true);
    const res = await submitCaptacion({
      tipo: "captacion",
      nombre: f.nombre.trim(),
      whatsapp: formatPhone(f.whatsapp),
      whatsapp_raw: "+56" + cleanPhone(f.whatsapp).replace(/^56/, ""),
      comuna: f.comuna,
      especialidad: f.especialidad,
      trabajos_mes: f.trabajos || null,
      fecha: new Date().toISOString(),
    });
    setLoading(false);
    if (res.ok) setDone(true);
    else setErr({ form: "No pudimos enviar. Intenta de nuevo." });
  }

  if (done) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-5 text-center">
        <div className="grid h-20 w-20 place-items-center rounded-full bg-naranjo/10 text-5xl">✅</div>
        <h1 className="mt-6 text-3xl font-extrabold">¡Listo, {f.nombre.split(" ")[0]}!</h1>
        <p className="mt-3 text-lg text-navy/70">
          Te contactamos por WhatsApp con los precios y los próximos trabajos.
        </p>
        <p className="mt-6 rounded-xl bg-white p-4 text-sm text-navy/60 shadow-card">
          📲 Revisa tu WhatsApp <b>{formatPhone(f.whatsapp)}</b> en las próximas horas.
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-md px-5 pb-12">
      {/* header */}
      <header className="-mx-5 bg-navy px-5 pb-8 pt-10 text-white">
        <div className="text-xs font-bold uppercase tracking-widest text-naranjo">TradeGlobalChile · Maestros</div>
        <h1 className="mt-3 text-3xl font-extrabold leading-tight">
          Precios mayoristas + <span className="text-naranjo">trabajos pagados cada semana</span>
        </h1>
        <p className="mt-3 text-white/80">
          Regístrate gratis y empieza a recibir pedidos y precios de mayorista en grifería, lavaplatos y más.
        </p>
        <div className="mt-5 flex flex-wrap gap-2 text-sm">
          {["💵 Pagos semanales por transferencia", "✅ Empresa verificada", "🆓 Sin costo de inscripción"].map((t) => (
            <span key={t} className="rounded-full bg-white/10 px-3 py-1.5 font-medium">{t}</span>
          ))}
        </div>
      </header>

      {/* form */}
      <form onSubmit={onSubmit} className="mt-6 space-y-5 rounded-2xl bg-white p-6 shadow-card">
        <div>
          <label className="lbl">Nombre completo</label>
          <input value={f.nombre} onChange={(e) => set("nombre", e.target.value)} placeholder="Juan Pérez" className={`field ${err.nombre ? "field-err" : ""}`} />
          {err.nombre && <p className="err">{err.nombre}</p>}
        </div>

        <div>
          <label className="lbl">WhatsApp</label>
          <div className="flex">
            <span className="grid place-items-center rounded-l-xl border border-r-0 border-navy/15 bg-warm px-3 text-navy/60">+56</span>
            <input value={f.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} inputMode="tel" placeholder="9 1234 5678" className={`field rounded-l-none ${err.whatsapp ? "field-err" : ""}`} />
          </div>
          {err.whatsapp && <p className="err">{err.whatsapp}</p>}
        </div>

        <div>
          <label className="lbl">Comuna</label>
          <input list="comunas" value={f.comuna} onChange={(e) => set("comuna", e.target.value)} placeholder="Ej: Maipú" className={`field ${err.comuna ? "field-err" : ""}`} />
          <datalist id="comunas">{COMUNAS.map((c) => <option key={c} value={c} />)}</datalist>
          {err.comuna && <p className="err">{err.comuna}</p>}
        </div>

        <div>
          <label className="lbl">Especialidad</label>
          <select value={f.especialidad} onChange={(e) => set("especialidad", e.target.value)} className={`field ${err.especialidad ? "field-err" : ""}`}>
            <option value="">Selecciona…</option>
            {ESPECIALIDADES.map((x) => <option key={x} value={x}>{x}</option>)}
          </select>
          {err.especialidad && <p className="err">{err.especialidad}</p>}
        </div>

        <div>
          <label className="lbl">Trabajos al mes (aprox.) <span className="font-normal text-navy/40">— opcional</span></label>
          <select value={f.trabajos} onChange={(e) => set("trabajos", e.target.value)} className="field">
            <option value="">Prefiero no decir</option>
            {TRABAJOS_MES.map((x) => <option key={x} value={x}>{x} trabajos</option>)}
          </select>
        </div>

        <label className="flex items-start gap-3 rounded-xl bg-warm p-3">
          <input type="checkbox" checked={f.consent} onChange={(e) => set("consent", e.target.checked)} className="mt-1 h-5 w-5 accent-naranjo" />
          <span className="text-sm text-navy/80">Quiero recibir <b>precios mayoristas y trabajos</b>.</span>
        </label>
        {err.consent && <p className="err -mt-3">{err.consent}</p>}

        <button type="submit" disabled={loading} className="btn-cta">
          {loading ? "Enviando…" : "Quiero registrarme"}
        </button>
        {err.form && <p className="err text-center">{err.form}</p>}
        <p className="text-center text-xs text-navy/40">Toma ~30 segundos · Sin compromiso</p>
      </form>
    </main>
  );
}
