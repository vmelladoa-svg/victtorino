import Link from "next/link";
import Image from "next/image";

/* ─────────────────────────────────────────────
 COMERCIAL SOLUTIONS — Landing Premium
 Estética: dark-to-light, tipografía display,
 sin emojis, sin bullets de colores, grid limpio
───────────────────────────────────────────── */

const STATS = [
  { value: "500+", label: "Productos en stock" },
  { value: "15",   label: "Regiones de despacho" },
  { value: "48h",  label: "Entrega promedio" },
  { value: "B2B",  label: "Solo empresas" },
];

const FEATURES = [
  {
    title: "Precios por volumen",
    desc:  "Tu precio baja automáticamente a mayor cantidad. Sin negociación, sin sorpresas.",
    tag:   "PRICING",
  },
  {
    title: "Stock en tiempo real",
    desc:  "Cada unidad reflejada al instante. Comprás lo que existe, nada queda pendiente.",
    tag:   "INVENTORY",
  },
  {
    title: "Despacho a todo Chile",
    desc:  "Desde Arica a Punta Arenas. Seguimiento completo del pedido desde el portal.",
    tag:   "LOGISTICS",
  },
  {
    title: "Facturación electrónica",
    desc:  "Emitimos factura con cada pedido. Compatible con cualquier sistema contable.",
    tag:   "BILLING",
  },
];

const STEPS = [
  { n: "01", title: "Regístrate", desc: "Crea tu cuenta con los datos de tu empresa en menos de 2 minutos." },
  { n: "02", title: "Navega el catálogo", desc: "Filtra por categoría, ve el stock disponible y arma tu pedido." },
  { n: "03", title: "Confirma y paga", desc: "Sube tu comprobante de transferencia y el pedido se procesa de inmediato." },
  { n: "04", title: "Recibe tu pedido", desc: "Despachamos a tu dirección con guía de seguimiento incluida." },
];

const CATS = [
  "Cuidado Personal", "Limpieza del Hogar",
  "Alimentos y Bebidas", "Farmacia y Salud",
  "Ferretería", "Electro y Tecnología",
];

/* ── Icons ── */
function IconArrow() {
  return (
    <svg width={14} height={14} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14M12 5l7 7-7 7"/>
    </svg>
  );
}
function IconCheck() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none"
      stroke="#0e7cc4" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  );
}

