@echo off
REM Ingesta de ventas al núcleo, una pasada (lo dispara la tarea de Windows cada ~10-15 min).
REM Portable: usa su propia ubicación. Requiere ERP_NUCLEO_KEY en el entorno.
cd /d "%~dp0.."
node server\erp-ingesta.mjs --once >> "%~dp0erp_ingesta.log" 2>&1
