@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-real-stack.ps1"
set EXIT_CODE=%ERRORLEVEL%
if not "%EXIT_CODE%"=="0" (
  echo.
  echo start-real-stack failed with exit code %EXIT_CODE%.
  echo Check the message above. Common causes are occupied ports 3000/3001/8000.
  pause
  exit /b %EXIT_CODE%
)
endlocal
