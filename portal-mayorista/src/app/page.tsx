import Link from "next/link";
import Image from "next/image";

/* ── icons ── */
function CheckIcon() {
  return (
    <svg width={18} height={18} viewBox="0 0 24 24" fill="none"
      stroke="#6ec9f7" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"
      style={{ flexShrink: 0 }}>
      <path d="M5 13l4 4L19 7" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14M12 5l7 7-7 7" />
    </svg>
  );
}

const FEATURES = [
  { icon: "📦", title: "Stock en tiempo real", desc: "Consultá disponibilidad actualizada antes de confirmar tu pedido." },
  { icon: "💰", title: "Precios escalonados", desc: "A mayor volumen, menor precio por unidad. Desde 1 caja." },
  { icon: "🚚", title: "Despacho a todo Chile", desc: "Enviamos a todas las regiones. Seguimiento de pedido incluido." },
  { icon: "🧾", title: "Facturación disponible", desc: "Emitimos factura electrónica para tu empresa o negocio." },
];

const CATEGORIAS = [
  "Cuidado Personal", "Limpieza del Hogar", "Alimentos y Bebidas",
  "Farmacia", "Ferretería", "Electro y Tecnología",
];

export default function HomePage() {
  return (
    <div style={{ fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif", color: "#0f1b2a", background: "#f7f9fb", minHeight: "100vh" }}>

      {/* ── NAV ── */}
      <nav style={{
        position: "sticky", top: 0, zIndex: 50,
        background: "rgba(255,255,255,0.95)", backdropFilter: "blur(12px)",
        borderBottom: "1px solid #e4ebf2",
        padding: "0 32px",
      }}>
        <div style={{ maxWidth: 1180, margin: "0 auto", display: "flex", alignItems: "center", gap: 16, height: 62 }}>
          <Image src="/logo-clean.png" alt="Comercial Solutions" width={34} height={34} style={{ borderRadius: "50%", objectFit: "contain" }} />
          <span style={{ fontWeight: 800, fontSize: 15, letterSpacing: "-0.01em" }}>Comercial Solutions</span>
          <span style={{ fontSize: 11, color: "#8696a8", fontWeight: 600, background: "#f0f4f8", padding: "2px 8px", borderRadius: 99 }}>Portal Mayorista</span>
          <div style={{ flex: 1 }} />
          <Link href="/login" style={{ fontSize: 14, fontWeight: 600, color: "#54657a", textDecoration: "none", padding: "8px 16px" }}>
            Iniciar sesión
          </Link>
          <Link href="/registro" style={{
            fontSize: 14, fontWeight: 700, color: "#fff",
            background: "#0e7cc4", borderRadius: 8,
            padding: "9px 20px", textDecoration: "none",
            boxShadow: "0 4px 12px -4px rgba(14,124,196,0.4)",
          }}>
            Registrarse
          </Link>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section style={{
        background: "linear-gradient(150deg, #083e62 0%, #051f35 100%)",
        color: "#fff", padding: "80px 32px 90px",
      }}>
        <div style={{ maxWidth: 780, margin: "0 auto", textAlign: "center" }}>
          <span style={{
            display: "inline-block", background: "rgba(110,201,247,0.15)",
            color: "#6ec9f7", fontSize: 12.5, fontWeight: 700,
            padding: "5px 14px", borderRadius: 99, marginBottom: 22,
            border: "1px solid rgba(110,201,247,0.3)",
          }}>
            Portal B2B · Solo para empresas y negocios
          </span>
          <h1 style={{ fontSize: "clamp(36px, 6vw, 58px)", fontWeight: 800, lineHeight: 1.08, letterSpacing: "-0.03em", margin: "0 0 20px" }}>
            Compra al por mayor,<br />
            <span style={{ color: "#6ec9f7" }}>sin complicaciones</span>
          </h1>
          <p style={{ fontSize: 18, lineHeight: 1.6, color: "rgba(255,255,255,0.78)", maxWidth: 560, margin: "0 auto 36px" }}>
            Accede a precios mayoristas, volumen por caja y despacho a todo Chile.
            Regístrate gratis y empieza a comprar hoy.
          </p>
          <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
            <Link href="/registro" style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              background: "#0e7cc4", color: "#fff", fontWeight: 700,
              fontSize: 16, padding: "14px 28px", borderRadius: 10,
              textDecoration: "none", boxShadow: "0 8px 24px -6px rgba(14,124,196,0.5)",
            }}>
              Crear cuenta gratis <ArrowIcon />
            </Link>
            <Link href="/login" style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              background: "rgba(255,255,255,0.1)", color: "#fff", fontWeight: 600,
              fontSize: 15, padding: "14px 24px", borderRadius: 10,
              textDecoration: "none", border: "1px solid rgba(255,255,255,0.2)",
            }}>
              Ya tengo cuenta
            </Link>
          </div>
        </div>
      </section>

      {/* ── BENEFICIOS ── */}
      <section style={{ padding: "72px 32px", background: "#fff" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <h2 style={{ textAlign: "center", fontSize: 30, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 48 }}>
            Todo lo que necesita tu negocio
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 24 }}>
            {FEATURES.map((f) => (
              <div key={f.title} style={{
                background: "#f7f9fb", borderRadius: 14,
                padding: "28px 24px", border: "1px solid #e4ebf2",
              }}>
                <div style={{ fontSize: 32, marginBottom: 14 }}>{f.icon}</div>
                <h3 style={{ fontSize: 16, fontWeight: 800, margin: "0 0 8px", letterSpacing: "-0.01em" }}>{f.title}</h3>
                <p style={{ fontSize: 14, color: "#54657a", lineHeight: 1.55, margin: 0 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CATEGORÍAS ── */}
      <section style={{ padding: "60px 32px", background: "#f7f9fb" }}>
        <div style={{ maxWidth: 900, margin: "0 auto", textAlign: "center" }}>
          <h2 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 8 }}>Categorías disponibles</h2>
          <p style={{ fontSize: 15, color: "#54657a", marginBottom: 32 }}>
            Más de 500 productos en stock permanente
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, justifyContent: "center" }}>
            {CATEGORIAS.map((c) => (
              <span key={c} style={{
                background: "#fff", border: "1px solid #e4ebf2",
                borderRadius: 99, padding: "8px 18px",
                fontSize: 14, fontWeight: 600, color: "#0f1b2a",
              }}>{c}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA FINAL ── */}
      <section style={{
        background: "linear-gradient(150deg, #083e62 0%, #051f35 100%)",
        color: "#fff", padding: "72px 32px", textAlign: "center",
      }}>
        <div style={{ maxWidth: 600, margin: "0 auto" }}>
          <h2 style={{ fontSize: 34, fontWeight: 800, letterSpacing: "-0.02em", margin: "0 0 14px" }}>
            ¿Listo para comprar al por mayor?
          </h2>
          <p style={{ fontSize: 16, color: "rgba(255,255,255,0.75)", marginBottom: 32 }}>
            Regístrate hoy. La aprobación es inmediata y sin costo.
          </p>
          <ul style={{ listStyle: "none", padding: 0, margin: "0 0 32px", display: "flex", flexDirection: "column", gap: 10, alignItems: "center" }}>
            {["Sin monto mínimo para registrarse", "Precios actualizados en tiempo real", "Soporte por WhatsApp"].map((t) => (
              <li key={t} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 15, fontWeight: 500 }}>
                <CheckIcon /> {t}
              </li>
            ))}
          </ul>
          <Link href="/registro" style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            background: "#0e7cc4", color: "#fff", fontWeight: 700,
            fontSize: 16, padding: "14px 32px", borderRadius: 10,
            textDecoration: "none", boxShadow: "0 8px 24px -6px rgba(14,124,196,0.5)",
          }}>
            Crear cuenta gratis <ArrowIcon />
          </Link>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{
        background: "#051f35", color: "rgba(255,255,255,0.45)",
        textAlign: "center", padding: "24px 32px", fontSize: 13,
      }}>
        © 2026 Trade Global Solutions SpA · comercialsolutions.cl
      </footer>

    </div>
  );
}
