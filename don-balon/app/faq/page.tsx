export const metadata = { title: "Preguntas frecuentes — Don Balón" };

const FAQS = [
  { q: "¿Cómo pago mi compra?", a: "Aceptamos tarjetas de crédito y débito a través de Webpay (Transbank), de forma 100% segura. En esta maqueta el pago es simulado." },
  { q: "¿Hacen envíos a todo Chile?", a: "Sí. Despachamos a todo el país en 24–48 horas hábiles. El envío es gratis en compras sobre $39.990." },
  { q: "¿Puedo retirar en tienda?", a: "Claro. Elige 'Retiro en tienda' en el checkout y retira gratis en Av. Deporte 1234, Santiago. Te avisamos cuando esté listo." },
  { q: "¿Los productos son originales?", a: "Siempre. Trabajamos solo con marcas y distribuidores oficiales, y todo cuenta con garantía contra defectos de fabricación." },
  { q: "¿Puedo cambiar o devolver un producto?", a: "Tienes 30 días desde la recepción para devolver o cambiar, sin uso y con su embalaje original." },
  { q: "¿Cómo sé qué tamaño de balón elegir?", a: "Cada producto indica su tamaño oficial en las especificaciones. Si tienes dudas, escríbenos por WhatsApp y te asesoramos." },
  { q: "¿Tienen boleta o factura?", a: "Sí, emitimos documento tributario por cada compra. Podrás descargarlo desde el correo de confirmación." },
];

export default function FaqPage() {
  return (
    <div className="container-db max-w-3xl py-12">
      <h1 className="display text-4xl md:text-5xl">Preguntas frecuentes</h1>
      <div className="mt-8 space-y-3">
        {FAQS.map((f) => (
          <details key={f.q} className="group rounded-2xl border border-black/10 bg-white p-5 shadow-card">
            <summary className="flex cursor-pointer list-none items-center justify-between font-head font-semibold">
              {f.q}
              <span className="text-balon transition-transform group-open:rotate-45">＋</span>
            </summary>
            <p className="mt-3 text-sm text-neutral-600">{f.a}</p>
          </details>
        ))}
      </div>
    </div>
  );
}
