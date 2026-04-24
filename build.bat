@echo off
echo Limpiando builds anteriores...
rmdir /s /q build
rmdir /s /q dist
del *.spec

echo Generando ejecutable...
python -m PyInstaller --onefile --windowed application.pyw --name InventariosCD --add-data "assets;assets"

echo Build completado.
pause 