"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

interface Props {
  pedidoId: string;
  folio: string;
  empresa: string;
}

export default function AccionesPago({ pedidoId, folio, empresa }: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [loading, setLoading] = useState<"validar" | "rechazar" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function ejecutar(tipoAccion: "validar" | "rechazar") {
    const estadoDestino = tipoAccion === "validar" ? "validado" : "rechazado";
    const msg =
      tipoAccion === "validar"
        ? "Validar el pago del pedido " + folio + " de " + empresa + "? Se reservara stock de inmediato."
        : "Rechazar el pago del pedido " + folio + " de " + empresa + "? El comerciante debera reiniciar el proceso.";

    if (!confirm(msg)) return;

    setLoading(tipoAccion);
    setError(null);

    try {
      const res = await fetch("/api/admin/pedidos/estado", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: pedidoId, a: estadoDestino }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        if (res.status === 409 && data.detalle) {
          const detalle = (data.detalle as Array<{ nombre: string; disponible: number; solicitado: number }>)
            .map((d: { nombre: string; disponible: number; solicitado: number }) => d.nombre + ": disponible " + d.disponible + ", solicitado " + d.solicitado)
            .join("\n");
          throw new Error("Stock insuficiente:\n" + detalle);
        }
        throw new Error(data.error ?? "Error al procesar la accion");
      }

      startTransition(() => {
        router.refresh();
      });
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : "Error inesperado";
      setError(errMsg);
    } finally {
      setLoading(null);
    }
  }

  const disabled = isPending || loading !== null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <div className="pago-actions">
        <button
          onClick={() => ejecutar("rechazar")}
          disabled={disabled}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            padding: "9px 16px",
            borderRadius: "8px",
            border: "1px solid var(--out)",
            background: "var(--out-t)",
            color: "var(--out)",
            fontWeight: 700,
            fontSize: "13px",
            cursor: disabled ? "not-allowed" : "pointer",
            opacity: disabled && loading !== "rechazar" ? 0.5 : 1,
            fontFamily: "inherit",
            transition: "background .15s, opacity .15s",
          }}
        >
          {loading === "rechazar" ? <SpinIcon /> : <XIcon />}
          Rechazar
        </button>

        <button
          onClick={() => ejecutar("validar")}
          disabled={disabled}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            padding: "9px 16px",
            borderRadius: "8px",
            border: "none",
            background: "var(--brand)",
            color: "#fff",
            fontWeight: 700,
            fontSize: "13px",
            cursor: disabled ? "not-allowed" : "pointer",
            opacity: disabled && loading !== "validar" ? 0.5 : 1,
            fontFamily: "inherit",
            transition: "background .15s, opacity .15s",
          }}
        >
          {loading === "validar" ? <SpinIcon /> : <CheckIcon />}
          Validar pago
        </button>
      </div>
      {error && (
        <span
          style={{
            fontSize: "11.5px",
            color: "var(--out)",
            fontWeight: 600,
            whiteSpace: "pre-line",
            lineHeight: 1.4,
          }}
        >
          {error}
        </span>
      )}
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 13l4 4L19 7" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  );
}

function SpinIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round"
      style={{ animation: "spin 0.8s linear infinite" }}>
      <style>{"@keyframes spin { to { transform: rotate(360deg); } }"}</style>
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
    </svg>
  );
}
