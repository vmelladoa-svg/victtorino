@echo off
REM Wrapper para Windows Task Scheduler
REM Ejecuta seguimiento_auto.py con encoding UTF-8 y log a archivo

cd /d "C:\Users\dell\victtorino"
set PYTHONIOENCODING=utf-8
"C:\Users\dell\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\dell\victtorino\seguimiento_auto.py" >> "C:\Users\dell\victtorino\data\auditoria\seguimiento_runs\bat_wrapper.log" 2>&1
exit /b %ERRORLEVEL%
