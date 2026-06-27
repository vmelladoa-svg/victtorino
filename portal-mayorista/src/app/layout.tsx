import type { Metadata } from "next";
import { Geist, Geist_Mono, Sora, Manrope } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { CartProvider } from "@/lib/cart-context";

const FB_PIXEL = "1361965342502798";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });
const sora = Sora({ variable: "--font-sora", subsets: ["latin"], weight: ["700", "800"] });
const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
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
      className={`${geistSans.variable} ${geistMono.variable} ${sora.variable} ${manrope.variable}`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>
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
        <CartProvider>{children}</CartProvider>
      </body>
    </html>
  );
}
