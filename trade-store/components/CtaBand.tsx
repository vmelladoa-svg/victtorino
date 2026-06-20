import { waLink } from "@/lib/site";

export function CtaBand() {
  return (
    <section className="block" style={{ paddingBottom: 0 }}>
      <div className="wrap">
        <div className="cta-band">
          <div>
            <h2>¿Listo para renovar tu hogar?</h2>
            <p>
              Explora el catálogo completo o escríbenos por WhatsApp para una asesoría sin
              costo.
            </p>
          </div>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
            <a className="btn btn-white" href="#catalogo">
              Ver catálogo
            </a>
            <a className="btn btn-accent" href={waLink()} target="_blank" rel="noopener">
              Escríbenos
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
