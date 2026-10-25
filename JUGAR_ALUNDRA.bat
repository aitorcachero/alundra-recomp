@echo off
cd /d "%~dp0"

:: 1. Si existe Alundra.exe en esta carpeta, arrancarlo directamente
if exist "Alundra.exe" (
    start "" "Alundra.exe"
    exit /b
)

:: 2. Localizar el directorio donde reside el ejecutable del juego
if exist "alundra-recomp\build-release\Alundra_Recompiled.exe" (
    cd /d "%~dp0alundra-recomp\build-release"
) else if exist "build-release\Alundra_Recompiled.exe" (
    cd /d "%~dp0build-release"
)

:: 3. Variables graficas y de refresco
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=1
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_2D=1

if exist "Alundra.exe" (
    start "" "Alundra.exe"
    exit /b
)

start "" "Alundra_Recompiled.exe"
exit /b
