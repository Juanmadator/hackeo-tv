@echo off
rem Registra "Hackeo TV" para que arranque solo con Windows, sin ventana.
rem Ejecutar una vez. Para quitarlo: schtasks /Delete /TN HackeoTV /F
set PY=%~dp0.venv\Scripts\pythonw.exe
set SCRIPT=%~dp0auto.py
schtasks /Create /F /TN "HackeoTV" /SC ONLOGON /RL LIMITED /TR "\"%PY%\" \"%SCRIPT%\""
if errorlevel 1 (echo ERROR creando la tarea & exit /b 1)
schtasks /Run /TN "HackeoTV"
echo Listo: Hackeo TV arrancara con Windows y ya esta en marcha.
