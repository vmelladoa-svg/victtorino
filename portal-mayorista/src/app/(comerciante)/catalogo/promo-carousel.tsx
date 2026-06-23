"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";

/* ─────────────────────────────────────────────────────────────
   Carrusel promocional del catálogo — estética marketplace (3 láminas).
   Hi-fi según handoff "Header Carrusel Promocional".
   Para poner foto real por lámina: agrega `foto: "/ruta.jpg"` al slide
   (reemplaza el placeholder con icono). Los badges siguen por encima.
   ───────────────────────────────────────────────────────────── */

const SORA = "var(--font-sora), 'Sora', system-ui, sans-serif";
const MANROPE = "var(--font-manrope), 'Manrope', system-ui, sans-serif";

/* Iconos inline (sustituibles por lucide-react si se adopta) */
const Bolt = ({ c = "#FFD400", s = 14 }: { c?: string; s?: number }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill={c} aria-hidden>
    <path d="M13 2 4 14h6l-1 8 9-12h-6z" />
  </svg>
);
const Truck = ({ c = "#15A05A", s = 16 }: { c?: string; s?: number }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={2}
    strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M1 3h15v13H1zM16 8h4l3 3v5h-7z" />
    <circle cx="5.5" cy="18.5" r="1.8" /><circle cx="18.5" cy="18.5" r="1.8" />
  </svg>
);
const Box = ({ c = "currentColor", s = 16 }: { c?: string; s?: number }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={2}
    strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M21 8 12 3 3 8v8l9 5 9-5z" /><path d="M3 8l9 5 9-5M12 13v8" />
  </svg>
);
const Check = ({ c = "#15A05A", s = 16 }: { c?: string; s?: number }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={3}
    strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M20 6 9 17l-5-5" />
  </svg>
);

type Slide = {
  bg: string;
  dots: string; // color patrón de puntos
  circles: [string, string]; // colores de los 2 círculos decorativos
  reverse?: boolean; // visual a la izquierda
  pill: { bg: string; color: string; icon: ReactNode; text: string };
  text: ReactNode;
  para: ReactNode;
  cta: { label: string; bg: string; color: string; glow: string; href: string };
  aside?: ReactNode; // texto/chip al lado del CTA
  card: { bg: string; rotate: number; icon?: ReactNode; foto?: string };
  badges: ReactNode; // badges/chips flotantes sobre la tarjeta (z-index alto)
};

