@echo off
cd /d "%~dp0"

:: 1. Lanzar el ejecutable nativo silencioso si existe
if exist "Alundra.exe" (
    start "" "Alundra.exe"
    exit /b
)
if exist "build-release\Alundra.exe" (
    start "" "build-release\Alundra.exe"
    exit /b
)

:: 2. Si se ejecuta desde el hub raíz
if exist "alundra-recomp\Alundra.exe" (
    cd /d "%~dp0alundra-recomp"
    start "" "Alundra.exe"
    exit /b
)

:: 3. Lanzar runtime directo si aplica
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=0
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_2D=1

if exist "Alundra_Recompiled.exe" (
    start "" "Alundra_Recompiled.exe"
) else if exist "build-release\Alundra_Recompiled.exe" (
    cd /d "%~dp0build-release"
    start "" "Alundra_Recompiled.exe"
)
exit /b
