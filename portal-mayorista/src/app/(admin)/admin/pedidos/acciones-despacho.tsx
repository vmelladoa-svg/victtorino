"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

interface Props {
  pedidoId: string;
  folio: string;
  empresa: string;
  estado: "oc_generada" | "despachado";
  transportistaActual?: string | null;
  trackingActual?: string | null;
}

export default function AccionesDespacho({
  pedidoId,
  folio,
  empresa,
  estado,
  transportistaActual,
  trackingActual,
}: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<"despachado" | "entregado" | null>(null);

  // Formulario de despacho
  const [transportista, setTransportista] = useState(transportistaActual ?? "");
  const [tracking, setTracking] = useState(trackingActual ?? "");

  const disabled = isPending || loading;

  async function despachar() {
    if (!transportista.trim()) {
      setError("Ingresa el nombre del transportista.");
      return;
    }
    if (!tracking.trim()) {
      setError("Ingresa el número de seguimiento (tracking).");
      return;
    }
    if (
      !confirm(
        `¿Despachar el pedido ${folio} de ${empresa}?\n\nTransportista: ${transportista}\nTracking: ${tracking}`
      )
    )
      return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/admin/pedidos/estado", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: pedidoId, a: "despachado", transportista, tracking }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.error ?? "Error al despachar el pedido");
      }

      setExito("despachado");
      startTransition(() => {
        router.refresh();
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  }

  async function marcarEntregado() {
    if (
      !confirm(`¿Marcar como entregado el pedido ${folio} de ${empresa}?\n\nEsta acción es definitiva.`)
    )
      return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/admin/pedidos/estado", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: pedidoId, a: "entregado" }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.error ?? "Error al marcar como entregado");
      }

      setExito("entregado");
      startTransition(() => {
        router.refresh();
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  }

  if (exito === "despachado") {
    return (
      <div style={bannerStyle("var(--brand)")}>
        <CheckIcon />
        <strong style={{ fontSize: "13px", color: "var(--brand)" }}>
          Pedido despachado correctamente.
        </strong>
      </div>
    );
  }

  if (exito === "entregado") {
    return (
      <div style={bannerStyle("var(--ok, #16a34a)")}>
        <CheckIcon color="var(--ok, #16a34a)" />
        <strong style={{ fontSize: "13px", color: "var(--ok, #16a34a)" }}>
          Pedido marcado como entregado.
        </strong>
      </div>
    );
  }

  if (estado === "oc_generada") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        <p style={{
          fontSize: "11px",
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: ".06em",
          color: "var(--ink-3)",
          margin: 0,
        }}>
          Registrar despacho
        </p>

        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {/* Campo transportista */}
          <div style={{ display: "flex", flexDirection: "column", gap: "4px", flex: "1 1 180px" }}>
            <label style={{ fontSize: "11.5px", fontWeight: 600, color: "var(--ink-2)" }}>
              Transportista
            </label>
            <input
              type="text"
              value={transportista}
              onChange={(e) => setTransportista(e.target.value)}
              placeholder="Ej: Starken, Chilexpress…"
              disabled={disabled}
              style={inputStyle(disabled)}
            />
          </div>

          {/* Campo tracking */}
          <div style={{ display: "flex", flexDirection: "column", gap: "4px", flex: "1 1 200px" }}>
            <label style={{ fontSize: "11.5px", fontWeight: 600, color: "var(--ink-2)" }}>
              Número de seguimiento
            </label>
            <input
              type="text"
              value={tracking}
              onChange={(e) => setTracking(e.target.value)}
              placeholder="Ej: 1234-5678-9012"
              disabled={disabled}
              style={inputStyle(disabled)}
            />
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <button
            onClick={despachar}
            disabled={disabled}
            style={btnStyle(disabled, "var(--brand)")}
          >
            {loading ? <SpinIcon /> : <TruckSmallIcon />}
            Despachar
          </button>

          {error && (
            <span style={{ fontSize: "11.5px", color: "var(--out)", fontWeight: 600 }}>
              {error}
            </span>
          )}
        </div>
      </div>
    );
  }

  // estado === "despachado"
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {(transportistaActual || trackingActual) && (
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "8px 12px",
          borderRadius: "8px",
          background: "var(--surface-2)",
          border: "1px solid var(--line-2)",
          fontSize: "12.5px",
          flexWrap: "wrap",
        }}>
          <TruckSmallIcon />
          {transportistaActual && (
            <span style={{ color: "var(--ink)", fontWeight: 600 }}>{transportistaActual}</span>
          )}
          {trackingActual && (
            <span style={{ fontFamily: "var(--mono)", color: "var(--brand)", fontWeight: 700 }}>
              {trackingActual}
            </span>
          )}
        </div>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <button
          onClick={marcarEntregado}
          disabled={disabled}
          style={btnStyle(disabled, "var(--ok, #16a34a)")}
        >
          {loading ? <SpinIcon /> : <CheckIcon />}
          Marcar entregado
        </button>

        {error && (
          <span style={{ fontSize: "11.5px", color: "var(--out)", fontWeight: 600 }}>
            {error}
          </span>
        )}
      </div>
    </div>
  );
}

/* ── helpers de estilo ── */

function inputStyle(disabled: boolean): React.CSSProperties {
  return {
    padding: "7px 11px",
    borderRadius: "7px",
    border: "1px solid var(--line-2)",
    fontSize: "13px",
    fontFamily: "inherit",
    background: disabled ? "var(--surface-2)" : "var(--surface)",
    color: "var(--ink)",
    outline: "none",
    width: "100%",
    boxSizing: "border-box" as const,
    opacity: disabled ? 0.6 : 1,
  };
}

function btnStyle(disabled: boolean, bg: string): React.CSSProperties {
  return {
    display: "inline-flex",
    alignItems: "center",
    gap: "7px",
    padding: "9px 18px",
    borderRadius: "8px",
    border: "none",
    background: disabled ? "var(--ink-3)" : bg,
    color: "#fff",
    fontWeight: 700,
    fontSize: "13px",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.6 : 1,
    fontFamily: "inherit",
    transition: "background .15s, opacity .15s",
  };
}

function bannerStyle(color: string): React.CSSProperties {
  return {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginTop: "8px",
    padding: "10px 14px",
    borderRadius: "8px",
    border: `1.5px solid ${color}`,
    background: color === "var(--brand)" ? "var(--brand-t, #e8f4fd)" : "#f0fdf4",
  };
}

/* ── íconos ── */

function TruckSmallIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="3" width="15" height="13" />
      <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
      <circle cx="5.5" cy="18.5" r="2.5" />
      <circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  );
}

function CheckIcon({ color }: { color?: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke={color ?? "currentColor"} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
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
