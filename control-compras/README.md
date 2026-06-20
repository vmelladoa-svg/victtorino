# 📊 Control de Compras

App web para llevar el control mensual de **Productos, Insumos, Servicios básicos, Gastos generales y Retiros**.
Cada movimiento lleva su fecha. Dashboard con totales por categoría, comparación de meses, gráficos y presupuesto vs. real.

## Stack
- Next.js 14 (App Router) + TypeScript + Tailwind
- Almacenamiento: **nube (Upstash Redis vía Vercel)** con **respaldo local** (localStorage) si no hay nube
- Acceso protegido por **PIN**

## Correr local
```bash
npm install
npm run dev    # http://localhost:3000
```
Sin variables de entorno corre en **modo local** (datos en este navegador). El PIN se crea en el primer uso.

## Activar sincronización entre dispositivos (nube)
1. En Vercel, agrega una base **Upstash Redis** (Marketplace) al proyecto → inyecta `KV_REST_API_URL` y `KV_REST_API_TOKEN` (o `UPSTASH_REDIS_REST_URL`/`TOKEN`).
2. Agrega la variable `APP_PIN` con el PIN que quieras (valida el acceso en el servidor).
3. Redeploy. La app detecta la nube sola (`/api/status`) y pasa a modo sincronizado.

## Datos
- Cada movimiento: fecha · categoría · descripción · proveedor · monto (CLP) · método de pago · nota.
- Presupuesto mensual por categoría.
- Exportar a Excel (CSV) desde el botón “Exportar”.
- Formato CLP vía `lib/format.ts`.
