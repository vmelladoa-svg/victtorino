import nodemailer from "nodemailer";

// Remitente configurable por env para poder cambiar de Gmail a buzon propio sin tocar codigo.
// Gmail SMTP requiere "contrasena de aplicacion" (no la clave normal).
const host = process.env.MAIL_HOST ?? "smtp.gmail.com";
const port = Number(process.env.MAIL_PORT ?? 465);
const user = process.env.MAIL_USER;
const pass = process.env.MAIL_PASS;
const from = process.env.MAIL_FROM ?? (user ? `Comercial Solutions <${user}>` : undefined);

// ponytail: sin credenciales = no-op silencioso. El correo NUNCA debe romper el flujo del pedido.
export async function enviarCorreo(to: string, asunto: string, html: string): Promise<boolean> {
  if (!user || !pass) {
    console.warn("[email] MAIL_USER/MAIL_PASS no configurados; se omite envio a", to);
    return false;
  }
  try {
    const t = nodemailer.createTransport({
      host,
      port,
      secure: port === 465,
      auth: { user, pass },
    });
    await t.sendMail({ from, to, subject: asunto, html });
    return true;
  } catch (e) {
    console.error("[email] fallo enviando a", to, e);
    return false;
  }
}

const wrap = (cuerpo: string) =>
  `<div style="font-family:system-ui,Arial,sans-serif;max-width:560px;margin:0 auto;color:#1a1a2e">
    <div style="background:#1f4e79;color:#fff;padding:16px 20px;border-radius:8px 8px 0 0">
      <strong style="font-size:18px">Comercial Solutions</strong>
    </div>
    <div style="border:1px solid #e5e7eb;border-top:0;padding:20px;border-radius:0 0 8px 8px">
      ${cuerpo}
      <p style="color:#6b7280;font-size:13px;margin-top:24px">Comercial Solutions · comercialsolutions.cl</p>
    </div>
  </div>`;

export function tplPagoValidado(nombre: string, pedidoId: string, total: number) {
  return wrap(
    `<h2 style="margin:0 0 12px">Pago confirmado ✅</h2>
     <p>Hola ${nombre}, recibimos y validamos el pago de tu pedido <strong>#${pedidoId.slice(-6).toUpperCase()}</strong> por <strong>$${total.toLocaleString("es-CL")}</strong>.</p>
     <p>Ya estamos preparando tu compra. Te avisaremos cuando salga despachada.</p>`,
  );
}

export function tplDespachado(
  nombre: string,
  pedidoId: string,
  transportista?: string | null,
  tracking?: string | null,
) {
  const envio = [
    transportista ? `<p>Transportista: <strong>${transportista}</strong></p>` : "",
    tracking ? `<p>Seguimiento: <strong>${tracking}</strong></p>` : "",
  ].join("");
  return wrap(
    `<h2 style="margin:0 0 12px">Tu pedido fue despachado 🚚</h2>
     <p>Hola ${nombre}, tu pedido <strong>#${pedidoId.slice(-6).toUpperCase()}</strong> ya va en camino.</p>
     ${envio}`,
  );
}
