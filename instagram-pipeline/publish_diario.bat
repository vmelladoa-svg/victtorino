@echo off
REM Publicador diario de Instagram para @victtorino_griferias
REM Ejecutado por Windows Task Scheduler todos los dias a las 19:00

cd /d "C:\Users\dell\victtorino\instagram-pipeline"
echo === %DATE% %TIME% === >> publish_diario.log
python 06_publish_instagram.py --next >> publish_diario.log 2>&1
echo === fin %DATE% %TIME% === >> publish_diario.log
echo. >> publish_diario.log
