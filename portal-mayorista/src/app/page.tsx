import type { Metadata } from "next";
import { Lexend, Source_Sans_3 } from "next/font/google";
import LandingClient from "@/components/landing-client";
import { prisma } from "@/lib/db";
import { imgSrc } from "@/lib/img";
import { GRUPOS, grupoDe, nivel1 } from "@/lib/categorias";

const SITE = "https://comercialsolutions.cl";

// Solo los pesos que la landing realmente usa: Lexend 600/700/800 (títulos/botones), Source 400/600 (texto).
const lexend = Lexend({ subsets: ["latin"], variable: "--font-lexend", weight: ["600", "700", "800"], display: "swap" });
const sourceSans = Source_Sans_3({ subsets: ["latin"], variable: "--font-source", weight: ["400", "600"], display: "swap" });

export const metadata: Metadata = {
  title: "Comercial Solutions — Portal Mayorista B2B | Venta por mayor en Chile",
  description:
    "Compra al por mayor para tu negocio: precios escalonados por volumen, stock en tiempo real y despacho a todo Chile. Tecnología, herramientas, hogar, salud y más. Regístrate gratis.",
  alternates: { canonical: SITE },
  openGraph: {
    type: "website",
    url: SITE,
    siteName: "Comercial Solutions",
    title: "Portal Mayorista B2B — Comercial Solutions",
    description: "Precios mayoristas, volumen por caja y despacho a todo Chile para tu negocio.",
  },
};

export const revalidate = 3600; // ISR: refresca el escaparate cada hora

type Featured = { nombre: string; img: string; grupo: string };

async function getEscaparate(): Promise<{ productos: Featured[]; catImg: Record<string, string> }> {
  try {
    const rows = await prisma.producto.findMany({
      where: { activo: true, fotoUrl: { not: null } },
      select: { nombre: true, categoria: true, fotoUrl: true },
      take: 80,
    });
    const productos: Featured[] = [];
    const catImg: Record<string, string> = {};
    for (const r of rows) {
      if (!r.fotoUrl) continue;
      const grupo = grupoDe(nivel1(r.categoria));
      const img = imgSrc(r.fotoUrl);
      if (!catImg[grupo]) catImg[grupo] = img;
      productos.push({ nombre: r.nombre, img, grupo });
    }
    return { productos: productos.slice(0, 18), catImg };
  } catch {
    return { productos: [], catImg: {} };
  }
}

export default async function Home() {
  const { productos, catImg } = await getEscaparate();
  const categorias = GRUPOS.map((g) => ({ nombre: g.nombre, img: catImg[g.nombre] ?? null }));

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": `${SITE}/#organizacion`,
        name: "Comercial Solutions",
        legalName: "Trade Global Solutions SpA",
        url: SITE,
        logo: `${SITE}/logo-clean.png`,
        description:
          "Portal de compras mayoristas B2B en Chile: precios por volumen, stock en tiempo real y despacho a todo el país.",
        areaServed: "CL",
      },
      { "@type": "WebSite", "@id": `${SITE}/#sitio`, url: SITE, name: "Portal Mayorista | Comercial Solutions", inLanguage: "es-CL", publisher: { "@id": `${SITE}/#organizacion` } },
    ],
  };

  return (
    <div className={`${lexend.variable} ${sourceSans.variable}`}>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <LandingClient productos={productos} categorias={categorias} />
    </div>
  );
}
