"use client";

import { useState, useRef, useMemo } from "react";
import { useCart } from "@/lib/cart-context";
import { precioPorCantidad } from "@/lib/precios";
import Link from "next/link";
import { useRouter } from "next/navigation";

/* ── Regiones de Chile ── */
const REGIONES = [
  "Región Metropolitana",
  "Valparaíso",
  "O'Higgins",
  "Maule",
  "Biobío",
  "Araucanía",
  "Los Ríos",
  "Los Lagos",
  "Aysén",
  "Magallanes",
  "Atacama",
  "Coquimbo",
  "Tarapacá",
  "Antofagasta",
  "Arica y Parinacota",
  "Ñuble",
];

/* ── Datos bancarios VERBATIM ── */
const BANCO = {
  banco: "Banco Scotiabank",
  tipo: "Cuenta Corriente",
  numero: "000993556831",
  titular: "Trade Global Solutions SpA",
  rut: "78.103.712-5",
  email: "victor.mellado@comercialsolutions.cl",
};

/* ── helpers ── */
function clp(n: number): string {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(n);
}

/* ── icons ── */
function ChevLeftIcon() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  );
}
function CheckIcon({ size = 15 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
function TruckIcon() {
  return (
    <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="3" width="15" height="13" /><path d="M16 8h4l3 5v4h-7z" />
      <circle cx="5.5" cy="18.5" r="2.5" /><circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  );
}
function DocIcon() {
  return (
    <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
    </svg>
  );
}
function UploadIcon() {
  return (
    <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="16 16 12 12 8 16" /><line x1="12" y1="12" x2="12" y2="21" />
      <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
    </svg>
  );
}
function ShieldIcon() {
  return (
    <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}
function GridIcon() {
  return (
    <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
    </svg>
  );
}

/* ── Steps ── */
function Steps({ step }: { step: number }) {
  const pasos = [
    { n: 1, label: "Despacho" },
    { n: 2, label: "Pago" },
    { n: 3, label: "Listo" },
  ];
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0, marginBottom: 30 }}>
      {pasos.map((p, i) => (
        <div key={p.n} style={{ display: "flex", alignItems: "center" }}>
          <div style={{
            display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
          }}>
            <div style={{
              width: 34, height: 34, borderRadius: "50%", display: "grid", placeItems: "center",
              background: step > p.n ? "var(--ok)" : step === p.n ? "var(--brand)" : "var(--line)",
              color: step >= p.n ? "#fff" : "var(--ink-3)",
              fontWeight: 700, fontSize: 14,
              transition: "all .2s",
            }}>
              {step > p.n ? <CheckIcon size={15} /> : p.n}
            </div>
            <span style={{ fontSize: 12, fontWeight: 600, color: step >= p.n ? "var(--ink)" : "var(--ink-3)" }}>
              {p.label}
            </span>
          </div>
          {i < pasos.length - 1 && (
            <div style={{ width: 80, height: 2, background: step > p.n ? "var(--ok)" : "var(--line)", margin: "0 8px", marginBottom: 20, transition: "background .2s" }} />
          )}
        </div>
      ))}
    </div>
  );
}

