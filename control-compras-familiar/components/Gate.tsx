"use client";
import { useState } from "react";
import { isCloud } from "@/lib/storage";

export default function Gate({
  firstTime,
  onUnlock,
}: {
  firstTime: boolean;
  onUnlock: (pin: string) => Promise<void>;
}) {
  const [pin, setPin] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pin.length < 4) {
      setErr("El PIN debe tener al menos 4 dígitos.");
      return;
    }
    setLoading(true);
    setErr("");
    try {
      await onUnlock(pin);
    } catch {
      setErr("PIN incorrecto.");
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen place-items-center p-4">
      <form onSubmit={submit} className="card w-full max-w-sm p-8 text-center">
        <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-brand text-2xl text-white">🔐</div>
        <h1 className="mt-5 font-display text-2xl font-bold">Control de Compras</h1>
        <p className="mt-1 text-sm text-slate-500">
          {firstTime ? "Crea un PIN para proteger tus datos." : "Ingresa tu PIN para continuar."}
        </p>
        <input
          type="password"
          inputMode="numeric"
          value={pin}
          onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
          placeholder="• • • •"
          autoFocus
          autoComplete="off"
          name="cc-pin"
          className="input mt-6 text-center text-2xl tracking-[0.4em]"
        />
        {err && <p className="mt-2 text-sm text-rose-600">{err}</p>}
        <button type="submit" disabled={loading} className="btn-brand mt-5 w-full py-3 disabled:opacity-60">
          {loading ? "Entrando…" : firstTime ? "Crear PIN y entrar" : "Entrar"}
        </button>
        <p className="mt-4 text-xs text-slate-400">
          {isCloud() ? "🔒 Datos sincronizados en la nube" : "💾 Datos guardados en este dispositivo"}
        </p>
      </form>
    </div>
  );
}
