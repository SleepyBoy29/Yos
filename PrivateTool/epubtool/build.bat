@echo off
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name EPUBTool epub_tool.py
if exist dist\EPUBTool.exe (
  echo.
  echo Selesai. Hasil: dist\EPUBTool.exe
) else (
  echo.
  echo GAGAL membuat EPUBTool.exe, cek pesan error di atas.
)
pause
