@echo off
REM Arranque del Monitor de Ventas en el PC de bodega.
REM Levanta el servidor (build de producción) y abre Chrome en pantalla completa (kiosko) en el TV.
cd /d "%~dp0"

REM 1) Servidor en segundo plano (sirve dist/ + /feed en http://localhost:5180)
start "monitor-server" /min cmd /c "npm run preview"

REM 2) Espera a que levante y abre Chrome en modo kiosko
timeout /t 7 /nobreak >nul
start "" chrome --kiosk "http://localhost:5180" --noerrdialogs --disable-session-crashed-bubble --disable-infobars --overscroll-history-navigation=0

REM Para salir del kiosko en el TV: Alt+F4 (o Ctrl+W).
