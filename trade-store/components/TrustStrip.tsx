import { Icon, ICONS } from "./Icon";

const ITEMS = [
  { ic: "truck", b: "Despacho a todo Chile", s: "Envíos en 2–5 días hábiles" },
  { ic: "shield", b: "Garantía 6 meses", s: "En todos nuestros productos" },
  { ic: "lock", b: "Compra segura", s: "Webpay, transferencia y tarjetas" },
  { ic: "chat", b: "Atención por WhatsApp", s: "Te ayudamos a elegir" },
];

export function TrustStrip() {
  return (
    <div className="trust">
      <div className="wrap trust-in">
        {ITEMS.map((it) => (
          <div className="trust-item" key={it.b}>
            <Icon d={ICONS[it.ic]} size={28} stroke={1.6} />
            <div>
              <b>{it.b}</b>
              <span>{it.s}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
