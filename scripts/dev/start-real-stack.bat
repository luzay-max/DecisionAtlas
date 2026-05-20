@echo off
setlocal
set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..\..

if /i "%~1"=="/?" goto :usage
if /i "%~1"=="-h" goto :usage
if /i "%~1"=="--help" goto :usage

cd /d "%REPO_ROOT%"
echo Starting DecisionAtlas real stack...
echo.
echo This will start Docker postgres/redis, run migrations, seed demo data,
echo and launch Engine ^(8000^), API ^(3001^), and Web ^(3000^).
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-real-stack.ps1" -OpenBrowser %*
set EXIT_CODE=%ERRORLEVEL%
echo.
if not "%EXIT_CODE%"=="0" (
  echo start-real-stack failed with exit code %EXIT_CODE%.
  echo Check the message above and logs under .tmp\real-stack.
  echo Common causes are occupied ports 3000/3001/8000 or Docker not running.
  if not defined DECISIONATLAS_NO_PAUSE pause
  exit /b %EXIT_CODE%
)
echo DecisionAtlas real stack startup command completed.
echo Web:    http://127.0.0.1:3000
echo API:    http://127.0.0.1:3001/health
echo Engine: http://127.0.0.1:8000/health
echo.
echo Keep this window for startup status. Stop the stack with:
echo powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1
echo.
if not defined DECISIONATLAS_NO_PAUSE pause
endlocal
exit /b 0

:usage
echo Usage: scripts\dev\start-real-stack.bat [-ResetSeededDemo]
echo.
echo Starts Docker postgres/redis, runs migrations, seeds demo data,
echo launches Engine ^(8000^), API ^(3001^), Web ^(3000^), and opens the Web UI.
echo.
echo Set DECISIONATLAS_NO_PAUSE=1 to skip the final pause in terminal automation.
endlocal
exit /b 0