export default function CheckoutPage() {
  const { items, total, clearCart } = useCart();
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [region, setRegion] = useState("Región Metropolitana");
  const [direccion, setDireccion] = useState("");
  const [archivo, setArchivo] = useState<File | null>(null);
  const [comprobanteUrl, setComprobanteUrl] = useState<string | null>(null);
  const [subiendo, setSubiendo] = useState(false);
  const [errorSubida, setErrorSubida] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [errorPedido, setErrorPedido] = useState<string | null>(null);
  const [pedidoId, setPedidoId] = useState<string | null>(null);
  const [copiado, setCopiado] = useState<string>("");
  const fileRef = useRef<HTMLInputElement>(null);

  const folio = useMemo(() => "TGS-" + Math.floor(100000 + Math.random() * 899999), []);

  // Si el carrito está vacío y no hay pedido confirmado, redirigir
  if (items.length === 0 && step < 3 && !pedidoId) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--bg)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16, padding: 32 }}>
        <p style={{ color: "var(--ink-2)", fontSize: 15 }}>Tu carrito está vacío.</p>
        <Link href="/catalogo" style={{ color: "var(--brand)", fontWeight: 700, textDecoration: "none" }}>Ir al catálogo</Link>
      </div>
    );
  }

  function copy(txt: string, key: string) {
    navigator.clipboard?.writeText(txt).catch(() => {});
    setCopiado(key);
    setTimeout(() => setCopiado(""), 1400);
  }

  async function handleSubirArchivo(file: File) {
    setSubiendo(true);
    setErrorSubida(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch("/api/comprobante", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) { setErrorSubida(data.error || "Error al subir"); return; }
      setComprobanteUrl(data.url);
    } catch (e: any) {
      setErrorSubida(e.message || "Error de red");
    } finally {
      setSubiendo(false);
    }
  }

  async function handleConfirmar() {
    if (!comprobanteUrl) return;
    setEnviando(true);
    setErrorPedido(null);
    try {
      const body = {
        region,
        direccion,
        comprobanteUrl,
        items: items.map((i) => ({ productoId: i.productoId, cantidad: i.cantidad })),
      };
      const res = await fetch("/api/pedidos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) { setErrorPedido(data.error || "Error al crear pedido"); return; }
      setPedidoId(data.pedidoId);
      clearCart();
      setStep(3);
    } catch (e: any) {
      setErrorPedido(e.message || "Error de red");
    } finally {
      setEnviando(false);
    }
  }

  /* ── resumen sidebar ── */
  const resumenTotal = items.reduce((acc, i) => {
    try { return acc + precioPorCantidad(i, i.cantidad) * i.cantidad; } catch { return acc; }
  }, 0);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", fontFamily: "var(--font)" }}>
      {/* Header */}
      <header style={{ position: "sticky", top: 0, zIndex: 40, background: "rgba(255,255,255,0.96)", backdropFilter: "blur(10px)", borderBottom: "1px solid var(--line)" }}>
        <div style={{ maxWidth: 1240, margin: "0 auto", padding: "13px 26px", display: "flex", alignItems: "center", gap: 16 }}>
          {step < 3 && (
            <button
              onClick={() => step === 1 ? router.push("/carrito") : setStep(step - 1)}
              style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "none", border: "none", fontSize: 13, fontWeight: 600, color: "var(--ink-2)", cursor: "pointer", padding: 0 }}
            >
              <ChevLeftIcon /> {step === 1 ? "Volver al carrito" : "Atrás"}
            </button>
          )}
          <div style={{ flex: 1 }} />
          <h1 style={{ fontSize: 18, fontWeight: 800, color: "var(--ink)" }}>Finalizar pedido</h1>
        </div>
      </header>

      <main style={{ maxWidth: 1100, margin: "0 auto", padding: "30px 26px 60px" }}>
        <Steps step={step} />

        <div style={{ display: "grid", gridTemplateColumns: step < 3 ? "1fr 300px" : "1fr", gap: 28, alignItems: "start" }}>

          {/* ── Paso 1: Despacho ── */}
          {step === 1 && (
            <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--radius)", padding: "28px 28px" }}>
              <h3 style={{ fontSize: 17, fontWeight: 800, marginBottom: 20, display: "flex", alignItems: "center", gap: 9, color: "var(--ink)" }}>
                <TruckIcon /> Datos de despacho
              </h3>

              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-2)" }}>Región de destino</span>
                  <select
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                    style={{ padding: "10px 12px", border: "1px solid var(--line)", borderRadius: "var(--rs)", fontSize: 14, background: "var(--surface)", color: "var(--ink)", outline: "none" }}
                  >
                    {REGIONES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </label>

                <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-2)" }}>Dirección de entrega</span>
                  <input
                    type="text"
                    value={direccion}
                    onChange={(e) => setDireccion(e.target.value)}
                    placeholder="Ej: Av. Matta 1234, bodega 5, Santiago"
                    style={{ padding: "10px 12px", border: "1px solid var(--line)", borderRadius: "var(--rs)", fontSize: 14, color: "var(--ink)", outline: "none" }}
                  />
                </label>

                <button
                  onClick={() => setStep(2)}
                  disabled={!direccion.trim()}
                  style={{
                    marginTop: 6, padding: "13px 0", width: "100%",
                    background: direccion.trim() ? "var(--brand)" : "var(--line)",
                    color: direccion.trim() ? "#fff" : "var(--ink-3)",
                    border: "none", borderRadius: "var(--rs)", fontSize: 15, fontWeight: 700,
                    cursor: direccion.trim() ? "pointer" : "not-allowed",
                    display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                  }}
                >
                  Continuar al pago
                </button>
              </div>
            </div>
          )}

          {/* ── Paso 2: Pago ── */}
          {step === 2 && (
            <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--radius)", padding: "28px 28px" }}>
              <h3 style={{ fontSize: 17, fontWeight: 800, marginBottom: 8, display: "flex", alignItems: "center", gap: 9, color: "var(--ink)" }}>
                <DocIcon /> Pago por transferencia
              </h3>
              <p style={{ fontSize: 13.5, color: "var(--ink-2)", marginBottom: 20, lineHeight: 1.5 }}>
                Transfiere el total y envía el comprobante. Validamos en 24–48h hábiles y coordinamos el despacho.
              </p>

              {/* Datos bancarios */}
              <div style={{ border: "1px solid var(--line)", borderRadius: "var(--rs)", overflow: "hidden", marginBottom: 20 }}>
                {[
                  ["Titular", BANCO.titular, false],
                  ["RUT", BANCO.rut, true],
                  ["Banco", BANCO.banco, false],
                  ["Tipo de cuenta", BANCO.tipo, false],
                  ["N° de cuenta", BANCO.numero, true],
                  ["Correo de comprobantes", BANCO.email, false],
                ].map(([k, v, mono]) => (
                  <div
                    key={k as string}
                    style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "11px 16px", borderBottom: "1px solid var(--line)", gap: 12 }}
                  >
                    <span style={{ fontSize: 12.5, color: "var(--ink-2)", flex: "0 0 140px" }}>{k as string}</span>
                    <strong style={{ fontSize: 13.5, color: "var(--ink)", flex: 1, fontFamily: mono ? "var(--mono)" : "inherit" }}>{v as string}</strong>
                    <button
                      onClick={() => copy(v as string, k as string)}
                      style={{ padding: "5px 10px", background: copiado === k ? "var(--ok-t)" : "var(--bg)", border: "1px solid var(--line)", borderRadius: "var(--rs)", fontSize: 12, fontWeight: 600, color: copiado === k ? "var(--ok)" : "var(--ink-2)", cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4, whiteSpace: "nowrap" }}
                    >
                      {copiado === k ? <><CheckIcon size={12} /> Copiado</> : "Copiar"}
                    </button>
                  </div>
                ))}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", background: "var(--brand-tint)", gap: 12 }}>
                  <span style={{ fontSize: 13, fontWeight: 700, color: "var(--brand-deep)" }}>Monto exacto a transferir</span>
                  <strong className="mono" style={{ fontSize: 18, color: "var(--brand-deep)", flex: 1, textAlign: "right" }}>{clp(resumenTotal)}</strong>
                  <button
                    onClick={() => copy(String(resumenTotal), "monto")}
                    style={{ padding: "5px 10px", background: copiado === "monto" ? "var(--ok-t)" : "var(--surface)", border: "1px solid var(--brand-line)", borderRadius: "var(--rs)", fontSize: 12, fontWeight: 600, color: copiado === "monto" ? "var(--ok)" : "var(--brand-deep)", cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4, whiteSpace: "nowrap" }}
                  >
                    {copiado === "monto" ? <><CheckIcon size={12} /> Copiado</> : "Copiar"}
                  </button>
                </div>
              </div>

              <p style={{ fontSize: 12, color: "var(--ink-3)", marginBottom: 14 }}>
                Indica el folio <strong className="mono">{folio}</strong> en el detalle de la transferencia.
              </p>

              {/* Subida comprobante */}
              <div
                onClick={() => !subiendo && fileRef.current?.click()}
                style={{
                  border: `2px dashed ${comprobanteUrl ? "var(--ok)" : "var(--line)"}`,
                  borderRadius: "var(--rs)",
                  padding: "22px 18px",
                  cursor: subiendo ? "wait" : "pointer",
                  textAlign: "center",
                  background: comprobanteUrl ? "var(--ok-t)" : "var(--bg)",
                  marginBottom: 18,
                  transition: "all .2s",
                }}
              >
                <input
                  ref={fileRef}
                  type="file"
                  hidden
                  accept="image/jpeg,image/png,image/webp,application/pdf"
                  onChange={async (e) => {
                    const f = e.target.files?.[0];
                    if (!f) return;
                    setArchivo(f);
                    await handleSubirArchivo(f);
                  }}
                />
                {comprobanteUrl ? (
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10, color: "var(--ok)" }}>
                    <CheckIcon size={20} />
                    <div style={{ textAlign: "left" }}>
                      <div style={{ fontWeight: 700, fontSize: 14 }}>{archivo?.name}</div>
                      <div style={{ fontSize: 12, color: "var(--ok)", opacity: 0.8 }}>Comprobante listo para enviar</div>
                    </div>
                  </div>
                ) : subiendo ? (
                  <div style={{ color: "var(--ink-2)", fontSize: 14 }}>Subiendo comprobante…</div>
                ) : (
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12, color: "var(--ink-3)" }}>
                    <UploadIcon />
                    <div style={{ textAlign: "left" }}>
                      <div style={{ fontWeight: 700, fontSize: 14, color: "var(--ink)" }}>Adjunta tu comprobante</div>
                      <div style={{ fontSize: 12 }}>JPG, PNG, WebP o PDF · máx 8MB</div>
                    </div>
                  </div>
                )}
              </div>

              {errorSubida && (
                <p style={{ fontSize: 13, color: "var(--out)", marginBottom: 12 }}>{errorSubida}</p>
              )}

              {errorPedido && (
                <p style={{ fontSize: 13, color: "var(--out)", marginBottom: 12 }}>{errorPedido}</p>
              )}

              <button
                onClick={handleConfirmar}
                disabled={!comprobanteUrl || enviando}
                style={{
                  width: "100%", padding: "13px 0",
                  background: comprobanteUrl && !enviando ? "var(--brand)" : "var(--line)",
                  color: comprobanteUrl && !enviando ? "#fff" : "var(--ink-3)",
                  border: "none", borderRadius: "var(--rs)", fontSize: 15, fontWeight: 700,
                  cursor: comprobanteUrl && !enviando ? "pointer" : "not-allowed",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                }}
              >
                <CheckIcon size={16} />
                {enviando ? "Enviando pedido…" : "Ya transferí · enviar comprobante"}
              </button>

              {!comprobanteUrl && !subiendo && (
                <p style={{ textAlign: "center", fontSize: 12, color: "var(--ink-3)", marginTop: 8 }}>
                  Adjunta el comprobante para continuar.
                </p>
              )}
            </div>
          )}

          {/* ── Paso 3: Confirmación ── */}
          {step === 3 && (
            <div style={{ maxWidth: 540, margin: "0 auto", background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--radius)", padding: "40px 36px", textAlign: "center" }}>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: "var(--ok-t)", display: "grid", placeItems: "center", margin: "0 auto 20px", color: "var(--ok)" }}>
                <CheckIcon size={28} />
              </div>
              <h2 style={{ fontSize: 24, fontWeight: 800, marginBottom: 12, color: "var(--ink)" }}>¡Pedido recibido!</h2>
              <p style={{ fontSize: 14.5, color: "var(--ink-2)", lineHeight: 1.6, marginBottom: 28 }}>
                Tu pedido <strong className="mono">{folio}</strong> quedó en{" "}
                <strong>validación de pago</strong>. Te avisaremos cuando confirmemos la transferencia y comencemos la preparación.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: 12, textAlign: "left", background: "var(--bg)", borderRadius: "var(--rs)", padding: "18px 20px", marginBottom: 28 }}>
                {[
                  "Validamos tu comprobante (24–48h hábiles)",
                  "Compramos al importador y preparamos tu pedido",
                  `Despachamos a ${region}`,
                ].map((txt, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 13.5, color: "var(--ink-2)" }}>
                    <span className="mono" style={{ width: 22, height: 22, borderRadius: "50%", background: "var(--brand-soft)", color: "var(--brand-deep)", display: "grid", placeItems: "center", fontSize: 12, fontWeight: 700, flexShrink: 0 }}>{i + 1}</span>
                    {txt}
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
                <Link
                  href="/catalogo"
                  style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "11px 20px", background: "var(--brand)", color: "#fff", borderRadius: "var(--rs)", fontWeight: 700, fontSize: 14, textDecoration: "none" }}
                >
                  <GridIcon /> Seguir comprando
                </Link>
              </div>
            </div>
          )}

          {/* Sidebar resumen (pasos 1 y 2) */}
          {step < 3 && (
            <aside style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--radius)", padding: "22px 20px", display: "flex", flexDirection: "column", gap: 12, position: "sticky", top: 80 }}>
              <h3 style={{ fontSize: 15, fontWeight: 800, color: "var(--ink)" }}>Tu pedido</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {items.map((i) => {
                  let sub = 0;
                  try { sub = precioPorCantidad(i, i.cantidad) * i.cantidad; } catch {}
                  return (
                    <div key={i.productoId} style={{ display: "flex", justifyContent: "space-between", fontSize: 13, color: "var(--ink-2)", gap: 8 }}>
                      <span style={{ flex: 1 }}>{i.cantidad}× {i.nombre}</span>
                      <span className="mono" style={{ flexShrink: 0 }}>{clp(sub)}</span>
                    </div>
                  );
                })}
              </div>
              <div style={{ borderTop: "1px solid var(--line)", paddingTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center", fontWeight: 800, fontSize: 15 }}>
                <span>Total</span>
                <strong className="mono">{clp(resumenTotal)}</strong>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--ink-3)" }}>
                <ShieldIcon />
                Folio <span className="mono">{folio}</span>
              </div>
            </aside>
          )}

        </div>
      </main>
    </div>
  );
}
