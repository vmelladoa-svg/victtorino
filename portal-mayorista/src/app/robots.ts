import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: ["/", "/registro", "/login"],
      disallow: ["/admin", "/api", "/catalogo", "/checkout", "/carrito", "/mis-pedidos", "/favoritos", "/revision"],
    },
    sitemap: "https://comercialsolutions.cl/sitemap.xml",
  };
}
