"use client";

import { ZONES } from "@/lib/shipping";
import { formatCLP } from "@/lib/format";
import { useStore } from "@/lib/store-context";

export function DespachoSection() {
  const { shipZone, setShipZone } = useStore();
  return (
    <section className="block soft" id="despacho">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Despacho</span>
            <h2>Zonas y tarifas de despacho</h2>
            <p className="sec-sub">
              Elige tu zona; la tarifa se aplica en el carrito. Sobre cierto monto, el despacho
              es gratis. También puedes retirar en bodega sin costo.
            </p>
          </div>
        </div>
        <div className="zone-grid">
          {ZONES.map((z) => (
            <button
              key={z.id}
              className={"zone-card" + (shipZone === z.id ? " on" : "")}
              onClick={() => setShipZone(z.id)}
            >
              <b>{z.name}</b>
              <span className="zone-cost">{z.cost === 0 ? "Gratis" : formatCLP(z.cost)}</span>
              <span className="zone-eta">{z.eta}</span>
              {z.freeMin ? (
                <span className="zone-free">Gratis sobre {formatCLP(z.freeMin)}</span>
              ) : (
                <span className="zone-free">Sin costo de envío</span>
              )}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
