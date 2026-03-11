@echo off
setlocal
set EXE=%~dp0dist\tr.exe
if exist "%EXE%" (
  "%EXE%" %*
) else (
  python "%~dp0tr.py" %*
)
if errorlevel 1 (
  echo Conversion finished with errors.
) else (
  echo Conversion done.
)
pause
