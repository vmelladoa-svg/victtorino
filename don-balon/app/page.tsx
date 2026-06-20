import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import { categories, getBestSellers, brands } from "@/data/products";
import { formatCLP } from "@/lib/format";

export default function HomePage() {
  const best = getBestSellers();

  return (
    <>
      {/* HERO */}
      <section className="relative overflow-hidden bg-grad-carbon text-white">
        <div className="pointer-events-none absolute -right-20 -top-24 h-[520px] w-[520px] rounded-full bg-balon/30 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-32 -left-24 h-[420px] w-[420px] rounded-full bg-cancha/20 blur-3xl" />
        <div className="container-db relative grid items-center gap-8 py-16 md:grid-cols-2 md:py-24">
          <div className="animate-fade-up">
            <span className="badge bg-balon text-white">Nueva temporada 2026</span>
            <h1 className="display mt-4 text-5xl text-white sm:text-6xl md:text-7xl">
              Vive el juego<br />con <span className="text-balon">Don Balón</span>
            </h1>
            <p className="mt-5 max-w-md text-lg text-neutral-300">
              Pelotas y equipamiento para fútbol, básquetbol, béisbol y vóleibol. Calidad profesional, despacho a todo Chile.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/catalogo" className="btn-primary px-7 py-4 text-base">Comprar ahora →</Link>
              <Link href="/catalogo?sport=basquetbol" className="btn px-7 py-4 text-base text-white ring-1 ring-white/30 hover:ring-white">
                Ver básquetbol
              </Link>
            </div>
            <div className="mt-7 flex flex-wrap gap-x-6 gap-y-2 text-sm text-neutral-400">
              <span>🚚 Envío gratis sobre {formatCLP(39990)}</span>
              <span>🔒 Pago seguro Webpay</span>
              <span>↩️ 30 días de devolución</span>
            </div>
          </div>
          {/* gráfico hero */}
          <div className="relative hidden h-80 md:block">
            <div className="absolute right-6 top-2 grid h-44 w-44 animate-fade-up place-items-center rounded-3xl bg-grad-balon text-8xl shadow-cta">🏀</div>
            <div className="absolute left-10 top-28 grid h-32 w-32 place-items-center rounded-3xl bg-white text-6xl shadow-card">⚽</div>
            <div className="absolute bottom-2 right-24 grid h-28 w-28 place-items-center rounded-3xl bg-azulina text-5xl shadow-card">⚾</div>
            <div className="absolute bottom-10 left-2 grid h-24 w-24 place-items-center rounded-2xl bg-cancha text-4xl shadow-card">🏐</div>
          </div>
        </div>
      </section>

      {/* BENEFICIOS */}
      <section className="border-b border-black/5 bg-white">
        <div className="container-db grid grid-cols-2 gap-4 py-8 md:grid-cols-4">
          {[
            { i: "🚚", t: "Envío rápido", s: "24–48h hábiles" },
            { i: "🔒", t: "Pago seguro", s: "Webpay / Transbank" },
            { i: "🛡️", t: "Garantía real", s: "Productos originales" },
            { i: "↩️", t: "Devoluciones", s: "Hasta 30 días" },
          ].map((b) => (
            <div key={b.t} className="flex items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-balon-50 text-xl">{b.i}</span>
              <div>
                <div className="font-head font-semibold leading-tight">{b.t}</div>
                <div className="text-xs text-neutral-500">{b.s}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CATEGORÍAS */}
      <section className="container-db py-14">
        <div className="mb-6 flex items-end justify-between">
          <h2 className="display text-3xl md:text-4xl">Compra por deporte</h2>
          <Link href="/catalogo" className="text-sm font-semibold text-balon hover:underline">Ver todo →</Link>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          {categories.map((c) => (
            <Link
              key={c.slug}
              href={`/catalogo?sport=${c.slug}`}
              className="group relative overflow-hidden rounded-2xl border border-black/10 p-5 transition-all hover:-translate-y-1 hover:shadow-card-hover"
              style={{ background: `linear-gradient(160deg, ${c.color}14, #fff)` }}
            >
              <span className="text-4xl">{c.icon}</span>
              <div className="mt-3 font-head text-lg font-bold">{c.name}</div>
              <div className="text-xs text-neutral-500">{c.tagline}</div>
              <span className="mt-3 inline-block text-sm font-semibold text-balon opacity-0 transition group-hover:opacity-100">Explorar →</span>
            </Link>
          ))}
        </div>
      </section>

      {/* MÁS VENDIDOS */}
      <section className="bg-neutral-50 py-14">
        <div className="container-db">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <span className="badge bg-carbon text-white">🔥 Top ventas</span>
              <h2 className="display mt-2 text-3xl md:text-4xl">Los más vendidos</h2>
            </div>
            <Link href="/catalogo" className="text-sm font-semibold text-balon hover:underline">Ver catálogo →</Link>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {best.map((p) => <ProductCard key={p.id} product={p} />)}
          </div>
        </div>
      </section>

      {/* MARCAS */}
      <section className="container-db py-12">
        <p className="text-center text-sm font-semibold uppercase tracking-widest text-neutral-400">Trabajamos con las mejores marcas</p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-x-10 gap-y-4">
          {brands.map((b) => (
            <span key={b} className="font-display text-2xl text-neutral-300 transition hover:text-carbon">{b}</span>
          ))}
        </div>
      </section>

      {/* TU EQUIPO / COLORES */}
      <section className="container-db py-8">
        <div className="overflow-hidden rounded-3xl bg-grad-balon p-10 text-white md:p-14">
          <h2 className="display max-w-xl text-3xl md:text-5xl">Encuentra el balón de tu equipo</h2>
          <p className="mt-3 max-w-md text-white/90">Elige por color y lleva los de tu club a la cancha.</p>
          <div className="mt-7 flex flex-wrap gap-3">
            {[
              { n: "Rojo", c: "#DC2626" }, { n: "Azul", c: "#2563EB" }, { n: "Verde", c: "#16A34A" },
              { n: "Negro", c: "#111111" }, { n: "Blanco", c: "#F8FAFC" }, { n: "Naranjo", c: "#E8590C" },
            ].map((t) => (
              <Link key={t.n} href="/catalogo" className="flex items-center gap-2 rounded-full bg-white/15 py-2 pl-2 pr-4 text-sm font-semibold backdrop-blur transition hover:bg-white/25">
                <span className="h-6 w-6 rounded-full ring-2 ring-white/60" style={{ background: t.c }} />
                {t.n}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* NEWSLETTER */}
      <section className="container-db py-14">
        <div className="rounded-3xl border border-black/10 bg-carbon px-6 py-12 text-center text-white">
          <h2 className="display text-3xl md:text-4xl">10% OFF en tu primera compra</h2>
          <p className="mx-auto mt-2 max-w-md text-neutral-300">Suscríbete y recibe ofertas, lanzamientos y tips deportivos.</p>
          <form className="mx-auto mt-6 flex max-w-md flex-col gap-3 sm:flex-row">
            <input type="email" placeholder="tu@correo.cl" className="flex-1 rounded-xl border-0 px-4 py-3 text-carbon outline-none" />
            <button type="button" className="btn-primary px-6 py-3">Quiero mi 10%</button>
          </form>
        </div>
      </section>
    </>
  );
}
