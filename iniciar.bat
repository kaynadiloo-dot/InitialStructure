@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %*
set "zenoExit=%errorlevel%"
if not "%zenoExit%"=="0" if "%~1"=="" pause
exit /b %zenoExit%
