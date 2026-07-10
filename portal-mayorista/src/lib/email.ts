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

// --- Contacto público: cambiar SOLO aquí y se actualiza en todos los correos ---
const WA_NUM = "56937624425";               // solo dígitos (código país + número)
const WA_DISPLAY = "+56 9 3762 4425";       // formato visible
const WA_LINK = `https://wa.me/${WA_NUM}`;

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
  const wa = WA_LINK + "?text=" + encodeURIComponent("Hola, me registré en Comercial Solutions y quiero comprar al por mayor.");
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
        <br>
        <a href="${wa}" style="display:inline-block;margin-top:12px;color:#1f9d57;font-size:14px;font-weight:700;text-decoration:none;">💬 O escríbenos por WhatsApp</a>
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
      <p style="font-size:14px;line-height:1.6;color:#54657a;">¿Dudas? Escríbenos por WhatsApp al <strong>${WA_DISPLAY}</strong> o a <a href="mailto:contacto@comercialsolutions.cl" style="color:#0e7cc4;">contacto@comercialsolutions.cl</a>.</p>
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

interface ItemPedido {
  nombre: string;
  cantidad: number;
  precio: number;
  subtotal: number;
}
interface ConfirmacionPedidoDatos {
  email: string;
  nombre: string;
  folio: string;
  fecha: Date;
  total: number;
  direccion: string;
  region: string;
  items: ItemPedido[];
}

const clp = (n: number) => "$" + n.toLocaleString("es-CL");

function htmlPedido(d: ConfirmacionPedidoDatos): string {
  const fecha = d.fecha.toLocaleDateString("es-CL", { day: "2-digit", month: "long", year: "numeric" });
  const filas = d.items.map((it) => `
        <tr>
          <td style="padding:9px 10px;border-bottom:1px solid #eef2f6;font-size:13px;">${esc(it.nombre)}</td>
          <td style="padding:9px 10px;border-bottom:1px solid #eef2f6;font-size:13px;text-align:center;">${it.cantidad}</td>
          <td style="padding:9px 10px;border-bottom:1px solid #eef2f6;font-size:13px;text-align:right;">${clp(it.precio)}</td>
          <td style="padding:9px 10px;border-bottom:1px solid #eef2f6;font-size:13px;text-align:right;font-weight:600;">${clp(it.subtotal)}</td>
        </tr>`).join("");
  return `
  <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:600px;margin:0 auto;color:#0f1b2a;">
    <div style="background:linear-gradient(135deg,#0a3d62,#051f35);padding:26px 32px;border-radius:12px 12px 0 0;">
      <h1 style="color:#fff;font-size:19px;margin:0;">Comercial Solutions</h1>
      <p style="color:#9db8cc;font-size:13px;margin:4px 0 0;">Comprobante de pedido</p>
    </div>
    <div style="background:#fff;border:1px solid #e4ebf2;border-top:none;padding:26px 32px;border-radius:0 0 12px 12px;">
      <p style="font-size:15px;">Hola ${esc(d.nombre)},</p>
      <p style="font-size:15px;line-height:1.6;">¡Recibimos tu pedido! Aquí está tu comprobante.</p>
      <table style="width:100%;border-collapse:collapse;margin:18px 0;">
        <tr>
          <td style="font-size:13px;color:#54657a;padding:2px 0;">N° de orden</td>
          <td style="font-size:15px;font-weight:700;text-align:right;padding:2px 0;">#${esc(d.folio)}</td>
        </tr>
        <tr>
          <td style="font-size:13px;color:#54657a;padding:2px 0;">Fecha</td>
          <td style="font-size:14px;text-align:right;padding:2px 0;">${fecha}</td>
        </tr>
        <tr>
          <td style="font-size:13px;color:#54657a;padding:2px 0;">Estado</td>
          <td style="text-align:right;padding:2px 0;"><span style="background:#fff3d9;color:#a9781a;font-size:12px;font-weight:700;padding:3px 10px;border-radius:20px;">Pago en validación</span></td>
        </tr>
      </table>
      <table style="width:100%;border-collapse:collapse;margin:8px 0 4px;">
        <thead>
          <tr style="background:#f3f8fc;">
            <th style="padding:9px 10px;text-align:left;font-size:11px;color:#54657a;text-transform:uppercase;letter-spacing:.04em;">Producto</th>
            <th style="padding:9px 10px;text-align:center;font-size:11px;color:#54657a;text-transform:uppercase;">Cant.</th>
            <th style="padding:9px 10px;text-align:right;font-size:11px;color:#54657a;text-transform:uppercase;">Precio</th>
            <th style="padding:9px 10px;text-align:right;font-size:11px;color:#54657a;text-transform:uppercase;">Subtotal</th>
          </tr>
        </thead>
        <tbody>${filas}
        </tbody>
      </table>
      <table style="width:100%;border-collapse:collapse;margin:6px 0 18px;">
        <tr>
          <td style="font-size:15px;font-weight:700;padding:10px 10px;">Total</td>
          <td style="font-size:17px;font-weight:800;text-align:right;padding:10px 10px;color:#0a3d62;">${clp(d.total)}</td>
        </tr>
      </table>
      <div style="background:#f3f8fc;border-radius:10px;padding:14px 18px;margin:0 0 18px;">
        <p style="font-size:12px;font-weight:700;color:#54657a;margin:0 0 4px;text-transform:uppercase;letter-spacing:.04em;">Despacho</p>
        <p style="font-size:14px;margin:0;">${esc(d.direccion)}, ${esc(d.region)}</p>
      </div>
      <p style="font-size:14px;line-height:1.6;color:#54657a;">Estamos validando tu pago. Te avisaremos apenas se confirme y preparemos el despacho. Puedes ver el estado en <a href="https://comercialsolutions.cl/mis-pedidos" style="color:#0e7cc4;">Mis pedidos</a>.</p>
      <p style="font-size:14px;line-height:1.6;color:#54657a;">¿Dudas? WhatsApp <strong>${WA_DISPLAY}</strong> o <a href="mailto:contacto@comercialsolutions.cl" style="color:#0e7cc4;">contacto@comercialsolutions.cl</a>.</p>
      <p style="font-size:14px;margin-top:22px;">Gracias por tu compra,<br><strong>Equipo Comercial Solutions</strong></p>
    </div>
    <p style="text-align:center;font-size:11px;color:#8696a8;margin-top:16px;">comercialsolutions.cl</p>
  </div>`;
}

export async function enviarConfirmacionPedido(d: ConfirmacionPedidoDatos): Promise<void> {
  const key = process.env.RESEND_API_KEY;
  if (!key) return; // sin API key → no-op silencioso
  const from = process.env.RESEND_FROM || "Comercial Solutions <onboarding@resend.dev>";
  try {
    await fetch(RESEND_API, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
      body: JSON.stringify({
        from,
        to: [d.email],
        subject: `Pedido #${d.folio} recibido — Comercial Solutions`,
        html: htmlPedido(d),
      }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    /* nunca bloquea el pedido */
  }
}
