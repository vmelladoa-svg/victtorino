@echo off
REM Re-mide la salud de las publicaciones y compara con baseline.
REM Lanzado manualmente o via Windows Task Scheduler.

cd /d "C:\Users\dell\victtorino"
python volver_a_medir.py > medicion_log.txt 2>&1
type medicion_log.txt
