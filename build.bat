@echo off
chcp 65001 >nul
echo ============================================
echo  Claude Code CLI Installer - Build Script
echo ============================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "ClaudeCodeInstaller" ^
    --add-data "data;data" ^
    --add-data "core;core" ^
    --add-data "gui;gui" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --noconfirm ^
    --clean ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo  Build successful!
    echo  Output: dist\ClaudeCodeInstaller.exe
    echo ============================================
) else (
    echo.
    echo ============================================
    echo  Build failed! Check errors above.
    echo ============================================
    exit /b 1
)
