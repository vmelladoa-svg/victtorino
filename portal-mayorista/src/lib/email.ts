// Envio de correos a comerciantes via Resend (API HTTP, sin SDK).
// Remitente configurable por env para cambiar dominio/remitente sin tocar codigo.
const apiKey = process.env.RESEND_API_KEY;
// Hasta verificar comercialsolutions.cl en Resend, su dominio de prueba solo
// entrega a tu propio correo. Con dominio verificado: "Comercial Solutions <pedidos@comercialsolutions.cl>".
const from = process.env.MAIL_FROM ?? "Comercial Solutions <onboarding@resend.dev>";

// ponytail: sin API key = no-op silencioso. El correo NUNCA debe romper el flujo del pedido.
export async function enviarCorreo(to: string, asunto: string, html: string): Promise<boolean> {
  if (!apiKey) {
    console.warn("[email] RESEND_API_KEY no configurada; se omite envio a", to);
    return false;
  }
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ from, to, subject: asunto, html }),
    });
    if (!res.ok) {
      console.error("[email] Resend respondio", res.status, await res.text());
      return false;
    }
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
