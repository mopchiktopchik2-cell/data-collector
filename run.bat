@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)

if not defined PY (
    echo.
    echo Python не найден.
    echo Установите Python 3.9 или новее: https://www.python.org/downloads/
    echo При установке отметьте галочку "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if errorlevel 1 (
    echo.
    echo Нужен Python 3.9 или новее. Установленная версия:
    %PY% --version
    echo.
    pause
    exit /b 1
)

%PY% main.py

echo.
echo Программа завершилась. Окно можно закрыть.
pause