const SLIDES: Slide[] = [
  {
    bg: "radial-gradient(120% 130% at 80% 0%, #3a82e0 0%, #2461bd 45%, #16438c 100%)",
    dots: "rgba(255,255,255,.16)",
    circles: ["rgba(255,255,255,.07)", "rgba(255,255,255,.05)"],
    pill: { bg: "rgba(255,255,255,.16)", color: "#fff", icon: <Bolt />, text: "PORTAL MAYORISTA B2B" },
    text: (
      <>
        <span style={{ fontFamily: MANROPE, fontWeight: 600, fontSize: 26, color: "#cfe0ff" }}>
          Compra por caja y ahorra
        </span>
        <span style={{ display: "flex", alignItems: "flex-end", gap: 12, lineHeight: 0.85 }}>
          <span style={{ fontFamily: SORA, fontWeight: 800, fontSize: 92, color: "#FFD400" }}>40%</span>
          <span style={{ fontFamily: SORA, fontWeight: 800, fontSize: 46, color: "#fff", paddingBottom: 6 }}>OFF</span>
        </span>
      </>
    ),
    para: "Precios escalonados según tu volumen. Mientras más llevas, mejor pagas.",
    cta: { label: "Ver precios mayoristas", bg: "#FFD400", color: "#143a72", glow: "rgba(255,212,0,.35)", href: "/catalogo" },
    aside: (
      <span style={{ display: "flex", alignItems: "center", gap: 8, color: "#cfe0ff", fontSize: 14, fontWeight: 600 }}>
        <Box c="#cfe0ff" s={18} /> +5.000 productos importados
      </span>
    ),
    card: { bg: "linear-gradient(160deg,#fff,#e7eefc)", rotate: -4, foto: "/banner/slide1.jpg" },
    badges: (
      <>
        <div style={{
          position: "absolute", top: -18, right: -14, width: 96, height: 96, borderRadius: "50%",
          background: "#FF3B5C", border: "3px dashed rgba(255,255,255,.55)", transform: "rotate(10deg)",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
          color: "#fff", boxShadow: "0 8px 20px rgba(255,59,92,.45)", zIndex: 3,
        }}>
          <span style={{ fontFamily: SORA, fontWeight: 800, fontSize: 24 }}>-40%</span>
          <span style={{ fontFamily: MANROPE, fontWeight: 700, fontSize: 10, letterSpacing: ".08em" }}>POR CAJA</span>
        </div>
        <div style={{
          position: "absolute", bottom: -16, left: "50%", transform: "translateX(-60%)",
          background: "#fff", color: "#143a72", borderRadius: 99, padding: "9px 16px",
          display: "flex", alignItems: "center", gap: 8, fontFamily: MANROPE, fontWeight: 700, fontSize: 13,
          boxShadow: "0 8px 20px rgba(0,0,0,.18)", whiteSpace: "nowrap", zIndex: 3,
        }}>
          <Truck /> Despacho a todo Chile
        </div>
      </>
    ),
  },
  {
    bg: "radial-gradient(120% 130% at 20% 0%, #ffe24d 0%, #FFD400 45%, #f5c100 100%)",
    dots: "rgba(20,58,114,.10)",
    circles: ["rgba(255,255,255,.30)", "rgba(20,58,114,.06)"],
    reverse: true,
    pill: { bg: "#143a72", color: "#FFD400", icon: <Truck c="#FFD400" />, text: "LOGÍSTICA" },
    text: (
      <span style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 12, lineHeight: 0.95 }}>
        <span style={{ fontFamily: SORA, fontWeight: 800, fontSize: 64, color: "#143a72" }}>Despacho gratis</span>
        <span style={{ fontFamily: MANROPE, fontWeight: 700, fontSize: 24, color: "#15A05A" }}>a todo Chile</span>
      </span>
    ),
    para: (
      <>
        En compras sobre <strong>$400.000</strong>. Con seguimiento completo, de la bodega a tu local.
      </>
    ),
    cta: { label: "Calcular mi despacho", bg: "#143a72", color: "#fff", glow: "rgba(20,58,114,.3)", href: "/catalogo" },
    card: { bg: "linear-gradient(160deg,#fff,#eaf0fb)", rotate: 4, foto: "/banner/slide2.jpg" },
    badges: (
      <div style={{
        position: "absolute", top: -22, right: -10, width: 104, height: 104, borderRadius: "50%",
        background: "#15A05A", transform: "rotate(-8deg)", display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", color: "#fff",
        boxShadow: "0 10px 24px rgba(21,160,90,.45)", zIndex: 3,
      }}>
        <span style={{ fontFamily: SORA, fontWeight: 800, fontSize: 24 }}>GRATIS</span>
        <span style={{ fontFamily: MANROPE, fontWeight: 700, fontSize: 11, letterSpacing: ".1em" }}>ENVÍO</span>
      </div>
    ),
  },
  {
    bg: "radial-gradient(120% 130% at 80% 0%, #1cb568 0%, #15A05A 45%, #0c7541 100%)",
    dots: "rgba(255,255,255,.16)",
    circles: ["rgba(255,255,255,.08)", "rgba(255,255,255,.05)"],
    pill: { bg: "rgba(255,255,255,.16)", color: "#fff", icon: <Box c="#fff" />, text: "IMPORTACIÓN DIRECTA" },
    text: (
      <>
        <span style={{ fontFamily: MANROPE, fontWeight: 600, fontSize: 26, color: "#d6f3e3" }}>
          Productos importados con
        </span>
        <span style={{ fontFamily: SORA, fontWeight: 800, fontSize: 62, color: "#fff", lineHeight: 0.95 }}>Stock real</span>
        <span style={{ fontFamily: SORA, fontWeight: 800, fontSize: 62, color: "#FFD400", lineHeight: 0.95 }}>por caja</span>
      </>
    ),
    para: "Inventario en tiempo real. Compra por volumen sin sorpresas de quiebre de stock.",
    cta: { label: "Explorar importados", bg: "#FFD400", color: "#0c7541", glow: "rgba(255,212,0,.35)", href: "/catalogo" },
    aside: (
      <span style={{ display: "flex", alignItems: "center", gap: 8, color: "#d6f3e3", fontSize: 14, fontWeight: 600 }}>
        <span className="pc-pulse" /> Stock actualizado hoy
      </span>
    ),
    card: { bg: "linear-gradient(160deg,#fff,#e7f6ee)", rotate: 4, foto: "/banner/slide3.jpg" },
    badges: (
      <>
        <div style={{
          position: "absolute", top: -16, right: -10, background: "#FFD400", color: "#0c7541",
          borderRadius: 10, padding: "8px 14px", transform: "rotate(6deg)",
          display: "flex", alignItems: "center", gap: 6, fontFamily: MANROPE, fontWeight: 800, fontSize: 14,
          boxShadow: "0 8px 20px rgba(0,0,0,.2)", zIndex: 3,
        }}>
          <Bolt c="#0c7541" /> NUEVO
        </div>
        <div style={{
          position: "absolute", bottom: -16, left: "50%", transform: "translateX(-60%)",
          background: "#fff", color: "#143a72", borderRadius: 99, padding: "9px 16px",
          display: "flex", alignItems: "center", gap: 8, fontFamily: MANROPE, fontWeight: 700, fontSize: 13,
          boxShadow: "0 8px 20px rgba(0,0,0,.18)", whiteSpace: "nowrap", zIndex: 3,
        }}>
          <Check /> Factura disponible
        </div>
      </>
    ),
  },
];

