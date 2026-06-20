/* ============================================================
   Componentes compartidos — Trade Global Solutions
   ============================================================ */
const { useState, useEffect, useRef, useMemo } = React;

/* ---------- Iconos (line icons simples) ---------- */
const ICON_PATHS = {
  grid: "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
  chip: "M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3M6 6h12v12H6z",
  home: "M3 11l9-8 9 8M5 10v10h14V10",
  drop: "M12 3s6 6.5 6 10a6 6 0 0 1-12 0c0-3.5 6-10 6-10z",
  box: "M3 7l9-4 9 4-9 4-9-4zM3 7v10l9 4 9-4V7M12 11v10",
  tool: "M14 7a4 4 0 0 1-5 5l-6 6 2 2 6-6a4 4 0 0 0 5-5l-2 2-2-2 2-2z",
  shirt: "M4 5l4-2 4 3 4-3 4 2-2 4-2-1v11H8V8L6 9z",
  search: "M11 4a7 7 0 1 1 0 14 7 7 0 0 1 0-14zM20 20l-3.5-3.5",
  cart: "M3 4h2l2.4 12.4a1 1 0 0 0 1 .8h8.7a1 1 0 0 0 1-.8L21 8H6M9 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2zM18 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2z",
  user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
  check: "M5 13l4 4L19 7",
  plus: "M12 5v14M5 12h14",
  minus: "M5 12h14",
  chevdown: "M6 9l6 6 6-6",
  chevright: "M9 6l6 6-6 6",
  chevleft: "M15 6l-6 6 6 6",
  bolt: "M13 2L4 14h7l-1 8 9-12h-7z",
  truck: "M3 6h11v9H3zM14 9h4l3 3v3h-7M7 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM17 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z",
  shield: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
  upload: "M12 16V4M7 9l5-5 5 5M4 20h16",
  doc: "M6 2h8l4 4v16H6zM14 2v4h4",
  filter: "M3 5h18M6 12h12M10 19h4",
  pin: "M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11zM12 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
  clock: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2",
  star: "M12 3l2.6 5.6L21 9.3l-4.5 4.3 1.1 6.1L12 17l-5.6 2.7L7.5 13.6 3 9.3l6.4-.7z",
  x: "M6 6l12 12M18 6L6 18",
  package: "M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10",
  trash: "M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14",
  logout: "M14 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-2M9 12h11M17 9l3 3-3 3",
};
function Icon({ name, size = 20, stroke = 1.8, style }) {
  const d = ICON_PATHS[name] || "";
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={stroke} strokeLinecap="round"
      strokeLinejoin="round" style={style} aria-hidden="true">
      {d.split("M").filter(Boolean).map((seg, i) => <path key={i} d={"M" + seg} />)}
    </svg>
  );
}

/* ---------- Placeholder de imagen (rayas + label mono) ---------- */
function ProductImage({ prod, h = 200, label }) {
  const tint = prod ? prod.tint : "#2b8466";
  const id = "stripe-" + (prod ? prod.id : "x") + "-" + Math.round(h);
  return (
    <div className="prod-img" style={{ height: h, background: tint + "14" }}>
      <svg width="100%" height="100%" preserveAspectRatio="none" style={{ position: "absolute", inset: 0 }}>
        <defs>
          <pattern id={id} width="14" height="14" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
            <rect width="14" height="14" fill="none" />
            <line x1="0" y1="0" x2="0" y2="14" stroke={tint} strokeWidth="6" strokeOpacity="0.10" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={"url(#" + id + ")"} />
      </svg>
      <span className="prod-img-tag" style={{ color: tint }}>{label || "product shot"}</span>
    </div>
  );
}

/* ---------- Botón ---------- */
function Button({ children, onClick, variant = "primary", size = "md", icon, iconRight, full, disabled, type }) {
  const cls = ["btn", "btn-" + variant, "btn-" + size];
  if (full) cls.push("btn-full");
  return (
    <button type={type || "button"} className={cls.join(" ")} onClick={onClick} disabled={disabled}>
      {icon && <Icon name={icon} size={size === "lg" ? 20 : 17} />}
      {children && <span>{children}</span>}
      {iconRight && <Icon name={iconRight} size={size === "lg" ? 20 : 17} />}
    </button>
  );
}

/* ---------- Badge / Pill ---------- */
function Badge({ children, tone = "neutral", icon }) {
  return (
    <span className={"badge badge-" + tone}>
      {icon && <Icon name={icon} size={13} stroke={2} />}
      {children}
    </span>
  );
}

/* ---------- Indicador de stock ---------- */
function StockDot({ prod }) {
  let tone = "ok", label = "En stock";
  if (prod.stock === 0) { tone = "out"; label = "Sin stock"; }
  else if (prod.stock <= prod.embalaje * 4) { tone = "low"; label = "Stock bajo"; }
  return (
    <span className={"stockdot stockdot-" + tone}>
      <span className="stockdot-dot" />
      {label} · <span className="mono">{prod.stock.toLocaleString("es-CL")}</span> u.
    </span>
  );
}

/* ---------- Stepper de cajas (paso = embalaje) ---------- */
function CajaStepper({ cajas, setCajas, max, size = "md" }) {
  const dec = () => setCajas(Math.max(1, cajas - 1));
  const inc = () => setCajas(Math.min(max, cajas + 1));
  return (
    <div className={"stepper stepper-" + size}>
      <button onClick={dec} disabled={cajas <= 1} aria-label="menos"><Icon name="minus" size={16} /></button>
      <div className="stepper-val">
        <span className="mono">{cajas}</span>
        <small>{cajas === 1 ? "caja" : "cajas"}</small>
      </div>
      <button onClick={inc} disabled={cajas >= max} aria-label="más"><Icon name="plus" size={16} /></button>
    </div>
  );
}

/* ---------- Logo / wordmark ---------- */
function Logo({ onClick, compact, onLight }) {
  return (
    <button className={"logo" + (onLight ? " logo-onlight" : "")} onClick={onClick} aria-label="Inicio">
      <span className="logo-mark"><img src="assets/logo-clean.png" alt="Trade Global Solutions" /></span>
      {!compact && (
        <span className="logo-text">
          <strong>Trade Global</strong>
          <small>Solutions · Mayorista</small>
        </span>
      )}
    </button>
  );
}

Object.assign(window, {
  Icon, ProductImage, Button, Badge, StockDot, CajaStepper, Logo,
});
