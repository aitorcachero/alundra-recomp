@echo off
title Alundra Recompiled (HD-2D 16:9 4K)
cd /d "%~dp0build-release"

:: Variables de optimizacion grafica y refresco
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=1
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_2D=1

:: Iniciar el reescalador IA 100% invisible en segundo plano (sin ventana)
if exist "%~dp0tools\auto_upscale_textures.py" (
    start "" pythonw "%~dp0tools\auto_upscale_textures.py" --watch
)

:: Ejecutar el juego directamente
"Alundra_Recompiled.exe"

:: Al salir, detener el proceso invisible de la IA
taskkill /f /im pythonw.exe >nul 2>&1