export default function PromoCarousel() {
  const [i, setI] = useState(0);
  const n = SLIDES.length;
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const downX = useRef<number | null>(null);

  const restart = () => {
    if (timer.current) clearInterval(timer.current);
    if (n > 1) timer.current = setInterval(() => setI((x) => (x + 1) % n), 5000);
  };
  useEffect(() => {
    restart();
    return () => { if (timer.current) clearInterval(timer.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [n]);

  const go = (idx: number) => { setI(((idx % n) + n) % n); restart(); };
  const step = (d: number) => go(i + d);

  return (
    <div
      className="pc-root"
      onPointerDown={(e) => { downX.current = e.clientX; }}
      onPointerUp={(e) => {
        if (downX.current == null) return;
        const dx = e.clientX - downX.current;
        downX.current = null;
        if (Math.abs(dx) > 40) step(dx < 0 ? 1 : -1);
      }}
    >
      <style>{`
        .pc-root { position: relative; width: 100%; height: 470px; overflow: hidden;
          border-radius: var(--radius); margin-bottom: 24px; background: #1a4f9c;
          box-shadow: 0 12px 32px -16px rgba(8,62,98,.55); cursor: grab; user-select: none; }
        .pc-track { display: flex; height: 100%; transition: transform .6s cubic-bezier(.65,0,.2,1); }
        .pc-slide { flex: 0 0 100%; min-width: 100%; height: 100%; position: relative; overflow: hidden; }
        .pc-wrap { position: relative; z-index: 2; max-width: 1200px; margin: 0 auto;
          padding: 0 48px; height: 100%; display: flex; align-items: center; gap: 24px; }
        .pc-textcol { flex: 1; max-width: 560px; display: flex; flex-direction: column; gap: 16px; }
        .pc-viscol { flex: 0 0 360px; display: flex; align-items: center; justify-content: center; }
        .pc-card { position: relative; width: 300px; height: 300px; border-radius: 24px;
          overflow: visible; box-shadow: 0 20px 50px rgba(0,0,0,.25);
          display: flex; align-items: center; justify-content: center; }
        .pc-card-inner { position: absolute; inset: 0; border-radius: 24px; overflow: hidden;
          display: flex; align-items: center; justify-content: center; z-index: 1; }
        .pc-arrow { position: absolute; top: 50%; transform: translateY(-50%); z-index: 5;
          width: 46px; height: 46px; border-radius: 50%; border: none; background: rgba(255,255,255,.9);
          color: #143a72; font-size: 26px; line-height: 1; display: flex; align-items: center;
          justify-content: center; box-shadow: 0 6px 18px rgba(0,0,0,.2); cursor: pointer; }
        .pc-arrow:hover { background: #fff; }
        .pc-dots { position: absolute; bottom: 22px; left: 50%; transform: translateX(-50%);
          z-index: 5; display: flex; gap: 7px; }
        .pc-dot { height: 9px; border-radius: 99px; border: none; padding: 0; cursor: pointer;
          transition: all .35s; }
        .pc-pulse { width: 10px; height: 10px; border-radius: 50%; background: #7CFFB0;
          display: inline-block; box-shadow: 0 0 0 0 rgba(124,255,176,.7); animation: pcPulse 1.6s infinite; }
        @keyframes pcPulse { 0%{box-shadow:0 0 0 0 rgba(124,255,176,.6);} 70%{box-shadow:0 0 0 10px rgba(124,255,176,0);} 100%{box-shadow:0 0 0 0 rgba(124,255,176,0);} }
        @media (max-width: 720px) {
          .pc-root { height: 380px; }
          .pc-wrap { padding: 0 20px; }
          .pc-viscol { display: none; }
          .pc-textcol { max-width: 100%; }
          .pc-slide .pc-bignum { font-size: 64px !important; }
        }
      `}</style>

      <div className="pc-track" style={{ transform: `translateX(${-i * 100}%)` }}>
        {SLIDES.map((s, idx) => (
          <div key={idx} className="pc-slide" style={{ background: s.bg }}>
            {/* Capas decorativas */}
            <div style={{ position: "absolute", inset: 0, zIndex: 0,
              backgroundImage: `radial-gradient(${s.dots} 1.4px, transparent 1.4px)`,
              backgroundSize: "22px 22px", opacity: 0.4 }} />
            <div style={{ position: "absolute", top: -160, right: -120, width: 620, height: 620,
              borderRadius: "50%", background: s.circles[0], zIndex: 0 }} />
            <div style={{ position: "absolute", bottom: -120, left: "30%", width: 320, height: 320,
              borderRadius: "50%", background: s.circles[1], zIndex: 0 }} />

            <div className="pc-wrap" style={{ flexDirection: s.reverse ? "row-reverse" : "row" }}>
              {/* Columna de texto */}
              <div className="pc-textcol">
                <span style={{
                  alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 8,
                  background: s.pill.bg, color: s.pill.color, borderRadius: 99, padding: "7px 14px",
                  fontFamily: MANROPE, fontWeight: 700, fontSize: 12, letterSpacing: ".1em",
                }}>
                  {s.pill.icon} {s.pill.text}
                </span>

                <div className="pc-bignum" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {s.text}
                </div>

                <p style={{ fontFamily: MANROPE, fontSize: 17, lineHeight: 1.45, maxWidth: 420,
                  color: s.reverse ? "#3a4a63" : (idx === 0 ? "#cfe0ff" : "#d6f3e3") }}>
                  {s.para}
                </p>

                <div style={{ display: "flex", alignItems: "center", gap: 22, flexWrap: "wrap", marginTop: 4 }}>
                  <Link href={s.cta.href} style={{
                    background: s.cta.bg, color: s.cta.color, fontFamily: MANROPE, fontWeight: 800,
                    fontSize: 16, padding: "16px 30px", borderRadius: 9, textDecoration: "none",
                    boxShadow: `0 8px 20px ${s.cta.glow}`,
                  }}>
                    {s.cta.label}
                  </Link>
                  {s.aside}
                </div>
              </div>

              {/* Columna visual */}
              <div className="pc-viscol">
                <div className="pc-card" style={{ transform: `rotate(${s.card.rotate}deg)` }}>
                  <div className="pc-card-inner" style={{ background: s.card.bg }}>
                    {s.card.foto ? (
                      <Image src={s.card.foto} alt="" fill sizes="300px"
                        style={{ objectFit: "contain", padding: 10 }} unoptimized priority={idx === 0} />
                    ) : (
                      s.card.icon ?? <Box c="rgba(20,58,114,.25)" s={64} />
                    )}
                  </div>
                  {s.badges}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button className="pc-arrow" style={{ left: 18 }} aria-label="Anterior"
        onClick={(e) => { e.stopPropagation(); step(-1); }}>‹</button>
      <button className="pc-arrow" style={{ right: 18 }} aria-label="Siguiente"
        onClick={(e) => { e.stopPropagation(); step(1); }}>›</button>

      <div className="pc-dots">
        {SLIDES.map((_, idx) => (
          <button key={idx} className="pc-dot" aria-label={`Ir a lámina ${idx + 1}`}
            onClick={(e) => { e.stopPropagation(); go(idx); }}
            style={{ width: idx === i ? 26 : 9, background: idx === i ? "#fff" : "rgba(255,255,255,.45)" }} />
        ))}
      </div>
    </div>
  );
}
