@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-real-stack.ps1"
set EXIT_CODE=%ERRORLEVEL%
if not "%EXIT_CODE%"=="0" (
  echo.
  echo stop-real-stack failed with exit code %EXIT_CODE%.
  pause
  exit /b %EXIT_CODE%
)
endlocal
