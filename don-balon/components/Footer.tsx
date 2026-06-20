import Link from "next/link";
import { categories } from "@/data/products";

export default function Footer() {
  return (
    <footer className="mt-20 bg-grad-carbon text-neutral-300">
      <div className="container-db grid grid-cols-2 gap-8 py-14 md:grid-cols-4">
        <div className="col-span-2 md:col-span-1">
          <span className="display text-2xl text-white">Don<span className="text-balon">Balón</span></span>
          <p className="mt-3 max-w-xs text-sm text-neutral-400">
            Tu tienda deportiva. Pelotas y artículos para que vivas el juego con todo. Envío a todo Chile.
          </p>
          <div className="mt-4 flex gap-3 text-xl">
            <a href="#" aria-label="Instagram" className="transition hover:text-balon">📸</a>
            <a href="#" aria-label="Facebook" className="transition hover:text-balon">📘</a>
            <a href="#" aria-label="TikTok" className="transition hover:text-balon">🎵</a>
            <a href="#" aria-label="YouTube" className="transition hover:text-balon">▶️</a>
          </div>
        </div>

        <div>
          <h4 className="font-head font-semibold text-white">Categorías</h4>
          <ul className="mt-3 space-y-2 text-sm">
            {categories.map((c) => (
              <li key={c.slug}>
                <Link href={`/catalogo?sport=${c.slug}`} className="transition hover:text-balon">{c.name}</Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="font-head font-semibold text-white">Ayuda</h4>
          <ul className="mt-3 space-y-2 text-sm">
            <li><Link href="/envios" className="hover:text-balon">Envíos y devoluciones</Link></li>
            <li><Link href="/faq" className="hover:text-balon">Preguntas frecuentes</Link></li>
            <li><Link href="/contacto" className="hover:text-balon">Contacto</Link></li>
            <li><Link href="/sobre" className="hover:text-balon">Sobre Don Balón</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-head font-semibold text-white">Pago seguro</h4>
          <p className="mt-3 text-sm text-neutral-400">Paga con tarjetas de crédito y débito vía Webpay.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="rounded-md bg-white px-3 py-1.5 text-xs font-bold text-azulina">Webpay</span>
            <span className="rounded-md bg-white/10 px-3 py-1.5 text-xs font-semibold">VISA</span>
            <span className="rounded-md bg-white/10 px-3 py-1.5 text-xs font-semibold">Mastercard</span>
            <span className="rounded-md bg-white/10 px-3 py-1.5 text-xs font-semibold">Redcompra</span>
          </div>
        </div>
      </div>

      <div className="border-t border-white/10">
        <div className="container-db flex flex-col items-center justify-between gap-2 py-5 text-xs text-neutral-500 md:flex-row">
          <span>© {new Date().getFullYear()} Don Balón · Maqueta de demostración</span>
          <span>Hecho en Chile 🇨🇱 · Precios en CLP</span>
        </div>
      </div>
    </footer>
  );
}
