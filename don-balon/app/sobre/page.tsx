export const metadata = { title: "Sobre Don Balón" };

export default function SobrePage() {
  return (
    <div className="container-db py-12">
      <section className="overflow-hidden rounded-3xl bg-grad-carbon p-10 text-white md:p-16">
        <span className="badge bg-balon text-white">Nuestra historia</span>
        <h1 className="display mt-4 max-w-2xl text-4xl md:text-6xl">Nacimos para que vivas el juego</h1>
        <p className="mt-4 max-w-xl text-neutral-300">
          Don Balón parte como un sueño de barrio: acercar equipamiento deportivo de calidad profesional a cada cancha,
          gimnasio y patio de Chile, a un precio justo y con despacho rápido.
        </p>
      </section>

      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {[
          { i: "🎯", t: "Calidad real", d: "Solo productos originales, probados en cancha por deportistas reales." },
          { i: "⚡", t: "Rápido y simple", d: "Compra en minutos y recibe en 24–48h hábiles en todo Chile." },
          { i: "🤝", t: "Cerca de ti", d: "Atención humana por WhatsApp y retiro en tienda cuando lo necesites." },
        ].map((v) => (
          <div key={v.t} className="rounded-2xl border border-black/10 p-6 shadow-card">
            <span className="text-3xl">{v.i}</span>
            <h3 className="mt-3 font-head text-xl font-bold">{v.t}</h3>
            <p className="mt-1 text-sm text-neutral-600">{v.d}</p>
          </div>
        ))}
      </div>

      <div className="mt-12 grid gap-4 rounded-3xl bg-balon-50 p-10 text-center md:grid-cols-4">
        {[["+15.000", "pedidos enviados"], ["4.8★", "valoración promedio"], ["+200", "productos"], ["24-48h", "despacho"]].map(([n, l]) => (
          <div key={l}>
            <div className="font-display text-4xl text-balon">{n}</div>
            <div className="text-sm text-neutral-600">{l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
