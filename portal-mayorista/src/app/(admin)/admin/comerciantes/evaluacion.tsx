"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import {
  scoreFinal as calcScoreFinal,
  tierEfectivo,
  tierDeScore,
  type Tier,
} from "@/lib/evaluacion";

interface Props {
  id: string;
  scoreAuto: number;
  componentes: { total: number; pago: number; frecuencia: number; antiguedad: number };
  scoreAjuste: number;
  tierManual: string | null;
  notaEval: string | null;
}

const TIER_COLOR: Record<Tier, string> = { A: "#1f9d57", B: "#c98a12", C: "#c4423f" };

export default function EvaluacionComerciante({
  id,
  scoreAuto,
  componentes,
  scoreAjuste,
  tierManual,
  notaEval,
}: Props) {
  const router = useRouter();
  const [abierto, setAbierto] = useState(false);
  const [ajuste, setAjuste] = useState(String(scoreAjuste));
  const [tier, setTier] = useState<string>(tierManual ?? "");
  const [nota, setNota] = useState(notaEval ?? "");
  const [guardando, setGuardando] = useState(false);
  const [ok, setOk] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const ajusteNum = Math.max(-100, Math.min(100, Math.round(Number(ajuste) || 0)));
  const finalPreview = calcScoreFinal(scoreAuto, ajusteNum);
  const tierPreview = tierEfectivo(finalPreview, tier || null);
  const tierAuto = tierDeScore(finalPreview);

  async function guardar() {
    setGuardando(true);
    setError(null);
    setOk(false);
    try {
      const res = await fetch("/api/admin/comerciantes/evaluar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, scoreAjuste: ajusteNum, tierManual: tier || null, notaEval: nota }),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.error ?? "Error al guardar la evaluación");
      }
      setOk(true);
      startTransition(() => router.refresh());
    } catch (e: any) {
      setError(e.message ?? "Error inesperado");
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div style={{ marginTop: "10px" }}>
      <button
        onClick={() => setAbierto((v) => !v)}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          padding: "5px 10px",
          borderRadius: "6px",
          border: "1px solid var(--line-2)",
          background: "transparent",
          color: "var(--ink-2)",
          fontWeight: 700,
          fontSize: "12px",
          cursor: "pointer",
          fontFamily: "inherit",
        }}
      >
        {abierto ? "▾" : "▸"} Evaluar cliente
      </button>

      {abierto && (
        <div
          style={{
            marginTop: "10px",
            padding: "14px",
            border: "1px solid var(--line-2)",
            borderRadius: "9px",
            background: "var(--bg-soft, #f7fafc)",
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            maxWidth: "520px",
          }}
        >
          {/* Desglose del score automático */}
          <div>
            <div style={{ fontSize: "11.5px", fontWeight: 700, color: "var(--ink-3)", marginBottom: "6px" }}>
              Score automático: <strong style={{ color: "var(--ink-1)" }}>{scoreAuto}/100</strong>
            </div>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              <Comp label="Total comprado" v={componentes.total} />
              <Comp label="Pago" v={componentes.pago} />
              <Comp label="Frecuencia" v={componentes.frecuencia} />
              <Comp label="Antigüedad" v={componentes.antiguedad} />
            </div>
          </div>

          {/* Ajuste manual + tier */}
          <div style={{ display: "flex", gap: "14px", flexWrap: "wrap", alignItems: "flex-end" }}>
            <label style={{ display: "flex", flexDirection: "column", gap: "4px", fontSize: "11.5px", fontWeight: 700, color: "var(--ink-3)" }}>
              Ajuste manual (-100 a 100)
              <input
                type="number"
                min={-100}
                max={100}
                value={ajuste}
                onChange={(e) => setAjuste(e.target.value)}
                style={{ width: "110px", padding: "7px 9px", border: "1px solid var(--line-2)", borderRadius: "6px", fontSize: "13px", fontFamily: "inherit" }}
              />
            </label>

            <label style={{ display: "flex", flexDirection: "column", gap: "4px", fontSize: "11.5px", fontWeight: 700, color: "var(--ink-3)" }}>
              Tier
              <select
                value={tier}
                onChange={(e) => setTier(e.target.value)}
                style={{ width: "150px", padding: "7px 9px", border: "1px solid var(--line-2)", borderRadius: "6px", fontSize: "13px", fontFamily: "inherit" }}
              >
                <option value="">Automático ({tierAuto})</option>
                <option value="A">A (fijar)</option>
                <option value="B">B (fijar)</option>
                <option value="C">C (fijar)</option>
              </select>
            </label>

            <div style={{ fontSize: "12px", color: "var(--ink-2)", fontWeight: 700 }}>
              Final:{" "}
              <span style={{ color: "var(--ink-1)" }}>{finalPreview}/100</span>{" "}
              <span
                style={{
                  display: "inline-block",
                  padding: "2px 8px",
                  borderRadius: "100px",
                  background: TIER_COLOR[tierPreview] + "22",
                  color: TIER_COLOR[tierPreview],
                  fontWeight: 800,
                  marginLeft: "4px",
                }}
              >
                Tier {tierPreview}
              </span>
            </div>
          </div>

          {/* Notas */}
          <label style={{ display: "flex", flexDirection: "column", gap: "4px", fontSize: "11.5px", fontWeight: 700, color: "var(--ink-3)" }}>
            Notas de evaluación
            <textarea
              value={nota}
              onChange={(e) => setNota(e.target.value)}
              rows={2}
              maxLength={500}
              placeholder="Ej: RUT verificado en SII, negocio con local físico, referencia comercial ok."
              style={{ padding: "8px 10px", border: "1px solid var(--line-2)", borderRadius: "6px", fontSize: "13px", fontFamily: "inherit", resize: "vertical" }}
            />
          </label>

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <button
              onClick={guardar}
              disabled={guardando || isPending}
              style={{
                padding: "8px 16px",
                borderRadius: "7px",
                border: "1px solid var(--brand)",
                background: "var(--brand)",
                color: "#fff",
                fontWeight: 700,
                fontSize: "12.5px",
                cursor: guardando ? "not-allowed" : "pointer",
                opacity: guardando ? 0.6 : 1,
                fontFamily: "inherit",
              }}
            >
              {guardando ? "Guardando..." : "Guardar evaluación"}
            </button>
            {ok && <span style={{ fontSize: "12px", color: "#1f9d57", fontWeight: 700 }}>✓ Guardado</span>}
            {error && <span style={{ fontSize: "12px", color: "#c4423f", fontWeight: 700 }}>{error}</span>}
          </div>
        </div>
      )}
    </div>
  );
}

function Comp({ label, v }: { label: string; v: number }) {
  return (
    <span
      style={{
        fontSize: "11px",
        fontWeight: 600,
        color: "var(--ink-2)",
        background: "var(--line-2)",
        padding: "3px 8px",
        borderRadius: "100px",
      }}
    >
      {label}: {v}
    </span>
  );
}
