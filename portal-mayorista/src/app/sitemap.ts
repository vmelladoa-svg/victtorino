import type { MetadataRoute } from "next";

const BASE = "https://comercialsolutions.cl";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${BASE}/registro`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 1.0,
    },
    {
      url: `${BASE}/login`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.6,
    },
  ];
}
