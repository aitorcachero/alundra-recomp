@echo off
cd /d "%~dp0"

:: Si existe el ejecutable nativo silencioso Alundra.exe, lanzarlo y cerrar cmd al instante
if exist "Alundra.exe" (
    start "" "Alundra.exe"
    exit /b
)
if exist "build-release\Alundra.exe" (
    start "" "build-release\Alundra.exe"
    exit /b
)

:: En caso contrario, configurar variables y lanzar
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=1
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_2D=1

if exist "tools\auto_upscale_textures.py" (
    start "" pythonw "tools\auto_upscale_textures.py" --watch
)

if exist "Alundra_Recompiled.exe" (
    start "" "Alundra_Recompiled.exe"
) else (
    start "" "build-release\Alundra_Recompiled.exe"
)
exit /b
