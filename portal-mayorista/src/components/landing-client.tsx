"use client";

import Link from "next/link";
import Image from "next/image";
import { motion, useReducedMotion, useInView, animate } from "framer-motion";
import { useEffect, useRef, useState } from "react";

type Featured = { nombre: string; img: string; grupo: string };
type Cat = { nombre: string; img: string | null };

// ponytail: el optimizador de Vercel puede dar 502 en la 1ª carga (cache frío).
// Si una foto de catálogo falla, la ocultamos y queda el fondo de marca, sin ícono roto.
function Pic(props: React.ComponentProps<typeof Image>) {
  const [bad, setBad] = useState(false);
  if (bad) return null;
  return <Image {...props} onError={() => setBad(true)} />;
}

function Ico({ d }: { d: string }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d={d} />
    </svg>
  );
}
const ICON = {
  tag: "M20 13l-7 7-9-9V4h7l9 9zM7.5 7.5h.01",
  bolt: "M13 2L3 14h7l-1 8 10-12h-7l1-8z",
  truck: "M3 7h11v8H3zM14 10h4l3 3v2h-7zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM17.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z",
  doc: "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M9 13h6M9 17h6",
  arrow: "M5 12h14M13 6l6 6-6 6",
  shield: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z M9 12l2 2 4-4",
  star: "M12 3l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 17.8 6.8 19.4l1-5.8L3.5 9.5l5.9-.9z",
};

const BENEFICIOS = [
  { i: ICON.tag, t: "Precios por volumen", d: "Tramos escalonados: mientras más compras, mejor precio. Pensado para revendedores." },
  { i: ICON.bolt, t: "Stock en tiempo real", d: "Disponibilidad actualizada a diario. Compras sobre lo que de verdad hay en bodega." },
  { i: ICON.truck, t: "Despacho a todo Chile", d: "Recibe donde estés, con seguimiento del pedido de principio a fin." },
  { i: ICON.doc, t: "Facturación disponible", d: "Documentación tributaria lista para la contabilidad de tu empresa." },
];
const PASOS = [
  { t: "Regístrate gratis", d: "Crea tu cuenta de empresa en minutos. Sin costo de membresía." },
  { t: "Aprobamos tu cuenta", d: "Validamos tu negocio y habilitamos los precios mayoristas." },
  { t: "Compra al por mayor", d: "Accede al catálogo completo con precios por volumen y pide." },
];
const STATS = [
  { n: 150, suf: "+", l: "Productos seleccionados" },
  { n: 9, suf: "", l: "Categorías" },
  { n: 100, suf: "%", l: "Despacho nacional" },
  { n: 0, suf: "$", pre: true, l: "Costo de membresía" },
];

function Counter({ to, suf = "", pre = false }: { to: number; suf?: string; pre?: boolean }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  const reduce = useReducedMotion();
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!inView) return;
    if (reduce) { setV(to); return; }
    const c = animate(0, to, { duration: 1.2, ease: "easeOut", onUpdate: (x) => setV(Math.round(x)) });
    return () => c.stop();
  }, [inView, to, reduce]);
  return <span ref={ref}>{pre ? suf : ""}{v}{!pre ? suf : ""}</span>;
}

const fadeUp = { hidden: { opacity: 0, y: 26 }, show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] as const } } };
const reveal = { hidden: { opacity: 0, y: 34 }, show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const } } };

