@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py"
if defined PY goto havepython

where python >nul 2>nul
if not errorlevel 1 set "PY=python"
if defined PY goto havepython

echo.
echo Python не найден.
echo Установите Python 3.9 или новее: https://www.python.org/downloads/
echo При установке отметьте галочку "Add Python to PATH".
echo.
pause
goto end

:havepython
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if errorlevel 1 goto oldpython

%PY% main.py

echo.
echo Программа завершилась. Окно можно закрыть.
pause
goto end

:oldpython
echo.
echo Нужен Python 3.9 или новее. Установленная версия:
%PY% --version
echo.
pause
goto end

:end
endlocal
