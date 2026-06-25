@echo off
chcp 65001 >nul
title Claude Code CLI Installer

echo ============================================
echo   Claude Code CLI Installer
echo   适配国内网络环境
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo 正在启动...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序异常退出，请检查上述错误信息。
    pause
)
