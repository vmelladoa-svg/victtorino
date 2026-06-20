import type { Metadata } from "next";
import { Sora, Hanken_Grotesk } from "next/font/google";
import "./globals.css";
import { StoreProvider } from "@/lib/store-context";
import { StoreChrome } from "@/components/StoreChrome";
import { SITE } from "@/lib/site";
import { OrgJsonLd } from "@/components/JsonLd";

const sora = Sora({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sora",
  display: "swap",
});

const hanken = Hanken_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-hanken",
  display: "swap",
});

const DESC =
  "Grifería, baño, cocina y accesorios para el hogar con despacho a todo Chile. Precios en CLP, IVA incluido y garantía de 6 meses.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE.url),
  title: {
    default: "Trade — Soluciones para tu hogar",
    template: "%s · Trade",
  },
  description: DESC,
  applicationName: "Trade",
  keywords: [
    "grifería",
    "baño",
    "cocina",
    "espejos",
    "mamparas",
    "lavaplatos",
    "accesorios de baño",
    "Chile",
    "Trade",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "es_CL",
    siteName: "Trade",
    title: "Trade — Soluciones para tu hogar",
    description: DESC,
    url: SITE.url,
    images: [{ url: "/logo.png", width: 242, height: 181, alt: "Trade" }],
  },
  twitter: {
    card: "summary",
    title: "Trade — Soluciones para tu hogar",
    description: DESC,
    images: ["/logo.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={`${sora.variable} ${hanken.variable}`}>
      <body>
        <OrgJsonLd />
        <StoreProvider>
          {children}
          <StoreChrome />
        </StoreProvider>
      </body>
    </html>
  );
}
