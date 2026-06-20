"use client";

import { useState } from "react";
import { Icon, ICONS } from "./Icon";

export function Newsletter() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  return (
    <section className="block" style={{ paddingBottom: 0 }}>
      <div className="wrap">
        <div className="news-band">
          <div>
            <span className="sec-kicker">Ofertas exclusivas</span>
            <h2>Recibe descuentos antes que nadie</h2>
            <p>
              Súmate a nuestra lista y te avisamos de ofertas, reposiciones y productos nuevos.
              Sin spam.
            </p>
          </div>
          {sent ? (
            <span className="news-ok">
              <Icon d={ICONS.check} size={20} /> ¡Listo! Te avisaremos de las próximas ofertas.
            </span>
          ) : (
            <form
              className="news-form"
              onSubmit={(e) => {
                e.preventDefault();
                if (email.trim()) setSent(true);
              }}
            >
              <input
                type="email"
                required
                placeholder="tucorreo@ejemplo.cl"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <button className="btn btn-primary" type="submit">
                Suscribirme
              </button>
            </form>
          )}
        </div>
      </div>
    </section>
  );
}