export default function LandingClient({ productos, categorias }: { productos: Featured[]; categorias: Cat[] }) {
  const reduce = useReducedMotion();
  const hero = productos.slice(0, 5);
  const loop = productos.length >= 8 ? [...productos, ...productos] : [];

  return (
    <main className="lp">
      {/* NAV */}
      <header className="lp-nav">
        <div className="lp-wrap lp-nav__in">
          <Link href="/" className="lp-brand" aria-label="Comercial Solutions inicio">
            <Image src="/logo-clean.png" alt="Comercial Solutions" width={36} height={36} className="lp-brand__img" />
            <span className="lp-brand__txt"><strong>Comercial Solutions</strong><small>Portal Mayorista</small></span>
          </Link>
          <nav className="lp-nav__act">
            <Link href="/login" className="lp-btn lp-btn--ghost">Iniciar sesión</Link>
            <Link href="/registro" className="lp-btn lp-btn--primary">Registrarse</Link>
          </nav>
        </div>
      </header>

      {/* HERO */}
      <section className="lp-hero">
        <div className="lp-hero__bg" aria-hidden>
          <span className="lp-aurora lp-aurora--1" /><span className="lp-aurora lp-aurora--2" /><span className="lp-grid" />
        </div>
        <div className="lp-wrap lp-hero__in">
          <motion.div className="lp-hero__copy" initial="hidden" animate="show" variants={{ show: { transition: { staggerChildren: 0.08 } } }}>
            <motion.span className="lp-eyebrow" variants={fadeUp}><span className="lp-dot" /> Mayorista B2B · Despacho a todo Chile</motion.span>
            <motion.h1 className="lp-h1" variants={fadeUp}>El mayorista de <span className="lp-grad">todo</span><br />para tu negocio</motion.h1>
            <motion.p className="lp-lead" variants={fadeUp}>
              Miles de productos con precios por volumen y stock real. Tecnología, herramientas, hogar, salud, mascotas y mucho más — en una sola plataforma.
            </motion.p>
            <motion.div className="lp-hero__cta" variants={fadeUp}>
              <Link href="/registro" className="lp-btn lp-btn--primary lp-btn--lg">Crear cuenta gratis <Ico d={ICON.arrow} /></Link>
              <Link href="/login" className="lp-btn lp-btn--glass lp-btn--lg">Ya tengo cuenta</Link>
            </motion.div>
            <motion.div className="lp-stats" variants={fadeUp}>
              {STATS.map((s) => (
                <div key={s.l} className="lp-stat">
                  <span className="lp-stat__n"><Counter to={s.n} suf={s.suf} pre={s.pre} /></span>
                  <span className="lp-stat__l">{s.l}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {hero.length >= 4 && (
            <motion.div className="lp-cluster" initial={{ opacity: 0, scale: 0.92 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }} aria-hidden>
              {hero.map((p, i) => (
                <motion.div key={i} className={`lp-pcard lp-pcard--${i}`}
                  animate={reduce ? {} : { y: [0, i % 2 ? 12 : -12, 0] }}
                  transition={{ duration: 4 + i, repeat: Infinity, ease: "easeInOut", delay: i * 0.3 }}>
                  <Pic src={p.img} alt="" fill sizes="220px" className="lp-pcard__img" />
                  <span className="lp-pcard__tag">Precio mayorista</span>
                </motion.div>
              ))}
              <span className="lp-cluster__glow" />
            </motion.div>
          )}
        </div>
      </section>

      {/* MARQUEE de productos reales */}
      {loop.length > 0 && (
        <section className="lp-marquee-sec">
          <div className="lp-marquee">
            <div className="lp-marquee__track">
              {loop.map((p, i) => (
                <div className="lp-mitem" key={i}><Pic src={p.img} alt={p.nombre} fill sizes="120px" className="lp-mitem__img" /></div>
              ))}
            </div>
          </div>
          <div className="lp-marquee lp-marquee--rev">
            <div className="lp-marquee__track">
              {loop.slice().reverse().map((p, i) => (
                <div className="lp-mitem" key={i}><Pic src={p.img} alt={p.nombre} fill sizes="120px" className="lp-mitem__img" /></div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* BENEFICIOS */}
      <section className="lp-sec">
        <div className="lp-wrap">
          <Head eyebrow="Ventajas" title="Por qué comprar con nosotros" sub="Una operación mayorista pensada para hacer crecer tu negocio." />
          <motion.div className="lp-grid4" initial="hidden" whileInView="show" viewport={{ once: true, margin: "-80px" }} variants={{ show: { transition: { staggerChildren: 0.08 } } }}>
            {BENEFICIOS.map((b) => (
              <motion.article key={b.t} className="lp-card" variants={fadeUp} whileHover={{ y: -6 }}>
                <span className="lp-ic"><Ico d={b.i} /></span>
                <h3 className="lp-card__t">{b.t}</h3>
                <p className="lp-card__d">{b.d}</p>
              </motion.article>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CATEGORÍAS — bento con imágenes */}
      <section className="lp-sec lp-sec--tint">
        <div className="lp-wrap">
          <Head eyebrow="Catálogo" title="Explora por categoría" sub="Un catálogo amplio para abastecer cualquier rubro." />
          <motion.div className="lp-bento" initial="hidden" whileInView="show" viewport={{ once: true, margin: "-60px" }} variants={{ show: { transition: { staggerChildren: 0.05 } } }}>
            {categorias.map((c, i) => (
              <motion.div key={c.nombre} variants={fadeUp} className={`lp-bento__cellwrap lp-bento__cellwrap--${i}`} whileHover={{ y: -5 }}>
                <Link href="/registro" className="lp-bcell">
                  {c.img ? <Pic src={c.img} alt="" fill sizes="(max-width:700px) 50vw, 360px" className="lp-bcell__img" /> : <span className="lp-bcell__ph" />}
                  <span className="lp-bcell__ov" />
                  <span className="lp-bcell__name">{c.nombre}<Ico d={ICON.arrow} /></span>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CÓMO FUNCIONA */}
      <section className="lp-sec">
        <div className="lp-wrap">
          <Head eyebrow="Simple" title="Cómo funciona" sub="En tres pasos empiezas a comprar al por mayor." />
          <div className="lp-steps">
            <span className="lp-steps__line" aria-hidden />
            {PASOS.map((p, i) => (
              <motion.article key={p.t} className="lp-step" variants={reveal} initial="hidden" whileInView="show" viewport={{ once: true, margin: "-80px" }} transition={{ delay: i * 0.12 }}>
                <span className="lp-step__n">{i + 1}</span>
                <h3 className="lp-card__t">{p.t}</h3>
                <p className="lp-card__d">{p.d}</p>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* TRUST */}
      <section className="lp-trust">
        <div className="lp-wrap lp-trust__in">
          {[
            { i: ICON.shield, t: "Compra segura", d: "Validación de cuentas y operación formal con factura." },
            { i: ICON.bolt, t: "Stock confiable", d: "Inventario sincronizado a diario, sin sorpresas." },
            { i: ICON.truck, t: "Cobertura nacional", d: "Despachamos a todo Chile con seguimiento." },
          ].map((t, i) => (
            <motion.div key={t.t} className="lp-trust__item" variants={reveal} initial="hidden" whileInView="show" viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <span className="lp-trust__ic"><Ico d={t.i} /></span>
              <div><strong>{t.t}</strong><p>{t.d}</p></div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="lp-cta">
        <span className="lp-cta__glow" aria-hidden />
        <motion.div className="lp-wrap lp-cta__in" variants={reveal} initial="hidden" whileInView="show" viewport={{ once: true }}>
          <h2 className="lp-cta__h">Empieza a comprar al por mayor hoy</h2>
          <p className="lp-cta__p">Crea tu cuenta de empresa gratis y desbloquea los precios mayoristas.</p>
          <Link href="/registro" className="lp-btn lp-btn--white lp-btn--lg">Crear cuenta gratis <Ico d={ICON.arrow} /></Link>
        </motion.div>
      </section>

      {/* FOOTER */}
      <footer className="lp-foot">
        <div className="lp-wrap lp-foot__in">
          <span>© 2026 Trade Global Solutions SpA · Comercial Solutions</span>
          <span className="lp-foot__lk"><Link href="/login">Iniciar sesión</Link><Link href="/registro">Registrarse</Link></span>
        </div>
      </footer>

      <style>{CSS}</style>
    </main>
  );
}

function Head({ eyebrow, title, sub }: { eyebrow: string; title: string; sub: string }) {
  return (
    <motion.div className="lp-head" variants={reveal} initial="hidden" whileInView="show" viewport={{ once: true, margin: "-60px" }}>
      <span className="lp-head__e">{eyebrow}</span>
      <h2 className="lp-h2">{title}</h2>
      <p className="lp-sub">{sub}</p>
    </motion.div>
  );
}

const CSS = `
.lp{--brand:#0e7cc4;--accent:#0369a1;--navy:#0b2238;--ink:#0f172a;--ink2:#475569;--line:#e6ecf3;--bg:#f6f9fc;
  font-family:var(--font-source),system-ui,sans-serif;color:var(--ink);background:#fff;-webkit-font-smoothing:antialiased;overflow-x:hidden;}
.lp h1,.lp h2,.lp h3,.lp strong{font-family:var(--font-lexend),system-ui,sans-serif;}
.lp a{text-decoration:none;}
.lp-wrap{max-width:1180px;margin:0 auto;padding:0 24px;}
.lp-nav{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.82);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);}
.lp-nav__in{display:flex;align-items:center;justify-content:space-between;height:68px;}
.lp-brand{display:flex;align-items:center;gap:11px;color:var(--ink);}
.lp-brand__img{border-radius:50%;}
.lp-brand__txt{display:flex;flex-direction:column;line-height:1.04;}
.lp-brand__txt strong{font-size:15px;font-weight:700;}.lp-brand__txt small{font-size:11px;color:var(--ink2);font-weight:600;}
.lp-nav__act{display:flex;gap:10px;}
.lp-btn{display:inline-flex;align-items:center;gap:8px;justify-content:center;font-weight:600;font-size:14.5px;font-family:var(--font-lexend);
  padding:10px 18px;border-radius:12px;border:1px solid transparent;cursor:pointer;white-space:nowrap;transition:transform .15s,background .2s,box-shadow .2s,border-color .2s;}
.lp-btn svg{width:18px;height:18px;}
.lp-btn--lg{padding:15px 26px;font-size:15.5px;}
.lp-btn--primary{background:linear-gradient(180deg,#15a0e8,#0e7cc4);color:#fff;box-shadow:0 12px 28px -10px rgba(14,124,196,.75);}
.lp-btn--primary:hover{transform:translateY(-2px);box-shadow:0 18px 34px -12px rgba(20,160,232,.85);}
.lp-btn--ghost{background:#fff;color:var(--ink);border-color:var(--line);}
.lp-btn--ghost:hover{border-color:#cbd8e6;background:#f8fbfe;}
.lp-btn--glass{background:rgba(255,255,255,.1);color:#fff;border-color:rgba(255,255,255,.3);backdrop-filter:blur(6px);}
.lp-btn--glass:hover{background:rgba(255,255,255,.2);transform:translateY(-2px);}
.lp-btn--white{background:#fff;color:var(--navy);}
.lp-btn--white:hover{transform:translateY(-2px);box-shadow:0 14px 30px -12px rgba(0,0,0,.4);}
/* HERO */
.lp-hero{position:relative;overflow:hidden;background:radial-gradient(120% 90% at 80% 0%,#0e3a5e 0%,#0a2236 45%,#06182a 100%);color:#fff;}
.lp-hero__bg{position:absolute;inset:0;pointer-events:none;}
.lp-aurora{position:absolute;border-radius:50%;filter:blur(60px);opacity:.55;}
.lp-aurora--1{width:620px;height:520px;top:-160px;right:-80px;background:radial-gradient(circle,#1f9cf0,transparent 62%);}
.lp-aurora--2{width:520px;height:480px;bottom:-200px;left:-120px;background:radial-gradient(circle,#0e7cc4,transparent 60%);opacity:.4;}
.lp-grid{position:absolute;inset:0;opacity:.4;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:48px 48px;mask-image:radial-gradient(circle at 30% 30%,#000 30%,transparent 75%);}
.lp-hero__in{position:relative;display:grid;grid-template-columns:1.05fr .95fr;align-items:center;gap:40px;padding:80px 24px 92px;}
.lp-eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;font-weight:600;letter-spacing:.03em;color:#bfe3fb;background:rgba(110,201,247,.1);border:1px solid rgba(110,201,247,.24);padding:7px 15px;border-radius:999px;}
.lp-dot{width:7px;height:7px;border-radius:50%;background:#3fb6f5;box-shadow:0 0 0 3px rgba(63,182,245,.25);}
.lp-h1{font-size:clamp(40px,5.6vw,66px);font-weight:800;line-height:1.02;letter-spacing:-.03em;margin:20px 0 18px;}
.lp-grad{background:linear-gradient(100deg,#6ec9f7,#aee2ff);-webkit-background-clip:text;background-clip:text;color:transparent;}
.lp-lead{font-size:clamp(16px,1.5vw,18.5px);line-height:1.6;color:rgba(255,255,255,.8);margin:0;max-width:520px;}
.lp-hero__cta{display:flex;gap:12px;flex-wrap:wrap;margin:32px 0 0;}
.lp-stats{display:grid;grid-template-columns:repeat(4,auto);gap:30px;margin-top:42px;padding-top:30px;border-top:1px solid rgba(255,255,255,.1);}
.lp-stat{display:flex;flex-direction:column;gap:3px;}
.lp-stat__n{font-family:var(--font-lexend);font-size:30px;font-weight:800;letter-spacing:-.02em;}
.lp-stat__l{font-size:12px;color:rgba(255,255,255,.6);}
/* cluster de productos flotantes */
.lp-cluster{position:relative;height:480px;}
.lp-cluster__glow{position:absolute;inset:10% 14%;background:radial-gradient(circle,rgba(31,156,240,.4),transparent 65%);filter:blur(40px);z-index:0;}
.lp-pcard{position:absolute;border-radius:20px;overflow:hidden;background:#0c2438;border:1px solid rgba(255,255,255,.14);
  box-shadow:0 30px 60px -24px rgba(0,0,0,.7);z-index:1;}
.lp-pcard__img{object-fit:cover;}
.lp-pcard__tag{position:absolute;left:10px;bottom:10px;font-family:var(--font-lexend);font-size:10.5px;font-weight:600;color:#06182a;
  background:rgba(255,255,255,.92);padding:4px 9px;border-radius:999px;}
.lp-pcard--0{width:230px;height:230px;top:6%;left:30%;z-index:3;}
.lp-pcard--1{width:160px;height:160px;top:0;left:2%;}
.lp-pcard--2{width:150px;height:150px;top:50%;left:0;}
.lp-pcard--3{width:185px;height:185px;top:54%;left:38%;z-index:2;}
.lp-pcard--4{width:140px;height:140px;top:20%;right:2%;}
/* MARQUEE */
.lp-marquee-sec{background:#06182a;padding:26px 0;overflow:hidden;display:flex;flex-direction:column;gap:16px;}
.lp-marquee{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);}
.lp-marquee__track{display:flex;gap:16px;width:max-content;animation:lp-scroll 48s linear infinite;}
.lp-marquee--rev .lp-marquee__track{animation-direction:reverse;animation-duration:56s;}
.lp-marquee:hover .lp-marquee__track{animation-play-state:paused;}
.lp-mitem{position:relative;width:108px;height:108px;flex:0 0 auto;border-radius:16px;overflow:hidden;background:#0c2438;border:1px solid rgba(255,255,255,.08);}
.lp-mitem__img{object-fit:cover;}
@keyframes lp-scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
/* SECCIONES */
.lp-sec{padding:88px 0;}
.lp-sec--tint{background:var(--bg);border-block:1px solid var(--line);}
.lp-head{text-align:center;max-width:640px;margin:0 auto 46px;}
.lp-head__e{display:inline-block;font-size:12.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--brand);margin-bottom:10px;}
.lp-h2{font-size:clamp(28px,3.8vw,40px);font-weight:800;letter-spacing:-.03em;margin:0 0 10px;}
.lp-sub{color:var(--ink2);font-size:16.5px;margin:0;line-height:1.5;}
.lp-grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;}
.lp-card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px;box-shadow:0 1px 2px rgba(16,40,70,.04);transition:box-shadow .25s,border-color .25s;}
.lp-card:hover{box-shadow:0 26px 50px -28px rgba(11,34,56,.45);border-color:#d4e2f0;}
.lp-ic{display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:14px;background:linear-gradient(160deg,#e8f4fd,#d4ecfb);color:var(--accent);margin-bottom:16px;}
.lp-card__t{font-size:17px;font-weight:700;margin:0 0 7px;letter-spacing:-.01em;}
.lp-card__d{font-size:14px;line-height:1.6;color:var(--ink2);margin:0;}
/* BENTO */
.lp-bento{display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:170px;gap:16px;}
.lp-bento__cellwrap{min-height:0;}
.lp-bento__cellwrap--0{grid-column:span 2;grid-row:span 2;}
.lp-bento__cellwrap--3{grid-row:span 2;}
.lp-bento__cellwrap--6{grid-column:span 2;}
.lp-bcell{position:relative;display:block;width:100%;height:100%;border-radius:20px;overflow:hidden;border:1px solid var(--line);background:linear-gradient(160deg,#0e3a5e,#06182a);}
.lp-bcell__img{object-fit:cover;transition:transform .5s ease;}
.lp-bcell:hover .lp-bcell__img{transform:scale(1.07);}
.lp-bcell__ph{position:absolute;inset:0;background:linear-gradient(160deg,#0e3a5e,#06182a);}
.lp-bcell__ov{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,24,42,.05) 30%,rgba(6,24,42,.82));}
.lp-bcell__name{position:absolute;left:16px;bottom:14px;right:16px;display:flex;align-items:center;justify-content:space-between;gap:8px;
  color:#fff;font-family:var(--font-lexend);font-weight:700;font-size:16px;letter-spacing:-.01em;}
.lp-bcell__name svg{width:18px;height:18px;opacity:.85;transition:transform .25s;}
.lp-bcell:hover .lp-bcell__name svg{transform:translateX(4px);}
/* PASOS */
.lp-steps{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:20px;}
.lp-steps__line{position:absolute;top:42px;left:16%;right:16%;height:2px;background:linear-gradient(90deg,transparent,var(--line),transparent);}
.lp-step{position:relative;background:#fff;border:1px solid var(--line);border-radius:20px;padding:30px 24px;text-align:center;}
.lp-step__n{display:inline-flex;align-items:center;justify-content:center;width:50px;height:50px;border-radius:50%;background:linear-gradient(180deg,#15a0e8,#0e7cc4);color:#fff;font-family:var(--font-lexend);font-weight:800;font-size:19px;margin-bottom:16px;box-shadow:0 12px 24px -10px rgba(14,124,196,.75);}
/* TRUST */
.lp-trust{background:radial-gradient(120% 100% at 50% 0%,#0e3a5e,#06182a);color:#fff;padding:52px 0;}
.lp-trust__in{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;}
.lp-trust__item{display:flex;gap:14px;align-items:flex-start;}
.lp-trust__ic{display:inline-flex;align-items:center;justify-content:center;width:46px;height:46px;border-radius:13px;flex-shrink:0;background:rgba(110,201,247,.13);color:#6ec9f7;border:1px solid rgba(110,201,247,.2);}
.lp-trust__item strong{font-size:16px;font-weight:700;display:block;margin-bottom:3px;}
.lp-trust__item p{font-size:13.5px;color:rgba(255,255,255,.66);margin:0;line-height:1.5;}
/* CTA */
.lp-cta{position:relative;overflow:hidden;background:linear-gradient(135deg,#0e7cc4,#072e4d 85%);color:#fff;}
.lp-cta__glow{position:absolute;top:-160px;left:50%;transform:translateX(-50%);width:700px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(110,201,247,.4),transparent 65%);filter:blur(30px);}
.lp-cta__in{position:relative;padding:84px 24px;text-align:center;}
.lp-cta__h{font-size:clamp(28px,4vw,42px);font-weight:800;letter-spacing:-.03em;margin:0 0 12px;}
.lp-cta__p{font-size:17px;color:rgba(255,255,255,.85);margin:0 0 28px;}
.lp-foot{border-top:1px solid var(--line);background:#fafcfe;}
.lp-foot__in{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:26px 24px;font-size:13.5px;color:var(--ink2);flex-wrap:wrap;}
.lp-foot__lk{display:flex;gap:20px;}.lp-foot__lk a{color:var(--ink2);}.lp-foot__lk a:hover{color:var(--brand);}
/* RESPONSIVE */
@media(max-width:920px){
  .lp-hero__in{grid-template-columns:1fr;}
  /* En móvil el cluster absoluto no cabe: lo mostramos como grilla 2×2 (sigue flotando). */
  .lp-cluster{display:grid !important;position:relative;height:auto;grid-template-columns:1fr 1fr;gap:12px;max-width:340px;margin:10px auto 0;}
  .lp-pcard{position:static !important;width:auto !important;height:auto !important;aspect-ratio:1;}
  .lp-pcard--4{display:none;}
  .lp-cluster__glow{display:none;}
  .lp-grid4{grid-template-columns:repeat(2,1fr);}.lp-steps{grid-template-columns:1fr;}.lp-steps__line{display:none;}.lp-trust__in{grid-template-columns:1fr;}
  .lp-bento{grid-template-columns:repeat(2,1fr);grid-auto-rows:150px;}
  .lp-bento__cellwrap--0,.lp-bento__cellwrap--6{grid-column:span 2;}.lp-bento__cellwrap--0{grid-row:span 1;}.lp-bento__cellwrap--3{grid-row:span 1;}
}
@media(max-width:560px){
  .lp-grid4{grid-template-columns:1fr;}.lp-stats{grid-template-columns:repeat(2,auto);gap:18px 26px;}
  .lp-nav__act .lp-btn--ghost{display:none;}.lp-hero__in{padding:60px 22px 70px;}.lp-bento{grid-template-columns:1fr;}
  .lp-bento__cellwrap--0,.lp-bento__cellwrap--6{grid-column:span 1;}
}
@media(prefers-reduced-motion:reduce){.lp-marquee__track{animation:none!important;}.lp *{transition:none!important;}}
`;
