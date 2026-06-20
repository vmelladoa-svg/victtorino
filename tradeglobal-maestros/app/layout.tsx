import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });

export const metadata: Metadata = {
  title: "Maestros — TradeGlobalChile",
  description:
    "Regístrate como maestro instalador: precios mayoristas y trabajos pagados semanalmente.",
};

export const viewport: Viewport = { themeColor: "#0F2942" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={inter.variable}>
      <body className="font-sans text-navy">{children}</body>
    </html>
  );
}
