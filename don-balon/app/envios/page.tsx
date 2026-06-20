import { formatCLP } from "@/lib/format";

export const metadata = { title: "Envíos y devoluciones — Don Balón" };

export default function EnviosPage() {
  return (
    <div className="container-db max-w-3xl py-12">
      <h1 className="display text-4xl md:text-5xl">Envíos y devoluciones</h1>

      <div className="mt-8 space-y-6">
        <Card title="🚚 Despacho a domicilio">
          Enviamos a todo Chile en <b>24 a 48 horas hábiles</b>. El costo se calcula en el checkout según tu comuna.
          <b className="text-cancha"> Envío gratis</b> en compras sobre {formatCLP(39990)}.
        </Card>
        <Card title="🏬 Retiro en tienda">
          Retira gratis en <b>Av. Deporte 1234, Santiago</b>, de lunes a sábado de 10:00 a 20:00. Te avisamos por correo cuando tu pedido esté listo (normalmente el mismo día).
        </Card>
        <Card title="↩️ Devoluciones (30 días)">
          Si el producto no te convence, tienes <b>30 días</b> desde la recepción para devolverlo, sin uso y con su embalaje original.
          Te reembolsamos por el mismo medio de pago o te lo cambiamos por otro producto.
        </Card>
        <Card title="🛡️ Garantía">
          Todos nuestros productos son originales y cuentan con garantía contra defectos de fabricación. Escríbenos y lo resolvemos.
        </Card>
      </div>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-black/10 p-6 shadow-card">
      <h2 className="font-head text-xl font-bold">{title}</h2>
      <p className="mt-2 text-neutral-600">{children}</p>
    </div>
  );
}
