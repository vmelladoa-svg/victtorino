import { Icon, ICONS } from "./Icon";

export function Hero({ productCount }: { productCount: number }) {
  return (
    <section className="hero" id="inicio">
      <div className="wrap hero-in">
        <div>
          <span className="hero-kicker">Baño · Cocina · Hogar</span>
          <h1>
            Soluciones para <em>tu hogar</em>, con calidad que se nota
          </h1>
          <p className="lead">
            Grifería, espejos, duchas, accesorios de baño y cocina seleccionados por su
            durabilidad y diseño. Precios claros y despacho a todo Chile.
          </p>
          <div className="hero-ctas">
            <a className="btn btn-primary" href="#catalogo">
              Ver catálogo <Icon d={ICONS.arrow} size={17} />
            </a>
            <a className="btn btn-ghost" href="#categorias">
              Explorar categorías
            </a>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <b>{productCount}+</b>
              <span>productos disponibles</span>
            </div>
            <div className="hero-stat">
              <b>7</b>
              <span>categorías de hogar</span>
            </div>
            <div className="hero-stat">
              <b>6 meses</b>
              <span>de garantía</span>
            </div>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div
            className="hero-orb"
            style={{ width: 340, height: 340, top: -80, right: -60 }}
          />
          <div
            className="hero-orb"
            style={{ width: 220, height: 220, bottom: 30, left: -70, opacity: 0.7 }}
          />
          <div className="hero-visual-inner">
            <h3>Renueva tu baño y cocina</h3>
            <p>Productos en acero inoxidable y cerámica, listos para instalar.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
