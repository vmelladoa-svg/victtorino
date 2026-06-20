import type { MetadataRoute } from "next";
import { SITE } from "@/lib/site";

// Sitio de una sola página: la home y sus secciones por ancla.
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: SITE.url, changeFrequency: "weekly", priority: 1 },
    { url: `${SITE.url}/#catalogo`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${SITE.url}/#categorias`, changeFrequency: "monthly", priority: 0.7 },
    { url: `${SITE.url}/#ofertas`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${SITE.url}/#nosotros`, changeFrequency: "yearly", priority: 0.4 },
    { url: `${SITE.url}/#contacto`, changeFrequency: "yearly", priority: 0.4 },
  ];
}
