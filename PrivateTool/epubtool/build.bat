@echo off
setlocal
cd /d "%~dp0"

set PY=python
%PY% --version >nul 2>&1
if errorlevel 1 set PY=py
%PY% --version >nul 2>&1
if errorlevel 1 (
  echo Python not found. Install Python from python.org first ^(tick "Add python.exe to PATH"^).
  pause
  exit /b 1
)

echo Installing PyInstaller...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo Failed to install PyInstaller.
  pause
  exit /b 1
)

echo Building EPUBTool.exe ...
%PY% -m PyInstaller --clean --onefile --windowed --name EPUBTool epub_tool.py
if not exist dist\EPUBTool.exe (
  echo.
  echo FAILED to build EPUBTool.exe, check the error messages above.
  pause
  exit /b 1
)

REM Make a ready-to-use portable folder
if not exist EPUBTool_App mkdir EPUBTool_App
copy /Y dist\EPUBTool.exe EPUBTool_App\EPUBTool.exe >nul
if not exist EPUBTool_App\raw mkdir EPUBTool_App\raw
if not exist EPUBTool_App\results mkdir EPUBTool_App\results
if not exist EPUBTool_App\cover mkdir EPUBTool_App\cover

rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
del /Q EPUBTool.spec 2>nul

echo.
echo Done. Your portable app is in the folder: EPUBTool_App
echo Copy that whole folder anywhere - no Python needed to run it.
pause
