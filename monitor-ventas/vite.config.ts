import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import legacy from '@vitejs/plugin-legacy'

// Endpoint /feed: scraper read-only servido en el mismo origen (sin CORS, sin proceso extra).
// Funciona en dev (configureServer) y en producción/preview (configurePreviewServer, vía import directo).
function feedPlugin() {
  const handler = (getData: () => Promise<any>) => async (_req: any, res: any) => {
    try {
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify(await getData()))
    } catch (e: any) {
      res.statusCode = 500
      res.end(JSON.stringify({ error: e?.message || 'feed error' }))
    }
  }
  return {
    name: 'ml-feed',
    configureServer(server: any) {
      server.middlewares.use('/feed', handler(async () =>
        (await server.ssrLoadModule('/server/feed.mjs')).obtenerFeed()))
    },
    configurePreviewServer(server: any) {
      server.middlewares.use('/feed', handler(async () =>
        (await import('./server/feed.mjs')).obtenerFeed()))
    },
  }
}

export default defineConfig({
  plugins: [
    react(),
    // Polyfills + transpilación para el navegador viejo del TV TCL.
    legacy({ targets: ['chrome >= 49', 'safari >= 10'], renderModernChunks: false }),
    feedPlugin(),
  ],
  server: { host: true, port: 5180 },   // dev
  preview: { host: true, port: 5180 },  // build servido para el TV
})
