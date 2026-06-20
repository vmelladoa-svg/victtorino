"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

interface LineaOc {
  codigoAlila: string;
  nombre: string;
  cantidad: number;
  link1688: string | null;
}

interface OcGenerada {
  numeroOc: string;
  lineasOc: LineaOc[];
}

interface Props {
  pedidoId: string;
  folio: string;
  empresa: string;
}

export default function AccionesGenerarOc({ pedidoId, folio, empresa }: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [oc, setOc] = useState<OcGenerada | null>(null);

  const disabled = isPending || loading;

  async function generarOc() {
    if (!confirm(`¿Generar OC para el pedido ${folio} de ${empresa}?\n\nSe creará la orden de compra a AlilaTop y se descontará el stock reservado.`))
      return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/admin/oc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pedidoId }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.error ?? "Error al generar la OC");
      }

      setOc({ numeroOc: data.numeroOc, lineasOc: data.lineasOc ?? [] });

      startTransition(() => {
        router.refresh();
      });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error inesperado";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  if (oc) {
    return (
      <div style={{
        marginTop: "12px",
        padding: "14px 16px",
        borderRadius: "10px",
        border: "1.5px solid var(--brand)",
        background: "var(--brand-t, #e8f4fd)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
          <CheckCircleIcon />
          <strong style={{ fontSize: "13.5px", color: "var(--brand)" }}>
            OC generada: <span style={{ fontFamily: "var(--mono)" }}>{oc.numeroOc}</span>
          </strong>
        </div>
        <p style={{ fontSize: "12px", color: "var(--ink-2)", margin: "0 0 8px" }}>
          Detalle para comprar en AlilaTop:
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {oc.lineasOc.map((l, i) => (
            <div key={i} style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "7px 10px",
              background: "white",
              borderRadius: "7px",
              border: "1px solid var(--line-2)",
              fontSize: "12.5px",
            }}>
              <span style={{ fontFamily: "var(--mono)", fontWeight: 700, color: "var(--ink)", minWidth: "80px" }}>
                {l.codigoAlila ?? "—"}
              </span>
              <span style={{ flex: 1, color: "var(--ink-2)" }}>{l.nombre}</span>
              <span style={{ fontFamily: "var(--mono)", fontWeight: 700, color: "var(--ink)" }}>
                ×{l.cantidad}
              </span>
              {l.link1688 && (
                <a
                  href={l.link1688}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: "11px",
                    color: "var(--brand)",
                    fontWeight: 600,
                    textDecoration: "none",
                    padding: "2px 7px",
                    borderRadius: "5px",
                    border: "1px solid var(--brand)",
                    whiteSpace: "nowrap",
                  }}
                >
                  Ver en 1688
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <button
        onClick={generarOc}
        disabled={disabled}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "7px",
          padding: "9px 18px",
          borderRadius: "8px",
          border: "none",
          background: disabled ? "var(--ink-3)" : "var(--brand)",
          color: "#fff",
          fontWeight: 700,
          fontSize: "13px",
          cursor: disabled ? "not-allowed" : "pointer",
          opacity: disabled ? 0.6 : 1,
          fontFamily: "inherit",
          transition: "background .15s, opacity .15s",
        }}
      >
        {loading ? <SpinIcon /> : <PackageIcon />}
        Generar OC a AlilaTop
      </button>
      {error && (
        <span style={{
          fontSize: "11.5px",
          color: "var(--out)",
          fontWeight: 600,
          lineHeight: 1.4,
        }}>
          {error}
        </span>
      )}
    </div>
  );
}

function PackageIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l10 6.5v7L12 22 2 15.5v-7L12 2z" />
      <path d="M12 22V12" />
      <path d="M2 8.5l10 3.5 10-3.5" />
      <path d="M7 5.5l5 2 5-2" />
    </svg>
  );
}

function CheckCircleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
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
