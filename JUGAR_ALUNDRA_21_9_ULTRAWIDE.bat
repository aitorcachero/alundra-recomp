@echo off
cd /d "%~dp0"

:: Lanzador dedicado 21:9 Ultra-Panoramico (Ultrawide 2560x1080 / 3440x1440 / 5120x2160)
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=0
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_FULLSCREEN=1
set PSX_WS_FORCE_3D=1
set PSX_WS_FORCE_2D=1
set PSX_ASPECT_RATIO=21:9
set PSX_INTERNAL_SCALE=8

if exist "Alundra.exe" (
    start "" "Alundra.exe" -21:9
    exit /b
)
if exist "build-release\Alundra.exe" (
    start "" "build-release\Alundra.exe" -21:9
    exit /b
)
if exist "alundra-recomp\Alundra.exe" (
    cd /d "%~dp0alundra-recomp"
    start "" "Alundra.exe" -21:9
    exit /b
)

if exist "Alundra_Recompiled.exe" (
    start "" "Alundra_Recompiled.exe"
) else if exist "build-release\Alundra_Recompiled.exe" (
    cd /d "%~dp0build-release"
    start "" "Alundra_Recompiled.exe"
) else if exist "alundra-recomp\build-release\Alundra_Recompiled.exe" (
    cd /d "%~dp0alundra-recomp\build-release"
    start "" "Alundra_Recompiled.exe"
)
exit /b
