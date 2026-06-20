import Image from "next/image";
import Link from "next/link";

export const metadata = { title: "Cuenta en revision | Trade Global" };

export default function RevisionPage() {
  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logoWrap}>
          <Image
            src="/logo-clean.png"
            alt="Trade Global Solutions"
            width={52}
            height={52}
            style={styles.logoImg}
          />
          <div style={styles.logoText}>
            <strong style={styles.logoStrong}>Trade Global</strong>
            <small style={styles.logoSmall}>Portal Mayorista</small>
          </div>
        </div>

        <div style={styles.iconWrap}>
          <ClockIcon />
        </div>

        <h1 style={styles.heading}>Tu cuenta está en revisión</h1>

        <p style={styles.body}>
          Hemos recibido tu solicitud. Revisaremos tu información y te
          notificaremos cuando tu cuenta sea aprobada.
        </p>

        <div style={styles.infoBox}>
          <InfoIcon />
          <span>
            El proceso de revisión toma entre 24 y 48 horas hábiles.
            Si tienes dudas, contactanos en{" "}
            <a href="mailto:contacto@tradeglobalsolutions.cl" style={styles.emailLink}>
              contacto@tradeglobalsolutions.cl
            </a>
          </span>
        </div>

        <Link href="/" style={styles.btnPrimary}>
          Volver al inicio
        </Link>
      </div>

      <footer style={styles.foot}>
        2026 Trade Global Solutions SpA
      </footer>
    </div>
  );
}

function ClockIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
      stroke="#0e7cc4" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="#0e7cc4" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
      style={{ flexShrink: 0, marginTop: "1px" }}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v4M12 16h.01" />
    </svg>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh", display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center",
    background: "#f3f6fa", fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
    padding: "24px",
  },
  card: {
    background: "#ffffff", border: "1px solid #e4ebf2",
    borderRadius: "16px", padding: "44px 40px",
    maxWidth: "480px", width: "100%", textAlign: "center",
    boxShadow: "0 6px 22px -8px rgba(16,40,70,0.16)",
  },
  logoWrap: {
    display: "flex", alignItems: "center", gap: "12px",
    justifyContent: "center", marginBottom: "28px",
  },
  logoImg: { borderRadius: "50%", objectFit: "contain" },
  logoText: { display: "flex", flexDirection: "column", lineHeight: 1.05, textAlign: "left" },
  logoStrong: { fontSize: "17px", fontWeight: 800, color: "#0f1b2a" },
  logoSmall: { fontSize: "12px", color: "#8696a8", fontWeight: 600 },
  iconWrap: {
    width: "80px", height: "80px", borderRadius: "50%",
    background: "#e7f0fc", display: "grid", placeItems: "center",
    margin: "0 auto 20px",
  },
  heading: {
    fontSize: "24px", fontWeight: 800, letterSpacing: "-0.02em",
    color: "#0f1b2a", margin: "0 0 12px",
  },
  body: {
    fontSize: "15px", lineHeight: 1.6, color: "#54657a",
    margin: "0 0 24px",
  },
  infoBox: {
    display: "flex", alignItems: "flex-start", gap: "10px", textAlign: "left",
    background: "#e7f0fc", border: "1px solid #bdd5f0", borderRadius: "10px",
    padding: "14px 16px", fontSize: "13.5px", color: "#1366c4",
    fontWeight: 500, marginBottom: "28px", lineHeight: 1.5,
  },
  emailLink: { color: "#0e7cc4", fontWeight: 700, textDecoration: "underline" },
  btnPrimary: {
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    width: "100%", padding: "14px 22px", fontSize: "15.5px", fontWeight: 700,
    background: "#0e7cc4", color: "#fff", border: "1px solid transparent",
    borderRadius: "7px", textDecoration: "none",
    boxShadow: "0 6px 16px -8px rgba(14,124,196,0.5)",
  },
  foot: {
    marginTop: "24px", fontSize: "12.5px", color: "#8696a8",
    fontFamily: "monospace",
  },
};
