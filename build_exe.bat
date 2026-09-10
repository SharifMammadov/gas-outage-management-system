@echo off
echo Gas Outage Management System - building executable...
echo.

pyinstaller --onefile --windowed ^
    --name "GasOutageManagementSystem" ^
    --hidden-import PyQt6.sip ^
    main.py

echo.
if %errorlevel% equ 0 (
    echo Build complete: dist\GasOutageManagementSystem.exe
) else (
    echo Build failed.
)

pause
