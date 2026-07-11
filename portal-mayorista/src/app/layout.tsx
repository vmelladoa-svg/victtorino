import type { Metadata } from "next";
import { Sora, Manrope } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { CartProvider } from "@/lib/cart-context";

const FB_PIXEL = "1361965342502798";
const GA4_ID = "G-MEBFEM1YS5"; // Propiedad GA4 "Comercial Solutions" (vinculada a Google Ads 9591328095)

// Sora/Manrope solo las usa el carrusel del catálogo. preload:false → no se descargan
// en páginas que no las aplican (p.ej. la landing). Geist/Geist Mono se quitaron (sin uso).
const sora = Sora({ variable: "--font-sora", subsets: ["latin"], weight: ["700", "800"], preload: false });
const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  preload: false,
});

export const metadata: Metadata = {
  title: "Portal Mayorista | Comercial Solutions",
  description: "Accede a precios mayoristas, volumen por caja y despacho a todo Chile. Portal B2B de Comercial Solutions.",
  metadataBase: new URL("https://comercialsolutions.cl"),
  alternates: {
    canonical: "https://comercialsolutions.cl",
  },
  openGraph: {
    title: "Comercial Solutions — Venta por Mayor B2B",
    description: "Precios escalonados por volumen, stock en tiempo real y seguimiento de pedidos. Despacho a todo Chile.",
    url: "https://comercialsolutions.cl",
    siteName: "Comercial Solutions",
    locale: "es_CL",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Comercial Solutions — Venta por Mayor B2B",
    description: "Precios escalonados por volumen, stock en tiempo real y seguimiento de pedidos.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "Comercial Solutions",
  url: "https://comercialsolutions.cl",
  description: "Portal de compras mayoristas B2B. Precios escalonados por volumen, despacho a todo Chile.",
  areaServed: "CL",
  contactPoint: {
    "@type": "ContactPoint",
    contactType: "sales",
    areaServed: "CL",
    availableLanguage: "Spanish",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="es"
      className={`${sora.variable} ${manrope.variable}`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>
        <Script src={`https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`} strategy="afterInteractive" />
        <Script id="ga4" strategy="afterInteractive">
          {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${GA4_ID}');`}
        </Script>
        <Script id="fb-pixel" strategy="lazyOnload">
          {`!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','${FB_PIXEL}');fbq('track','PageView');`}
        </Script>
        <noscript>
          <img
            height="1"
            width="1"
            style={{ display: "none" }}
            alt=""
            src={`https://www.facebook.com/tr?id=${FB_PIXEL}&ev=PageView&noscript=1`}
          />
        </noscript>
        {/* Victoria — agente IA de Comercial Solutions (motor multi-tenant en okai.cl) */}
        <Script
          src="https://okai.cl/assets/victoria-widget.js"
          data-client="comercial-solutions"
          data-endpoint="https://okai.cl/api/chat"
          strategy="lazyOnload"
        />
        <CartProvider>{children}</CartProvider>
      </body>
    </html>
  );
}
