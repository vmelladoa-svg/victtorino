"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

interface Props {
  id: string;
  nombre: string;
}

export default function AccionesComerciante({ id, nombre }: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [loading, setLoading] = useState<"aprobar" | "rechazar" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function ejecutar(accion: "aprobar" | "rechazar") {
    const confirmMsg =
      accion === "aprobar"
        ? "Aprobar a " + nombre + "? Podrá acceder al catálogo de inmediato."
        : "Rechazar a " + nombre + "? No podrá ingresar al portal.";

    if (!confirm(confirmMsg)) return;

    setLoading(accion);
    setError(null);

    try {
      const res = await fetch("/api/admin/comerciantes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, accion }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error ?? "Error al procesar la acción");
      }

      startTransition(() => {
        router.refresh();
      });
    } catch (e: any) {
      setError(e.message ?? "Error inesperado");
    } finally {
      setLoading(null);
    }
  }

  const disabled = isPending || loading !== null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <div style={{ display: "flex", gap: "7px" }}>
        <button
          onClick={() => ejecutar("aprobar")}
          disabled={disabled}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "5px",
            padding: "7px 13px",
            borderRadius: "7px",
            border: "1px solid var(--ok)",
            background: "var(--ok-t)",
            color: "var(--ok)",
            fontWeight: 700,
            fontSize: "12.5px",
            cursor: disabled ? "not-allowed" : "pointer",
            opacity: disabled && loading !== "aprobar" ? 0.5 : 1,
            transition: "background .15s, opacity .15s",
            fontFamily: "inherit",
          }}
        >
          {loading === "aprobar" ? <SpinIcon /> : <CheckIcon />}
          Aprobar
        </button>

        <button
          onClick={() => ejecutar("rechazar")}
          disabled={disabled}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "5px",
            padding: "7px 13px",
            borderRadius: "7px",
            border: "1px solid var(--out)",
            background: "var(--out-t)",
            color: "var(--out)",
            fontWeight: 700,
            fontSize: "12.5px",
            cursor: disabled ? "not-allowed" : "pointer",
            opacity: disabled && loading !== "rechazar" ? 0.5 : 1,
            transition: "background .15s, opacity .15s",
            fontFamily: "inherit",
          }}
        >
          {loading === "rechazar" ? <SpinIcon /> : <XIcon />}
          Rechazar
        </button>
      </div>
      {error && (
        <span style={{ fontSize: "11.5px", color: "var(--out)", fontWeight: 600 }}>
          {error}
        </span>
      )}
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 13l4 4L19 7" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  );
}

function SpinIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round"
      style={{ animation: "spin 0.8s linear infinite" }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
    </svg>
  );
}