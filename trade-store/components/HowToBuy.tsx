const STEPS = [
  {
    n: "1",
    b: "Elige y paga seguro",
    p: "Busca por categoría o SKU, agrega al carrito y paga con Webpay o transferencia. Boleta al correo de inmediato.",
  },
  {
    n: "2",
    b: "Despachamos a tu puerta",
    p: "Enviamos a todo Chile en 2 a 5 días hábiles. Sobre $60.000 el despacho es gratis.",
  },
  {
    n: "3",
    b: "Instala con respaldo",
    p: "Todos los productos incluyen 6 meses de garantía y 10 días para cambios o devoluciones.",
  },
];

export function HowToBuy() {
  return (
    <section className="block soft" id="como-comprar">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <span className="sec-kicker">Simple y seguro</span>
            <h2>Comprar en Trade es así de fácil</h2>
          </div>
        </div>
        <div className="steps-grid">
          {STEPS.map((s) => (
            <div className="step-card" key={s.n}>
              <span className="step-num">{s.n}</span>
              <b>{s.b}</b>
              <p>{s.p}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