export default function HomePage() {
  return (
    <div style={{ fontFamily: "var(--font-manrope, 'Inter', system-ui, sans-serif)", background: "#fff", color: "#0a1628", minHeight: "100vh", overflowX: "hidden" }}>

      {/* ── GLOBAL STYLES ── */}
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::selection { background: #0e7cc4; color: #fff; }
        @media (max-width: 768px) {
          .cs-hero-h1  { font-size: 38px !important; }
          .cs-stats     { grid-template-columns: repeat(2,1fr) !important; }
          .cs-feats     { grid-template-columns: 1fr !important; }
          .cs-steps     { grid-template-columns: 1fr !important; }
          .cs-cta-row   { flex-direction: column !important; align-items: stretch !important; }
          .cs-nav-links { display: none !important; }
        }
      `}</style>

      {/* ══════════════════════════════
           NAV
      ══════════════════════════════ */}
      <nav style={{
        position: "sticky", top: 0, zIndex: 100,
        background: "rgba(10,22,40,0.92)",
        backdropFilter: "blur(16px) saturate(180%)",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 32px", height: 64, display: "flex", alignItems: "center", gap: 32 }}>
          <Link href="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <Image src="/logo-clean.png" alt="Comercial Solutions" width={32} height={32}
              style={{ borderRadius: 8, objectFit: "contain" }} />
            <span style={{ fontWeight: 800, fontSize: 15, color: "#fff", letterSpacing: "-0.02em" }}>
              Comercial Solutions
            </span>
          </Link>
          <div className="cs-nav-links" style={{ flex: 1, display: "flex", alignItems: "center", gap: 28, marginLeft: 24 }}>
            <a href="#como-funciona" style={{ fontSize: 13.5, color: "rgba(255,255,255,0.55)", textDecoration: "none", fontWeight: 600 }}>Cómo funciona</a>
            <a href="#categorias"    style={{ fontSize: 13.5, color: "rgba(255,255,255,0.55)", textDecoration: "none", fontWeight: 600 }}>Categorías</a>
          </div>
          <div style={{ flex: 1 }} />
          <Link href="/login" style={{ fontSize: 13.5, fontWeight: 600, color: "rgba(255,255,255,0.65)", textDecoration: "none", padding: "8px 16px" }}>
            Iniciar sesión
          </Link>
          <Link href="/registro" style={{
            fontSize: 13.5, fontWeight: 700, color: "#fff",
            background: "#0e7cc4",
            borderRadius: 8, padding: "10px 22px",
            textDecoration: "none",
            border: "1px solid rgba(255,255,255,0.15)",
            boxShadow: "0 0 0 1px rgba(14,124,196,0.4), 0 4px 16px -4px rgba(14,124,196,0.5)",
          }}>
            Crear cuenta
          </Link>
        </div>
      </nav>

      {/* ══════════════════════════════
           HERO — fondo oscuro, tipografía display
      ══════════════════════════════ */}
      <section style={{
        background: "linear-gradient(160deg, #070f1d 0%, #0a1f3a 55%, #062038 100%)",
        padding: "96px 32px 112px",
        position: "relative",
        overflow: "hidden",
      }}>
        {/* glow decorativo */}
        <div style={{
          position: "absolute", top: "-20%", right: "-10%",
          width: 700, height: 700, borderRadius: "50%",
          background: "radial-gradient(circle, rgba(14,124,196,0.18) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", bottom: "-10%", left: "-5%",
          width: 500, height: 500, borderRadius: "50%",
          background: "radial-gradient(circle, rgba(14,124,196,0.10) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <div style={{ maxWidth: 820, margin: "0 auto", textAlign: "center", position: "relative" }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            background: "rgba(14,124,196,0.12)",
            border: "1px solid rgba(14,124,196,0.3)",
            borderRadius: 99, padding: "6px 16px", marginBottom: 28,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#3ab4f2", display: "inline-block" }} />
            <span style={{ fontSize: 12, fontWeight: 700, color: "#3ab4f2", letterSpacing: "0.08em", textTransform: "uppercase" }}>
              Portal B2B · Solo para empresas
            </span>
          </div>
          <h1 className="cs-hero-h1" style={{
            fontSize: "clamp(42px, 6.5vw, 72px)",
            fontWeight: 800,
            lineHeight: 1.04,
            letterSpacing: "-0.035em",
            color: "#fff",
            margin: "0 0 24px",
          }}>
            La plataforma mayorista<br />
            <span style={{
              background: "linear-gradient(90deg, #3ab4f2, #0e7cc4)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}>
              que tu negocio necesita
            </span>
          </h1>
          <p style={{
            fontSize: 18, lineHeight: 1.65,
            color: "rgba(255,255,255,0.6)",
            maxWidth: 540, margin: "0 auto 40px",
            fontWeight: 400,
          }}>
            Precios por volumen, stock en tiempo real y despacho a todo Chile.
            Acceso exclusivo para negocios y empresas registradas.
          </p>
          <div className="cs-cta-row" style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
            <Link href="/registro" style={{
              display: "inline-flex", alignItems: "center", gap: 10,
              background: "#0e7cc4", color: "#fff",
              fontWeight: 700, fontSize: 15,
              padding: "14px 28px", borderRadius: 10,
              textDecoration: "none",
              boxShadow: "0 8px 32px -8px rgba(14,124,196,0.7)",
              border: "1px solid rgba(255,255,255,0.1)",
            }}>
              Solicitar acceso <IconArrow />
            </Link>
            <Link href="/login" style={{
              display: "inline-flex", alignItems: "center", gap: 10,
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.12)",
              color: "rgba(255,255,255,0.8)", fontWeight: 600, fontSize: 15,
              padding: "14px 24px", borderRadius: 10,
              textDecoration: "none",
            }}>
              Iniciar sesión
            </Link>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════
           STATS BAR
      ══════════════════════════════ */}
      <section style={{
        background: "#0a1628",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "32px 32px",
      }}>
        <div className="cs-stats" style={{
          maxWidth: 900, margin: "0 auto",
          display: "grid", gridTemplateColumns: "repeat(4,1fr)",
          gap: 0,
        }}>
          {STATS.map((s, i) => (
            <div key={s.value} style={{
              textAlign: "center", padding: "16px 24px",
              borderRight: i < STATS.length - 1 ? "1px solid rgba(255,255,255,0.08)" : "none",
            }}>
              <div style={{ fontSize: 30, fontWeight: 800, color: "#fff", letterSpacing: "-0.03em", lineHeight: 1 }}>
                {s.value}
              </div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", fontWeight: 600, marginTop: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════
           FEATURES — fondo blanco limpio
      ══════════════════════════════ */}
      <section style={{ padding: "88px 32px", background: "#fff" }}>
        <div style={{ maxWidth: 1160, margin: "0 auto" }}>
          <div style={{ maxWidth: 520, marginBottom: 56 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: "#0e7cc4", letterSpacing: "0.1em", textTransform: "uppercase" }}>
              PLATAFORMA
            </span>
            <h2 style={{ fontSize: "clamp(28px, 4vw, 40px)", fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.1, marginTop: 10, color: "#0a1628" }}>
              Todo lo que necesita tu operación
            </h2>
          </div>
          <div className="cs-feats" style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 2 }}>
            {FEATURES.map((f) => (
              <div key={f.title} style={{
                background: "#f8fafc",
                border: "1px solid #e8edf2",
                borderRadius: 16,
                padding: "36px 32px",
                display: "flex", flexDirection: "column", gap: 12,
                transition: "border-color .2s",
              }}>
                <span style={{ fontSize: 10, fontWeight: 800, color: "#0e7cc4", letterSpacing: "0.12em", textTransform: "uppercase" }}>
                  {f.tag}
                </span>
                <h3 style={{ fontSize: 20, fontWeight: 800, color: "#0a1628", letterSpacing: "-0.02em" }}>
                  {f.title}
                </h3>
                <p style={{ fontSize: 15, color: "#54657a", lineHeight: 1.65, fontWeight: 400 }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════
           CÓMO FUNCIONA
      ══════════════════════════════ */}
      <section id="como-funciona" style={{ padding: "88px 32px", background: "#f4f7fb" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: "#0e7cc4", letterSpacing: "0.1em", textTransform: "uppercase" }}>
              PROCESO
            </span>
            <h2 style={{ fontSize: "clamp(26px, 4vw, 38px)", fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.1, marginTop: 10, color: "#0a1628" }}>
              Cómo funciona
            </h2>
          </div>
          <div className="cs-steps" style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 24 }}>
            {STEPS.map((s) => (
              <div key={s.n} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: "#0a1628", color: "#fff",
                  display: "grid", placeItems: "center",
                  fontSize: 13, fontWeight: 800, letterSpacing: "0.02em",
                }}>
                  {s.n}
                </div>
                <h3 style={{ fontSize: 16, fontWeight: 800, color: "#0a1628", letterSpacing: "-0.01em" }}>{s.title}</h3>
                <p style={{ fontSize: 14, color: "#54657a", lineHeight: 1.6, fontWeight: 400 }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════
           CATEGORÍAS
      ══════════════════════════════ */}
      <section id="categorias" style={{ padding: "80px 32px", background: "#fff" }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: 40, flexWrap: "wrap", gap: 16 }}>
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#0e7cc4", letterSpacing: "0.1em", textTransform: "uppercase" }}>CATÁLOGO</span>
              <h2 style={{ fontSize: "clamp(24px, 3.5vw, 34px)", fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.1, marginTop: 8, color: "#0a1628" }}>
                Categorías disponibles
              </h2>
            </div>
            <Link href="/registro" style={{ fontSize: 14, fontWeight: 700, color: "#0e7cc4", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 6 }}>
              Ver catálogo completo <IconArrow />
            </Link>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {CATS.map((c) => (
              <div key={c} style={{
                padding: "10px 20px",
                border: "1px solid #e0e8f0",
                borderRadius: 99,
                fontSize: 14, fontWeight: 600, color: "#0a1628",
                background: "#f8fafc",
              }}>
                {c}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════
           CTA FINAL — dark premium
      ══════════════════════════════ */}
      <section style={{
        background: "linear-gradient(160deg, #070f1d 0%, #0a1f3a 100%)",
        padding: "96px 32px",
        position: "relative", overflow: "hidden",
      }}>
        <div style={{
          position: "absolute", top: "50%", left: "50%",
          transform: "translate(-50%,-50%)",
          width: 800, height: 400, borderRadius: "50%",
          background: "radial-gradient(ellipse, rgba(14,124,196,0.15) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <div style={{ maxWidth: 640, margin: "0 auto", textAlign: "center", position: "relative" }}>
          <h2 style={{
            fontSize: "clamp(30px, 5vw, 48px)", fontWeight: 800,
            letterSpacing: "-0.03em", lineHeight: 1.08,
            color: "#fff", marginBottom: 16,
          }}>
            Acceso exclusivo para negocios registrados
          </h2>
          <p style={{ fontSize: 17, color: "rgba(255,255,255,0.55)", lineHeight: 1.65, marginBottom: 40, fontWeight: 400 }}>
            Regístrate con los datos de tu empresa y obtén acceso inmediato al catálogo completo, precios mayoristas y herramientas de gestión.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, alignItems: "center", marginBottom: 40 }}>
            {["Sin costo de membresía", "Aprobación en menos de 24 horas", "Soporte directo por WhatsApp"].map((t) => (
              <div key={t} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 14.5, color: "rgba(255,255,255,0.75)", fontWeight: 500 }}>
                <IconCheck /> {t}
              </div>
            ))}
          </div>
          <Link href="/registro" style={{
            display: "inline-flex", alignItems: "center", gap: 10,
            background: "#fff", color: "#0a1628",
            fontWeight: 800, fontSize: 15,
            padding: "15px 32px", borderRadius: 10,
            textDecoration: "none",
            boxShadow: "0 8px 32px -8px rgba(0,0,0,0.4)",
          }}>
            Solicitar acceso <IconArrow />
          </Link>
        </div>
      </section>

      {/* ══════════════════════════════
           FOOTER
      ══════════════════════════════ */}
      <footer style={{
        background: "#070f1d",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        padding: "28px 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Image src="/logo-clean.png" alt="Comercial Solutions" width={24} height={24} style={{ borderRadius: 6, objectFit: "contain", opacity: 0.7 }} />
          <span style={{ fontSize: 13, color: "rgba(255,255,255,0.35)", fontWeight: 500 }}>
            © 2026 Trade Global Solutions SpA
          </span>
        </div>
        <div style={{ display: "flex", gap: 24 }}>
          <Link href="/login"    style={{ fontSize: 13, color: "rgba(255,255,255,0.35)", textDecoration: "none", fontWeight: 500 }}>Iniciar sesión</Link>
          <Link href="/registro" style={{ fontSize: 13, color: "rgba(255,255,255,0.35)", textDecoration: "none", fontWeight: 500 }}>Registrarse</Link>
        </div>
      </footer>

    </div>
  );
      }
