"use client";
import { useState } from "react";
import { ESPECIALIDADES, COMUNAS, BANCOS, TIPOS_CUENTA } from "@/lib/data";
import { validateRut, validatePhone, validateEmail, formatPhone, cleanPhone } from "@/lib/validations";
import { submitRegistro } from "@/lib/submit";

const STEPS = ["Datos personales", "Especialización", "Zona de cobertura", "Datos bancarios", "Documentos"];

export default function RegistroPage() {
  const [step, setStep] = useState(0);
  const [err, setErr] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [f, setF] = useState({
    nombre: "", rut: "", whatsapp: "", email: "", direccion: "", comuna: "",
    espPrincipal: "", espSecundarias: [] as string[], anios: "", herramientas: "",
    comunasCobertura: [] as string[], movilizacion: "",
    banco: "", tipoCuenta: "", numeroCuenta: "", titularNombre: "", titularRut: "",
  });
  const [files, setFiles] = useState<{ cedula?: File; certificado?: File; foto?: File }>({});

  const set = (k: string, v: unknown) => setF((s) => ({ ...s, [k]: v }));
  const toggle = (k: "espSecundarias" | "comunasCobertura", v: string) =>
    setF((s) => ({ ...s, [k]: s[k].includes(v) ? s[k].filter((x) => x !== v) : [...s[k], v] }));

  function validateStep(i: number) {
    const e: Record<string, string> = {};
    if (i === 0) {
      if (!f.nombre.trim()) e.nombre = "Requerido.";
      if (!validateRut(f.rut)) e.rut = "RUT inválido.";
      if (!validatePhone(f.whatsapp)) e.whatsapp = "Teléfono inválido.";
      if (!validateEmail(f.email)) e.email = "Email inválido.";
      if (!f.direccion.trim()) e.direccion = "Requerido.";
      if (!f.comuna.trim()) e.comuna = "Requerido.";
    }
    if (i === 1) {
      if (!f.espPrincipal) e.espPrincipal = "Elige una.";
      if (!f.anios || Number(f.anios) < 0) e.anios = "Indica los años.";
      if (!f.herramientas) e.herramientas = "Selecciona.";
    }
    if (i === 2) {
      if (f.comunasCobertura.length === 0) e.comunasCobertura = "Elige al menos una comuna.";
      if (!f.movilizacion) e.movilizacion = "Selecciona.";
    }
    if (i === 3) {
      if (!f.banco) e.banco = "Requerido.";
      if (!f.tipoCuenta) e.tipoCuenta = "Requerido.";
      if (!f.numeroCuenta.trim()) e.numeroCuenta = "Requerido.";
      if (!f.titularNombre.trim()) e.titularNombre = "Requerido.";
      if (!validateRut(f.titularRut)) e.titularRut = "RUT inválido.";
    }
    if (i === 4) {
      if (!files.cedula) e.cedula = "Sube tu cédula.";
    }
    setErr(e);
    return Object.keys(e).length === 0;
  }

  function next() {
    if (validateStep(step)) { setErr({}); setStep((s) => Math.min(s + 1, STEPS.length - 1)); window.scrollTo(0, 0); }
  }
  function back() { setErr({}); setStep((s) => Math.max(0, s - 1)); window.scrollTo(0, 0); }

  async function submit() {
    if (!validateStep(4)) return;
    setLoading(true);
    const fd = new FormData();
    Object.entries(f).forEach(([k, v]) => fd.append(k, Array.isArray(v) ? v.join("; ") : String(v)));
    fd.set("whatsapp", formatPhone(f.whatsapp));
    if (files.cedula) fd.append("cedula", files.cedula);
    if (files.certificado) fd.append("certificado", files.certificado);
    if (files.foto) fd.append("foto", files.foto);
    fd.append("estado", "Pendiente"); // campo interno (admin), no visible al maestro
    fd.append("fecha", new Date().toISOString());
    const res = await submitRegistro(fd);
    setLoading(false);
    if (res.ok) setDone(true);
    else setErr({ form: "No pudimos enviar. Intenta de nuevo." });
  }

  if (done) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-5 text-center">
        <div className="grid h-20 w-20 place-items-center rounded-full bg-naranjo/10 text-5xl">📋</div>
        <h1 className="mt-6 text-3xl font-extrabold">Recibimos tus datos</h1>
        <p className="mt-3 text-lg text-navy/70">
          Revisaremos tu registro y te activamos para empezar a recibir trabajos. Te avisamos por WhatsApp.
        </p>
      </main>
    );
  }

  const pct = Math.round(((step + 1) / STEPS.length) * 100);

  return (
    <main className="mx-auto max-w-md px-5 pb-28">
      <header className="-mx-5 bg-navy px-5 pb-5 pt-8 text-white">
        <div className="text-xs font-bold uppercase tracking-widest text-naranjo">TradeGlobalChile · Registro de maestro</div>
        <h1 className="mt-2 text-2xl font-extrabold">{STEPS[step]}</h1>
        <div className="mt-4 flex items-center gap-3">
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/15">
            <div className="h-full rounded-full bg-naranjo transition-all" style={{ width: `${pct}%` }} />
          </div>
          <span className="text-sm font-semibold text-white/80">{step + 1}/{STEPS.length}</span>
        </div>
      </header>

      <div className="mt-6 space-y-5 rounded-2xl bg-white p-6 shadow-card">
        {step === 0 && (
          <>
            <Field label="Nombre completo" v={f.nombre} set={(x) => set("nombre", x)} e={err.nombre} ph="Juan Pérez" />
            <Field label="RUT" v={f.rut} set={(x) => set("rut", x)} e={err.rut} ph="12.345.678-9" />
            <div>
              <label className="lbl">WhatsApp / teléfono</label>
              <div className="flex">
                <span className="grid place-items-center rounded-l-xl border border-r-0 border-navy/15 bg-warm px-3 text-navy/60">+56</span>
                <input value={f.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} inputMode="tel" placeholder="9 1234 5678" className={`field rounded-l-none ${err.whatsapp ? "field-err" : ""}`} />
              </div>
              {err.whatsapp && <p className="err">{err.whatsapp}</p>}
            </div>
            <Field label="Email" v={f.email} set={(x) => set("email", x)} e={err.email} ph="tu@correo.cl" type="email" />
            <Field label="Dirección" v={f.direccion} set={(x) => set("direccion", x)} e={err.direccion} ph="Calle 123" />
            <SelectField label="Comuna" v={f.comuna} set={(x) => set("comuna", x)} e={err.comuna} options={COMUNAS} />
          </>
        )}

        {step === 1 && (
          <>
            <SelectField label="Especialidad principal" v={f.espPrincipal} set={(x) => set("espPrincipal", x)} e={err.espPrincipal} options={ESPECIALIDADES} />
            <div>
              <label className="lbl">Especialidades secundarias <span className="font-normal text-navy/40">— opcional</span></label>
              <div className="flex flex-wrap gap-2">
                {ESPECIALIDADES.map((x) => (
                  <button type="button" key={x} onClick={() => toggle("espSecundarias", x)}
                    className={`chip ${f.espSecundarias.includes(x) ? "border-naranjo bg-naranjo text-white" : "border-navy/20 text-navy/70"}`}>{x}</button>
                ))}
              </div>
            </div>
            <Field label="Años de experiencia" v={f.anios} set={(x) => set("anios", x)} e={err.anios} ph="5" type="number" />
            <YesNo label="¿Tiene herramientas propias?" v={f.herramientas} set={(x) => set("herramientas", x)} e={err.herramientas} />
          </>
        )}

        {step === 2 && (
          <>
            <MultiComuna selected={f.comunasCobertura} toggle={(c) => toggle("comunasCobertura", c)} e={err.comunasCobertura} />
            <YesNo label="¿Tiene movilización propia?" v={f.movilizacion} set={(x) => set("movilizacion", x)} e={err.movilizacion} />
          </>
        )}

        {step === 3 && (
          <>
            <p className="rounded-xl bg-warm p-3 text-sm text-navy/70">💵 Estos datos son para tus <b>liquidaciones semanales</b> por transferencia.</p>
            <SelectField label="Banco" v={f.banco} set={(x) => set("banco", x)} e={err.banco} options={BANCOS} />
            <SelectField label="Tipo de cuenta" v={f.tipoCuenta} set={(x) => set("tipoCuenta", x)} e={err.tipoCuenta} options={TIPOS_CUENTA} />
            <Field label="Número de cuenta" v={f.numeroCuenta} set={(x) => set("numeroCuenta", x)} e={err.numeroCuenta} ph="00012345678" type="text" />
            <Field label="Nombre del titular" v={f.titularNombre} set={(x) => set("titularNombre", x)} e={err.titularNombre} ph="Juan Pérez" />
            <Field label="RUT del titular" v={f.titularRut} set={(x) => set("titularRut", x)} e={err.titularRut} ph="12.345.678-9" />
          </>
        )}

        {step === 4 && (
          <>
            <FileField label="Cédula de identidad (foto)" required onPick={(file) => setFiles((s) => ({ ...s, cedula: file }))} picked={files.cedula} e={err.cedula} />
            <FileField label="Certificado o constancia de oficio" onPick={(file) => setFiles((s) => ({ ...s, certificado: file }))} picked={files.certificado} />
            <FileField label="Foto de perfil" onPick={(file) => setFiles((s) => ({ ...s, foto: file }))} picked={files.foto} />
          </>
        )}
      </div>

      {/* navegación fija abajo */}
      <div className="fixed inset-x-0 bottom-0 mx-auto flex max-w-md gap-3 bg-warm/95 p-4 backdrop-blur">
        {step > 0 && <button onClick={back} className="rounded-xl border border-navy/20 px-5 py-4 font-semibold text-navy">Atrás</button>}
        {step < STEPS.length - 1 ? (
          <button onClick={next} className="btn-cta flex-1">Continuar</button>
        ) : (
          <button onClick={submit} disabled={loading} className="btn-cta flex-1">{loading ? "Enviando…" : "Enviar registro"}</button>
        )}
      </div>
      {err.form && <p className="err mt-3 text-center">{err.form}</p>}
    </main>
  );
}

