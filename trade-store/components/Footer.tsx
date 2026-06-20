import Image from "next/image";
import { SITE, waLink } from "@/lib/site";
import { InstallTermsLink } from "./InstallTermsLink";

export function Footer() {
  return (
    <footer className="site-footer" id="contacto">
      <div className="wrap">
        <div className="foot-in">
          <div>
            <div className="foot-brand">
              <Image src="/logo.png" alt="Logo Trade" width={54} height={40} />
              <b>{SITE.brand}</b>
            </div>
            <p>
              Soluciones para tu hogar. Grifería, baño, cocina y accesorios con despacho a todo
              Chile.
            </p>
          </div>
          <div>
            <h4>Tienda</h4>
            <div className="foot-links">
              <a href="#catalogo">Catálogo completo</a>
              <a href="#categorias">Categorías</a>
              <a href="#ofertas">Ofertas</a>
              <a href="#faq">Preguntas frecuentes</a>
            </div>
          </div>
          <div>
            <h4>Empresa</h4>
            <div className="foot-links">
              <a href="#nosotros">Nosotros</a>
              <a href="#instalacion">Servicio de instalación</a>
              <InstallTermsLink>Condiciones de instalación</InstallTermsLink>
              <a href="#faq">Cambios y devoluciones</a>
            </div>
          </div>
          <div>
            <h4>Contacto</h4>
            <div className="foot-links">
              <a href={`mailto:${SITE.email}`}>{SITE.email}</a>
              <a href={waLink()} target="_blank" rel="noopener">
                WhatsApp {SITE.whatsappDisplay}
              </a>
              <p>{SITE.hours}</p>
            </div>
          </div>
        </div>
        <div className="pay-badges">
          {["Webpay", "Visa", "Mastercard", "Transferencia", "12 cuotas sin interés"].map((b) => (
            <span className="pay-badge" key={b}>
              {b}
            </span>
          ))}
        </div>
        <div className="foot-bottom">
          <span>© 2026 Trade — Soluciones para tu hogar. Todos los derechos reservados.</span>
          <span>Precios en pesos chilenos (CLP), IVA incluido.</span>
        </div>
      </div>
    </footer>
  );
}
