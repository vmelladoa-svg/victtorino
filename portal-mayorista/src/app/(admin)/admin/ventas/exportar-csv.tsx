"use client";

interface FilaCsv {
  folio: string;
  fecha: string;
  comerciante: string;
  email: string;
  estado: string;
  total: number;
}

interface Props {
  filas: FilaCsv[];
}

function fmtClpRaw(n: number) {
  return n.toLocaleString("es-CL");
}

export default function ExportarCsvBtn({ filas }: Props) {
  function descargar() {
    const cabecera = ["Folio", "Fecha", "Comerciante", "Email", "Estado", "Total (CLP)"];

    const filasCsv = filas.map((f) => [
      f.folio,
      f.fecha,
      `"${f.comerciante.replace(/"/g, '""')}"`,
      f.email,
      f.estado,
      fmtClpRaw(f.total),
    ]);

    const contenido = [cabecera, ...filasCsv]
      .map((row) => row.join(","))
      .join("\r\n");

    // BOM UTF-8 para que Excel abra con tildes
    const bom = "﻿";
    const blob = new Blob([bom + contenido], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const hoy = new Date().toISOString().slice(0, 10);
    a.download = `ventas-trade-${hoy}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <button
      onClick={descargar}
      disabled={filas.length === 0}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "7px",
        padding: "9px 16px",
        background: "var(--surface)",
        color: "var(--ink-2)",
        border: "1px solid var(--line)",
        borderRadius: "var(--rs)",
        fontWeight: 700,
        fontSize: "13.5px",
        cursor: filas.length === 0 ? "not-allowed" : "pointer",
        opacity: filas.length === 0 ? 0.5 : 1,
        fontFamily: "var(--font)",
      }}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="15" x2="12" y2="3" />
      </svg>
      Exportar CSV
      {filas.length > 0 && (
        <span style={{ fontSize: "11px", fontWeight: 800, background: "var(--brand-soft)", color: "var(--brand-ink)", padding: "1px 7px", borderRadius: "100px" }}>
          {filas.length}
        </span>
      )}
    </button>
  );
}
