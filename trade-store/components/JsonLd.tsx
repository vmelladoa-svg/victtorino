import { SITE, waLink } from "@/lib/site";

// Datos estructurados de la marca/tienda (Schema.org) para SEO y buscadores con IA.
export function OrgJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@type": "Store",
    name: "Trade",
    slogan: SITE.tagline,
    description:
      "Tienda de grifería, baño, cocina y accesorios para el hogar con despacho a todo Chile.",
    url: SITE.url,
    logo: `${SITE.url}/logo.png`,
    image: `${SITE.url}/logo.png`,
    email: SITE.email,
    telephone: "+" + SITE.whatsapp,
    areaServed: { "@type": "Country", name: "Chile" },
    currenciesAccepted: "CLP",
    paymentAccepted: "Webpay, Transferencia bancaria",
    sameAs: [waLink()],
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
