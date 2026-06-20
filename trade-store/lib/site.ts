// Datos de contacto y marca. Provisorios — reemplazar por los definitivos de Trade.
export const SITE = {
  brand: "TRADE",
  tagline: "Soluciones para tu hogar",
  email: "contacto@trade.cl",
  // número en formato internacional sin "+" para los enlaces wa.me
  whatsapp: "56912345678",
  whatsappDisplay: "+56 9 1234 5678",
  hours: "Lunes a viernes · 9:00 a 18:00 hrs",
  // URL pública del sitio (para canonical/OG/sitemap). Definir al publicar.
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://tradeglobalchile.cl",
};

export const waLink = (text?: string) =>
  `https://wa.me/${SITE.whatsapp}` + (text ? `?text=${encodeURIComponent(text)}` : "");
