@echo off
REM Refresca falabella_raw.json una vez (lo dispara la tarea de Windows cada 5 min).
REM Portable: usa su propia ubicacion, sirve igual en el notebook o en el PC de bodega.
cd /d "%~dp0.."
node server\falabella-refresher.mjs --once >> "%~dp0fala_refresh.log" 2>&1
