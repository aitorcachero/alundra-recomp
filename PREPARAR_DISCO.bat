@echo off
title Alundra Recompiled - Preparador Universal de Disco
cd /d "%~dp0"
echo ========================================================
echo   Iniciando Preparador de Disco Universal de Alundra
echo ========================================================
echo.
py -3 "tools\setup_disc.py" %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocurrio un error preparando el disco.
    pause
) else (
    echo.
    echo Todo listo. Ya puedes hacer doble clic en JUGAR_ALUNDRA.bat
    pause
)
