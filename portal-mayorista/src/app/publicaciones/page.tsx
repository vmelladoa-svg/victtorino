/* eslint-disable @next/next/no-img-element */
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Publicaciones — Comercial Solutions",
  description:
    "Novedades, productos y ofertas mayoristas de Comercial Solutions. Venta por mayor con despacho a todo Chile.",
  alternates: { canonical: "https://comercialsolutions.cl/publicaciones" },
};

// ISR: refresca el feed cada 60s leyendo el JSON hospedado en okai.cl (server-side, sin CORS).
export const revalidate = 60;

type Post = {
  img?: string;
  caption?: string;
  hashtags?: string[];
  formato?: string;
  fecha?: string;
};

async function getPosts(): Promise<Post[]> {
  try {
    const r = await fetch("https://okai.cl/publicaciones-cs.json", {
      next: { revalidate: 60 },
    });
    if (!r.ok) return [];
    return (await r.json()) as Post[];
  } catch {
    return [];
  }
}

function fmtFecha(iso?: string) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleDateString("es-CL", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

export default async function PublicacionesPage() {
  const posts = await getPosts();
  return (
    <div className="pub">
      <style>{CSS}</style>

      <header className="pub-nav">
        <a href="/" className="pub-brand">
          Comercial Solutions
        </a>
        <a href="/registro" className="pub-cta">
          Crear cuenta gratis →
        </a>
      </header>

      <section className="pub-hero">
        <div className="pub-eyebrow">Novedades</div>
        <h1>Publicaciones</h1>
        <p>Productos, ofertas y novedades mayoristas — en un solo lugar.</p>
      </section>

      <main className="pub-feed">
        {posts.length === 0 ? (
          <div className="pub-empty">
            <div className="pub-big">🌱</div>
            Pronto publicaremos aquí. ¡Vuelve pronto!
          </div>
        ) : (
          posts.map((p, i) => (
            <article className="pub-post" key={i}>
              {p.img ? <img src={p.img} alt="" loading="lazy" /> : null}
              <div className="pub-body">
                <div className="pub-meta">
                  {p.formato ? <span className="pub-fmt">{p.formato}</span> : null}
                  <span className="pub-fecha">{fmtFecha(p.fecha)}</span>
                </div>
                <div className="pub-cap">{p.caption}</div>
                {p.hashtags && p.hashtags.length ? (
                  <div className="pub-tags">
                    {p.hashtags.map((h, j) => (
                      <span className="pub-tag" key={j}>
                        {h}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            </article>
          ))
        )}
      </main>

      <footer className="pub-foot">
        Comercial Solutions · Venta por mayor · comercialsolutions.cl
      </footer>
    </div>
  );
}

const CSS = `
.pub{background:var(--bg,#f3f6fa);color:var(--ink,#0f1b2a);min-height:100vh;font-family:var(--font,'Plus Jakarta Sans',system-ui,sans-serif)}
.pub *{box-sizing:border-box}
.pub-nav{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;
  padding:16px 24px;background:rgba(255,255,255,.85);backdrop-filter:blur(12px);border-bottom:1px solid var(--brand-line,#c9def0)}
.pub-brand{font-weight:800;font-size:17px;color:var(--brand-ink,#0b3a5e);text-decoration:none}
.pub-cta{font-weight:700;font-size:14px;color:#fff;background:var(--brand,#0e7cc4);border-radius:999px;padding:9px 18px;text-decoration:none}
.pub-hero{max-width:900px;margin:0 auto;padding:52px 24px 20px;text-align:center}
.pub-eyebrow{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--brand,#0e7cc4);margin-bottom:10px}
.pub-hero h1{font-size:clamp(32px,5vw,48px);font-weight:800;margin:0;line-height:1.05}
.pub-hero p{color:var(--ink-2,#54657a);font-size:17px;max-width:52ch;margin:14px auto 0}
.pub-feed{max-width:900px;margin:0 auto;padding:24px 24px 60px;display:grid;gap:20px}
.pub-post{background:var(--surface,#fff);border:1px solid var(--brand-line,#dce9f5);border-radius:var(--radius,16px);
  overflow:hidden;display:grid;grid-template-columns:280px 1fr;transition:transform .2s,box-shadow .2s;box-shadow:0 6px 20px rgba(15,27,42,.05)}
.pub-post:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(15,27,42,.1)}
@media(max-width:620px){.pub-post{grid-template-columns:1fr}}
.pub-post img{width:100%;height:100%;min-height:200px;object-fit:cover;display:block;background:var(--brand-tint,#eef5fb)}
.pub-body{padding:24px 26px}
.pub-meta{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.pub-fmt{font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--brand,#0e7cc4);
  border:1px solid var(--brand-line,#c9def0);border-radius:999px;padding:4px 10px}
.pub-fecha{font-size:13px;color:var(--ink-3,#8696a8)}
.pub-cap{font-size:16px;line-height:1.65;color:var(--ink,#0f1b2a);white-space:pre-wrap}
.pub-tags{margin-top:16px;display:flex;gap:7px;flex-wrap:wrap}
.pub-tag{font-size:12px;color:var(--ink-2,#54657a);background:var(--brand-tint,#eef5fb);border-radius:999px;padding:4px 11px}
.pub-empty{text-align:center;padding:70px 20px;color:var(--ink-3,#8696a8)}
.pub-big{font-size:52px;margin-bottom:12px}
.pub-foot{border-top:1px solid var(--brand-line,#dce9f5);padding:26px 0;text-align:center;color:var(--ink-3,#8696a8);font-size:13px}
`;
