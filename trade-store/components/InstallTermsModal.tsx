"use client";

import { INSTALL_TERMS } from "@/lib/install-terms";
import { useStore } from "@/lib/store-context";

export function InstallTermsModal() {
  const { installTermsOpen, closeInstallTerms } = useStore();
  if (!installTermsOpen) return null;
  return (
    <div>
      <div className="overlay" onClick={closeInstallTerms} />
      <div
        className="modal"
        onClick={(e) => {
          if (e.target === e.currentTarget) closeInstallTerms();
        }}
      >
        <div className="modal-card" style={{ maxWidth: 560 }}>
          <button
            className="icon-btn"
            style={{ position: "absolute", top: 16, right: 16, zIndex: 2 }}
            onClick={closeInstallTerms}
            aria-label="Cerrar"
          >
            ✕
          </button>
          <div style={{ padding: "36px 36px 32px" }}>
            <span className="sec-kicker">Servicio de instalación</span>
            <h3 style={{ fontSize: 22, marginBottom: 18 }}>Condiciones del servicio</h3>
            <ol className="terms-list">
              {INSTALL_TERMS.map((t) => (
                <li key={t.title}>
                  <b>{t.title}</b>
                  <p>{t.body}</p>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
