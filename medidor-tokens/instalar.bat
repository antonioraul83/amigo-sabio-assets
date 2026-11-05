@echo off
rem Instala el medidor de tokens y crea un acceso directo en el escritorio.
rem Doble clic en este archivo (debe estar en la misma carpeta que medidor_tokens.py).
setlocal
set "DEST=%LOCALAPPDATA%\MedidorTokens"

if not exist "%~dp0medidor_tokens.py" (
  echo No encuentro medidor_tokens.py al lado de este instalador.
  echo Pon los dos archivos en la misma carpeta y vuelve a probar.
  pause & exit /b 1
)

set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo No encuentro Python en este PC.
  echo Instalalo desde https://www.python.org/downloads/ marcando "Add python.exe to PATH"
  echo y vuelve a hacer doble clic en este instalador.
  pause & exit /b 1
)

if not exist "%DEST%" mkdir "%DEST%"
copy /y "%~dp0medidor_tokens.py" "%DEST%\medidor_tokens.py" >nul

> "%DEST%\Medidor de tokens.bat" (
  echo @echo off
  echo cd /d "%DEST%"
  echo %PY% medidor_tokens.py --dias 30 --salida "%DEST%\medidor-tokens.html"
  echo if errorlevel 1 pause
)

powershell -NoProfile -Command "$d=[Environment]::GetFolderPath('Desktop'); $s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Medidor de tokens.lnk')); $s.TargetPath='%DEST%\Medidor de tokens.bat'; $s.WorkingDirectory='%DEST%'; $s.IconLocation='%SystemRoot%\System32\imageres.dll,144'; $s.WindowStyle=7; $s.Save()"

if errorlevel 1 (
  echo No he podido crear el acceso directo.
  pause & exit /b 1
)
echo.
echo Listo. Tienes "Medidor de tokens" en el escritorio.
echo Doble clic y se abre el medidor en el navegador.
pause