/* ---------- subcomponentes ---------- */
function Field({ label, v, set, e, ph, type = "text" }: { label: string; v: string; set: (x: string) => void; e?: string; ph?: string; type?: string }) {
  return (
    <div>
      <label className="lbl">{label}</label>
      <input type={type} value={v} onChange={(ev) => set(ev.target.value)} placeholder={ph} className={`field ${e ? "field-err" : ""}`} />
      {e && <p className="err">{e}</p>}
    </div>
  );
}
function SelectField({ label, v, set, e, options }: { label: string; v: string; set: (x: string) => void; e?: string; options: string[] }) {
  return (
    <div>
      <label className="lbl">{label}</label>
      <select value={v} onChange={(ev) => set(ev.target.value)} className={`field ${e ? "field-err" : ""}`}>
        <option value="">Selecciona…</option>
        {options.map((x) => <option key={x} value={x}>{x}</option>)}
      </select>
      {e && <p className="err">{e}</p>}
    </div>
  );
}
function YesNo({ label, v, set, e }: { label: string; v: string; set: (x: string) => void; e?: string }) {
  return (
    <div>
      <label className="lbl">{label}</label>
      <div className="flex gap-3">
        {["Sí", "No"].map((o) => (
          <button type="button" key={o} onClick={() => set(o)}
            className={`flex-1 rounded-xl border py-3 font-semibold transition ${v === o ? "border-naranjo bg-naranjo text-white" : "border-navy/20 text-navy/70"}`}>{o}</button>
        ))}
      </div>
      {e && <p className="err">{e}</p>}
    </div>
  );
}
function FileField({ label, onPick, picked, required, e }: { label: string; onPick: (f: File) => void; picked?: File; required?: boolean; e?: string }) {
  return (
    <div>
      <label className="lbl">{label} {required && <span className="text-naranjo">*</span>}</label>
      <label className={`flex cursor-pointer items-center gap-3 rounded-xl border-2 border-dashed p-4 ${e ? "border-red-400" : picked ? "border-naranjo bg-naranjo/5" : "border-navy/20"}`}>
        <span className="text-2xl">{picked ? "✅" : "📷"}</span>
        <span className="flex-1 text-sm text-navy/70">{picked ? picked.name : "Toca para subir foto o archivo"}</span>
        <input type="file" accept="image/*,.pdf" className="hidden" onChange={(ev) => ev.target.files?.[0] && onPick(ev.target.files[0])} />
      </label>
      {e && <p className="err">{e}</p>}
    </div>
  );
}
function MultiComuna({ selected, toggle, e }: { selected: string[]; toggle: (c: string) => void; e?: string }) {
  const [q, setQ] = useState("");
  const list = COMUNAS.filter((c) => c.toLowerCase().includes(q.toLowerCase()));
  return (
    <div>
      <label className="lbl">Comunas donde trabajas <span className="font-normal text-navy/40">({selected.length} seleccionadas)</span></label>
      <input value={q} onChange={(ev) => setQ(ev.target.value)} placeholder="Buscar comuna…" className="field mb-2" />
      <div className={`max-h-56 overflow-y-auto rounded-xl border p-2 ${e ? "border-red-400" : "border-navy/15"}`}>
        {list.map((c) => (
          <label key={c} className="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-warm">
            <input type="checkbox" checked={selected.includes(c)} onChange={() => toggle(c)} className="h-4 w-4 accent-naranjo" />
            <span className="text-sm">{c}</span>
          </label>
        ))}
      </div>
      {selected.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {selected.map((c) => (
            <span key={c} onClick={() => toggle(c)} className="cursor-pointer rounded-full bg-naranjo/10 px-2.5 py-1 text-xs font-medium text-naranjo-600">{c} ✕</span>
          ))}
        </div>
      )}
      {e && <p className="err">{e}</p>}
    </div>
  );
}
