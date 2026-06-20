"use client";

import { useState } from "react";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

export function InstallSection() {
  const { openInstallTerms } = useStore();
  const [imgOk, setImgOk] = useState(true);
  return (
    <section className="block" id="instalacion">
      <div className="wrap install-band">
        <div className="install-visual">
          {imgOk && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src="/categories/instalacion.webp"
              alt="Servicio de instalación Trade"
              loading="lazy"
              onError={() => setImgOk(false)}
            />
          )}
        </div>
        <div>
          <span className="sec-kicker">Servicio adicional</span>
          <h2 style={{ fontSize: 30, marginBottom: 12 }}>
            ¿Compraste tus productos? Te los instalamos.
          </h2>
          <p style={{ color: "var(--ink-soft)", fontSize: 16 }}>
            Agregas la instalación al comprar y nosotros te asignamos un maestro verificado que te
            contacta por WhatsApp para coordinar. Sin cotizaciones ni costos ocultos.
          </p>
          <div className="install-list">
            <span>
              <Icon d={ICONS.check} size={18} /> Maestro verificado asignado al comprar
            </span>
            <span>
              <Icon d={ICONS.check} size={18} /> Registro fotográfico: antes, durante y al finalizar
            </span>
            <span>
              <Icon d={ICONS.check} size={18} /> Garantía de 30 días · Solo Región Metropolitana
            </span>
          </div>
          <button className="btn btn-primary" onClick={openInstallTerms}>
            Ver condiciones del servicio
          </button>
        </div>
      </div>
    </section>
  );
}
