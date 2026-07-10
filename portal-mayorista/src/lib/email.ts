// Envío de emails transaccionales vía Resend. Fire-and-forget: si Resend falla o
// no está configurado, NUNCA bloquea el registro.
//
// Configuración (una sola vez):
//   1. Crear cuenta en resend.com y una API key.
//   2. Verificar el dominio comercialsolutions.cl (o usar onboarding@resend.dev
//      para pruebas).
//   3. Variables de entorno:
//      RESEND_API_KEY = la API key (empieza con "re_")
//      RESEND_FROM    = remitente, ej. "Comercial Solutions <no-reply@comercialsolutions.cl>"

const RESEND_API = "https://api.resend.com/emails";
const TIMEOUT_MS = 8000;

// Escapa texto para insertarlo con seguridad en el HTML del email.
function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

interface BienvenidaDatos {
  email: string;
  nombre: string;
}

function htmlBienvenida(nombre: string): string {
  return `
  <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:560px;margin:0 auto;color:#0f1b2a;">
    <div style="background:linear-gradient(135deg,#0a3d62,#051f35);padding:28px 32px;border-radius:12px 12px 0 0;">
      <h1 style="color:#fff;font-size:20px;margin:0;">Comercial Solutions</h1>
      <p style="color:#9db8cc;font-size:13px;margin:4px 0 0;">Portal Mayorista B2B</p>
    </div>
    <div style="background:#fff;border:1px solid #e4ebf2;border-top:none;padding:28px 32px;border-radius:0 0 12px 12px;">
      <p style="font-size:15px;">Hola ${esc(nombre)},</p>
      <p style="font-size:15px;line-height:1.6;"><strong>¡Tu cuenta ya está activa! 🎉</strong> Puedes entrar ahora mismo y ver todos los precios mayoristas.</p>
      <div style="text-align:center;margin:22px 0;">
        <a href="https://comercialsolutions.cl/login" style="display:inline-block;background:#0a3d62;color:#fff;text-decoration:none;font-size:15px;font-weight:700;padding:13px 28px;border-radius:8px;">Entrar al portal &rarr;</a>
      </div>
      <div style="background:#f3f8fc;border-radius:10px;padding:18px 22px;margin:20px 0;">
        <p style="font-size:13px;font-weight:700;color:#54657a;margin:0 0 12px;">Cómo comprar, paso a paso:</p>
        <ol style="font-size:14px;line-height:1.9;margin:0;padding-left:20px;">
          <li><strong>Explora el catálogo</strong> — +5.000 productos importados con stock real.</li>
          <li><strong>Arma tu pedido</strong> — el precio baja según la cantidad (precios escalonados por volumen).</li>
          <li><strong>Paga por transferencia</strong> y sube tu comprobante desde "Mis pedidos".</li>
          <li><strong>Validamos y despachamos</strong> a todo Chile (envío gratis sobre $400.000).</li>
        </ol>
      </div>
      <p style="font-size:14px;line-height:1.6;color:#54657a;">¿Dudas? Escríbenos por WhatsApp al <strong>+56 9 2178 9322</strong> o a <a href="mailto:contacto@comercialsolutions.cl" style="color:#0e7cc4;">contacto@comercialsolutions.cl</a>.</p>
      <p style="font-size:14px;margin-top:24px;">Un saludo,<br><strong>Equipo Comercial Solutions</strong></p>
    </div>
    <p style="text-align:center;font-size:11px;color:#8696a8;margin-top:16px;">comercialsolutions.cl</p>
  </div>`;
}

export async function enviarBienvenida(datos: BienvenidaDatos): Promise<void> {
  const key = process.env.RESEND_API_KEY;
  if (!key) return; // sin API key → no-op silencioso
  const from = process.env.RESEND_FROM || "Comercial Solutions <onboarding@resend.dev>";

  try {
    await fetch(RESEND_API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        from,
        to: [datos.email],
        subject: "¡Bienvenido! Tu cuenta ya está activa — Comercial Solutions",
        html: htmlBienvenida(datos.nombre),
      }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    /* nunca bloquea el registro */
  }
}
