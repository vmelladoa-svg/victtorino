"use client";

import { useState } from "react";

const SLOTS = [
  { id: "amb-1", cap: "Baño con espejo LED" },
  { id: "amb-2", cap: "Rain shower" },
  { id: "amb-3", cap: "Cocina equipada" },
  { id: "amb-4", cap: "Vanitorio doble" },
  { id: "amb-5", cap: "Lavadero minimalista" },
  { id: "amb-6", cap: "Mampara de vidrio" },
];

function AmbCard({ s }: { s: { id: string; cap: string } }) {
  const [imgOk, setImgOk] = useState(true);
  return (
    <div className="amb-card">
      <div className="amb-media">
        {imgOk ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`/ambientes/${s.id}.webp`}
            alt={s.cap}
            loading="lazy"
            onError={() => setImgOk(false)}
          />
        ) : (
          <span className="amb-ph">Foto: {s.cap}</span>
        )}
      </div>
      <div className="amb-cap">
        <b>{s.cap}</b>
        <span>Ambiente</span>
      </div>
    </div>
  );
}

export function AmbientGallery() {
  return (
    <section className="block soft" id="ambientes">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Inspírate</span>
            <h2>Espacios reales con productos Trade</h2>
            <p className="sec-sub">
              Ambientes e instalaciones terminadas con nuestros productos.
            </p>
          </div>
        </div>
        <div className="amb-grid">
          {SLOTS.map((s) => (
            <AmbCard key={s.id} s={s} />
          ))}
        </div>
      </div>
    </section>
  );
}
