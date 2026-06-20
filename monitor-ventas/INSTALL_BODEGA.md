# Instalar el Monitor de Ventas en el PC de bodega (Lenovo, Windows 11)

El monitor queda corriendo **solo en ese PC**, independiente del notebook. Sirve datos reales
(ML, Web, Falabella) en `http://localhost:5180` y Chrome lo muestra en el TV en pantalla completa.

## 1. Requisitos (una vez)

1. Instalar **Node.js LTS** desde https://nodejs.org (botón "LTS"). Acepta todo por defecto.
2. Copiar la carpeta **`monitor-ventas`** completa a este PC (ej. `C:\monitor-ventas`),
   incluyendo la subcarpeta **`secrets\`** (trae los tokens; NO está en internet, viene en el paquete).

## 2. Setup (una vez, en una terminal dentro de la carpeta)

Abre **PowerShell** en `C:\monitor-ventas` (clic derecho en la carpeta → "Abrir en Terminal") y corre:

```powershell
npm install
npx playwright install chromium
npm run build
```

## 3. Login de Falabella (una vez)

```powershell
npm run fala:login
```
Se abre una ventana de Chrome → inicia sesión como **Trade Global** (contactotradegs@gmail.com).
Cuando veas la lista de órdenes, listo (guarda la sesión). Ciérrala.

## 4. Dejar Falabella refrescándose solo (tarea de Windows)

En **PowerShell como Administrador**, en `C:\monitor-ventas`:

```powershell
schtasks /create /tn "TradeFalabellaFeed" /tr "`"$PWD\server\fala_refresh.cmd`"" /sc minute /mo 5 /st 00:00 /f
```

## 5. Arrancar el monitor

Doble clic en **`start-monitor.cmd`** (o desde PowerShell: `.\start-monitor.cmd`).
- Levanta el servidor y abre Chrome en **pantalla completa** en el TV.
- Para salir del modo kiosko en el TV: **Alt+F4**.

## 6. Que arranque solo al prender el PC

1. Tecla **Windows + R** → escribe `shell:startup` → Enter (abre la carpeta de Inicio).
2. Crea ahí un **acceso directo** a `C:\monitor-ventas\start-monitor.cmd`.

Listo: cada vez que se prenda el PC, el monitor se abre solo en el TV.

## Notas

- Necesita **internet** (consulta las APIs de ML y la web; Falabella se refresca por el navegador logueado).
- Si Falabella deja de actualizar y el log (`server\fala_refresh.log`) dice "NO logueado" → repetir el paso 3.
- **MercadoLibre / tokens:** este PC refresca los tokens de ML por su cuenta. Para evitar peleas de tokens,
  asegúrate de que la integración ML de Victoria en Railway esté apagada (`ML_ENABLED=false`) — los loops de
  ML allá no deben estar refrescando los mismos tokens.
- Para actualizar el monitor a futuro: reemplazar los archivos (sin tocar `secrets\`) y `npm run build`.
