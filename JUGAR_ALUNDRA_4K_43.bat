@echo off
cd /d "%~dp0"

:: Lanzador dedicado 4:3 Clasico Original en 4K UHD
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=0
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_FULLSCREEN=0
set PSX_WS_FORCE_3D=0
set PSX_WS_FORCE_2D=0
set PSX_ASPECT_RATIO=4:3
set PSX_INTERNAL_SCALE=8

if exist "Alundra.exe" (
    start "" "Alundra.exe" -4:3
    exit /b
)
if exist "build-release\Alundra.exe" (
    start "" "build-release\Alundra.exe" -4:3
    exit /b
)
if exist "alundra-recomp\Alundra.exe" (
    cd /d "%~dp0alundra-recomp"
    start "" "Alundra.exe" -4:3
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
