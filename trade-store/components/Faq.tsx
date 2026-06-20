"use client";

import { useState } from "react";

const FAQS = [
  {
    q: "¿Hacen despacho a todo Chile?",
    a: "Sí. Despachamos a todas las regiones a través de couriers establecidos. El plazo habitual es de 2 a 5 días hábiles según la comuna de destino.",
  },
  {
    q: "¿Qué medios de pago aceptan?",
    a: "Aceptamos tarjetas de crédito y débito (Webpay) y transferencia bancaria. El pago se confirma de inmediato y recibirás tu boleta por correo.",
  },
  {
    q: "¿Los productos tienen garantía?",
    a: "Todos nuestros productos cuentan con 6 meses de garantía por defectos de fábrica. Si algo falla, coordinamos el cambio o la devolución sin costo para ti.",
  },
  {
    q: "¿Puedo cambiar o devolver un producto?",
    a: "Tienes 10 días desde la recepción para solicitar un cambio o devolución, siempre que el producto esté sin uso y en su empaque original.",
  },
  {
    q: "¿Me pueden ayudar a elegir el producto correcto?",
    a: "Por supuesto. Escríbenos por WhatsApp con una foto o las medidas de tu espacio y te recomendamos las opciones compatibles.",
  },
];

export function Faq() {
  const [open, setOpen] = useState(0);
  return (
    <section className="block soft" id="faq">
      <div className="wrap">
        <div className="sec-head" style={{ justifyContent: "center", textAlign: "center" }}>
          <div style={{ margin: "0 auto" }}>
            <span className="sec-kicker">Ayuda</span>
            <h2>Preguntas frecuentes</h2>
          </div>
        </div>
        <div className="faq-list">
          {FAQS.map((f, i) => (
            <div className="faq-item" key={i}>
              <button className="faq-q" onClick={() => setOpen(open === i ? -1 : i)}>
                {f.q}
                <span className="tg">{open === i ? "−" : "+"}</span>
              </button>
              {open === i && <div className="faq-a">{f.a}</div>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
