const LIST = [
  {
    n: "Carolina M.",
    w: "Santiago",
    t: "Compré una llave monomando y un espejo LED. Llegó todo bien embalado y la calidad superó lo que esperaba por el precio.",
  },
  {
    n: "Rodrigo P.",
    w: "Viña del Mar",
    t: "Me asesoraron por WhatsApp para elegir la mampara correcta para mi baño. Excelente atención y despacho rápido.",
  },
  {
    n: "Fernanda A.",
    w: "Concepción",
    t: "Renové la cocina completa: lavaplatos, grifería y accesorios. Todo combinó perfecto y los precios son muy convenientes.",
  },
];

export function Testimonials() {
  return (
    <section className="block" id="testimonios">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Clientes</span>
            <h2>Lo que dicen de nosotros</h2>
          </div>
        </div>
        <div className="testi-grid">
          {LIST.map((x) => (
            <div className="testi" key={x.n}>
              <span className="stars">★★★★★</span>
              <p>“{x.t}”</p>
              <div className="testi-who">
                <span className="testi-av">{x.n[0]}</span>
                <span>
                  <b>{x.n}</b>
                  <span>{x.w}</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
