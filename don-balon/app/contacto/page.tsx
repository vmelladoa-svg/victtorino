export const metadata = { title: "Contacto — Don Balón" };

export default function ContactoPage() {
  return (
    <div className="container-db grid max-w-5xl gap-10 py-12 md:grid-cols-2">
      <div>
        <h1 className="display text-4xl md:text-5xl">Hablemos</h1>
        <p className="mt-3 text-neutral-600">¿Dudas con tu pedido o un producto? Estamos para ayudarte.</p>
        <div className="mt-8 space-y-4">
          <Info icon="💬" title="WhatsApp" value="+56 9 1234 5678" />
          <Info icon="✉️" title="Correo" value="hola@donbalon.cl" />
          <Info icon="📍" title="Tienda" value="Av. Deporte 1234, Santiago" />
          <Info icon="🕒" title="Horario" value="Lun a Sáb · 10:00–20:00" />
        </div>
      </div>

      <form className="rounded-2xl border border-black/10 p-6 shadow-card">
        <h2 className="font-head text-lg font-bold">Envíanos un mensaje</h2>
        <div className="mt-4 space-y-4">
          <Field label="Nombre" placeholder="Tu nombre" />
          <Field label="Correo" type="email" placeholder="tu@correo.cl" />
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium">Mensaje</span>
            <textarea rows={4} placeholder="¿En qué te ayudamos?" className="rounded-xl border border-black/15 px-4 py-2.5 text-sm outline-none focus:border-balon" />
          </label>
          <button type="button" className="btn-primary w-full py-3">Enviar mensaje</button>
        </div>
      </form>
    </div>
  );
}

function Info({ icon, title, value }: { icon: string; title: string; value: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid h-11 w-11 place-items-center rounded-xl bg-balon-50 text-xl">{icon}</span>
      <div>
        <div className="text-xs uppercase tracking-wide text-neutral-400">{title}</div>
        <div className="font-head font-semibold">{value}</div>
      </div>
    </div>
  );
}
function Field({ label, ...rest }: { label: string } & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm font-medium">{label}</span>
      <input {...rest} className="rounded-xl border border-black/15 px-4 py-2.5 text-sm outline-none focus:border-balon" />
    </label>
  );
}
