import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: { root: __dirname },
  images: {
    // Fotos de producto viven en el CDN de uniCloud/bspapp (host único por app).
    remotePatterns: [{ protocol: "https", hostname: "**.cdn.bspapp.com" }],
    formats: ["image/avif", "image/webp"],
  },
};

export default nextConfig;
