import type { MetadataRoute } from "next";

const BASE = "https://comercialsolutions.cl";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${BASE}/login`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${BASE}/registro`, changeFrequency: "monthly", priority: 0.9 },
  ];
}
