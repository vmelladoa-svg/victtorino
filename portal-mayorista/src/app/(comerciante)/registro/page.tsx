"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";

export default function RegistroPage() {
  const router = useRouter();

  const [form, setForm] = useState({
    nombre: "",
    email: "",
    clave: "",
    claveConfirm: "",
    rutEmpresa: "",
    giro: "",
    telefono: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    if (form.clave !== form.claveConfirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    if (form.clave.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/registro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre: form.nombre,
          email: form.email,
          clave: form.clave,
          rutEmpresa: form.rutEmpresa,
          giro: form.giro,
          telefono: form.telefono,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error ?? "Error al crear la cuenta. Intenta nuevamente.");
        return;
      }

      setSuccess(true);
      // Meta Pixel: registro de comerciante completado
      (window as unknown as { fbq?: (...a: unknown[]) => void }).fbq?.(
        "track",
        "CompleteRegistration"
      );
      setTimeout(() => router.push("/login?registrado=1"), 2000);
    } catch {
      setError("Error de conexión. Intenta nuevamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.aside}>
        <div style={styles.asideBody}>
          <div style={styles.logoWrap}>
            <Image
              src="/logo-clean.png"
              alt="Trade Global Solutions"
              width={42}
              height={42}
              style={styles.logoImg}
            />
            <div style={styles.logoText}>
              <strong style={styles.logoStrong}>Trade Global</strong>
              <small style={styles.logoSmall}>Portal Mayorista</small>
            </div>
          </div>
          <h1 style={styles.asideH1}>Venta por Mayor para tu negocio</h1>
          <p style={styles.asideP}>
            Regístrate y accede a precios mayoristas, volumen por caja
            y despacho a todo Chile.
          </p>
          <ul style={styles.feats}>
            <li style={styles.featItem}><CheckIcon /> Precios escalonados por volumen</li>
            <li style={styles.featItem}><CheckIcon /> Stock en tiempo real</li>
            <li style={styles.featItem}><CheckIcon /> Seguimiento de pedido completo</li>
            <li style={styles.featItem}><CheckIcon /> Facturación disponible</li>
          </ul>
        </div>
        <footer style={styles.asideFoot}>2026 Trade Global Solutions SpA</footer>
      </div>

      <div style={styles.formWrap}>
        <div style={styles.formCard}>
          <h2 style={styles.formH2}>Crear cuenta</h2>
          <p style={styles.formSub}>
            ¿Ya tienes cuenta?{" "}
            <Link href="/login" style={styles.link}>Inicia sesión</Link>
          </p>

          {success ? (
            <div style={styles.successBox}>
              <CheckIcon color="#1f9d57" />
              <span>Tu cuenta fue creada. Quedará en revisión. Redirigiendo...</span>
            </div>
          ) : (
            <form onSubmit={handleSubmit} noValidate>
              {error && <div style={styles.errorBox}>{error}</div>}

              <div style={styles.formGrid}>
                <div style={styles.field}>
                  <label style={styles.label} htmlFor="nombre">Nombre completo</label>
                  <input id="nombre" name="nombre" type="text" autoComplete="name" required
                    placeholder="Maria Fernanda Rojas" value={form.nombre} onChange={handleChange} style={styles.input} />
                </div>

                <div style={styles.field}>
                  <label style={styles.label} htmlFor="email">Email</label>
                  <input id="email" name="email" type="email" autoComplete="email" required
                    placeholder="compras@empresa.cl" value={form.email} onChange={handleChange} style={styles.input} />
                </div>

                <div style={styles.field}>
                  <label style={styles.label} htmlFor="clave">Contraseña</label>
                  <input id="clave" name="clave" type="password" autoComplete="new-password" required
                    placeholder="Mínimo 8 caracteres" value={form.clave} onChange={handleChange} style={styles.input} />
                </div>

                <div style={styles.field}>
                  <label style={styles.label} htmlFor="claveConfirm">Confirmar contraseña</label>
                  <input id="claveConfirm" name="claveConfirm" type="password" autoComplete="new-password" required
                    placeholder="Repite tu contraseña" value={form.claveConfirm} onChange={handleChange} style={styles.input} />
                </div>

                <div style={styles.field}>
                  <label style={styles.label} htmlFor="rutEmpresa">RUT empresa</label>
                  <input id="rutEmpresa" name="rutEmpresa" type="text" required
                    placeholder="76.998.221-4" value={form.rutEmpresa} onChange={handleChange} style={styles.input} />
                </div>

                <div style={styles.field}>
                  <label style={styles.label} htmlFor="giro">Giro comercial</label>
                  <input id="giro" name="giro" type="text" required
                    placeholder="Comercio al por menor" value={form.giro} onChange={handleChange} style={styles.input} />
                </div>

                <div style={{ ...styles.field, gridColumn: "1 / -1" }}>
                  <label style={styles.label} htmlFor="telefono">
                    Teléfono (WhatsApp)
                  </label>
                  <input id="telefono" name="telefono" type="tel" autoComplete="tel" required
                    placeholder="+56 9 1234 5678" value={form.telefono} onChange={handleChange} style={styles.input} />
                </div>
              </div>

              <button type="submit" disabled={loading} style={{
                ...styles.btnPrimary,
                opacity: loading ? 0.6 : 1,
                cursor: loading ? "not-allowed" : "pointer",
              }}>
                {loading ? "Creando cuenta..." : "Crear cuenta"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

function CheckIcon({ color = "#6ec9f7" }: { color?: string }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke={color} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"
      style={{ flexShrink: 0 }}>
      <path d="M5 13l4 4L19 7" />
    </svg>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh", display: "grid", gridTemplateColumns: "1.05fr 1fr",
    fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
  },
  aside: {
    background: "linear-gradient(150deg, #083e62, #051f35)", color: "#fff",
    padding: "44px", display: "flex", flexDirection: "column",
    justifyContent: "space-between", position: "relative", overflow: "hidden",
  },
  asideBody: { position: "relative", maxWidth: "460px" },
  logoWrap: { display: "flex", alignItems: "center", gap: "11px", marginBottom: "32px" },
  logoImg: { borderRadius: "50%", objectFit: "contain" },
  logoText: { display: "flex", flexDirection: "column", lineHeight: 1.05 },
  logoStrong: { fontSize: "16px", fontWeight: 800, color: "#fff" },
  logoSmall: { fontSize: "11px", color: "rgba(255,255,255,0.65)", fontWeight: 600 },
  asideH1: { fontSize: "38px", fontWeight: 800, lineHeight: 1.1, margin: "0 0 16px", letterSpacing: "-0.02em" },
  asideP: { fontSize: "16px", lineHeight: 1.55, color: "rgba(255,255,255,0.82)", margin: 0 },
  feats: { listStyle: "none", padding: 0, margin: "28px 0 0", display: "flex", flexDirection: "column", gap: "14px" },
  featItem: { display: "flex", alignItems: "center", gap: "12px", fontWeight: 600, fontSize: "15px" },
  asideFoot: { position: "relative", fontSize: "12.5px", color: "rgba(255,255,255,0.5)", fontFamily: "monospace" },
  formWrap: { display: "grid", placeItems: "center", padding: "44px", background: "#ffffff" },
  formCard: { width: "100%", maxWidth: "420px" },
  formH2: { fontSize: "26px", fontWeight: 800, letterSpacing: "-0.02em", margin: 0 },
  formSub: { color: "#54657a", fontSize: "14.5px", margin: "8px 0 24px" },
  link: { color: "#0e7cc4", fontWeight: 600, textDecoration: "none" },
  formGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 16px" },
  field: { display: "flex", flexDirection: "column", gap: "7px", marginBottom: "16px" },
  label: { fontSize: "12.5px", fontWeight: 700, color: "#54657a" },
  optional: { fontWeight: 500, color: "#8696a8" },
  input: {
    width: "100%", padding: "12px 14px", border: "1px solid #e4ebf2",
    borderRadius: "7px", fontSize: "14.5px", background: "#ffffff",
    color: "#0f1b2a", outline: "none", fontFamily: "inherit",
  },
  btnPrimary: {
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    width: "100%", padding: "14px 22px", fontSize: "15.5px", fontWeight: 700,
    background: "#0e7cc4", color: "#fff", border: "1px solid transparent",
    borderRadius: "7px", marginTop: "8px", fontFamily: "inherit",
    boxShadow: "0 6px 16px -8px rgba(14,124,196,0.5)",
  },
  errorBox: {
    background: "#fbeceb", color: "#c4423f", border: "1px solid #f5c6c5",
    borderRadius: "7px", padding: "11px 14px", fontSize: "14px",
    marginBottom: "16px", fontWeight: 600,
  },
  successBox: {
    background: "#e9f7ee", color: "#1f9d57", border: "1px solid #b8e4cc",
    borderRadius: "7px", padding: "14px 16px", fontSize: "14px",
    fontWeight: 600, display: "flex", alignItems: "center", gap: "10px",
  },
};
