"use client";

import { useEffect, useState } from "react";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

const STEPS = [
  { b: "Pedido recibido", d: "Confirmamos tu compra y tu boleta fue enviada por correo", st: "done" },
  { b: "Pago confirmado", d: "Tu pago fue verificado correctamente", st: "done" },
  { b: "En preparación", d: "Estamos embalando tus productos en bodega", st: "done" },
  { b: "En camino", d: "Tu pedido va en ruta con el courier", st: "now" },
  { b: "Entregado", d: "Recibirás una confirmación al momento de la entrega", st: "" },
];

export function TrackingModal() {
  const { trackOpen, closeTracking } = useStore();
  const [code, setCode] = useState("");
  const [found, setFound] = useState(false);

  useEffect(() => {
    if (trackOpen) {
      setFound(false);
      setCode("");
    }
  }, [trackOpen]);

  if (!trackOpen) return null;

  return (
    <div>
      <div className="overlay" onClick={closeTracking} />
      <div
        className="modal"
        onClick={(e) => {
          if (e.target === e.currentTarget) closeTracking();
        }}
      >
        <div className="modal-card" style={{ maxWidth: 480 }}>
          <button
            className="icon-btn"
            style={{ position: "absolute", top: 16, right: 16, zIndex: 2 }}
            onClick={closeTracking}
            aria-label="Cerrar"
          >
            ✕
          </button>
          <div style={{ padding: "36px 36px 32px" }}>
            <h3 style={{ fontSize: 22, marginBottom: 6 }}>Seguir mi pedido</h3>
            <p style={{ color: "var(--ink-soft)", fontSize: 14.5, marginBottom: 20 }}>
              Ingresa el número de pedido que recibiste en tu correo de confirmación.
            </p>
            <form
              style={{ display: "flex", gap: 10 }}
              onSubmit={(e) => {
                e.preventDefault();
                if (code.trim()) setFound(true);
              }}
            >
              <input
                style={{
                  flex: 1,
                  border: "1.5px solid var(--line)",
                  borderRadius: 10,
                  padding: "12px 14px",
                  fontSize: 15,
                  outline: "none",
                }}
                placeholder="Ej: TR-10234"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <button className="btn btn-primary" type="submit">
                Buscar
              </button>
            </form>
            {found && (
              <div>
                <div className="track-steps">
                  {STEPS.map((s, i) => (
                    <div className={"track-step " + s.st} key={s.b}>
                      {i < STEPS.length - 1 && <span className="track-line" />}
                      <span className="track-dot">
                        {s.st === "done" ? <Icon d={ICONS.check} size={13} stroke={2.4} /> : null}
                      </span>
                      <span>
                        <b>{s.b}</b>
                        <span className="td">{s.d}</span>
                      </span>
                    </div>
                  ))}
                </div>
                <div className="demo-note" style={{ marginTop: 18 }}>
                  Demo: el seguimiento real se conectará al sistema del courier al publicar el
                  sitio.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
