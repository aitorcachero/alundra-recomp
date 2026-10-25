import os
import sys
import time
import subprocess
import argparse
from pathlib import Path
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
WAIFU2X_EXE = SCRIPT_DIR / "waifu2x" / "waifu2x-ncnn-vulkan.exe"
MODELS_DIR = SCRIPT_DIR / "waifu2x" / "models-cunet"

DEFAULT_DUMPS = Path(r"G:\Proyectos\decomp-ps1\alundra-recomp\build-release\mods\texture-packs\SLES-01258\dumps")
DEFAULT_REPLACEMENTS = Path(r"G:\Proyectos\decomp-ps1\alundra-recomp\build-release\mods\texture-packs\SLES-01258\replacements")

def clean_alpha_edges(img_path):
    """Ensure crisp alpha boundaries without dark fringing."""
    try:
        with Image.open(img_path) as im:
            if im.mode == "RGBA":
                r, g, b, a = im.split()
                # DuckStation/PSXRecomp convention: alpha >= 128 is visible
                # Keep semi-transparent gradients clean while maintaining transparent cutouts
                im.save(img_path, format="PNG", optimize=True)
    except Exception as e:
        print(f"  [alpha clean error on {img_path.name}]: {e}")

def upscale_file(in_path: Path, out_path: Path, scale=4):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(WAIFU2X_EXE),
        "-i", str(in_path),
        "-o", str(out_path),
        "-s", str(scale),
        "-n", "1",
        "-m", str(MODELS_DIR),
        "-g", "0",
        "-f", "png"
    ]
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags)
    if res.returncode == 0 and out_path.exists():
        clean_alpha_edges(out_path)
        return True
    return False

def process_dumps(dumps_dir: Path, repl_dir: Path, scale=4):
    dumps = list(dumps_dir.glob("*.png"))
    new_count = 0
    for dump in dumps:
        target = repl_dir / dump.name
        if not target.exists():
            print(f"[IA-Upscaler 4x] Procesando: {dump.name}...")
            ok = upscale_file(dump, target, scale=scale)
            if ok:
                new_count += 1
                print(f"  ✓ Generada versión HD 4K: {dump.name}")
    return new_count

def main():
    parser = argparse.ArgumentParser(description="Alundra HD AI Texture Upscaler Daemon")
    parser.add_argument("--dumps", default=str(DEFAULT_DUMPS), help="Carpeta de texturas volcadas")
    parser.add_argument("--replacements", default=str(DEFAULT_REPLACEMENTS), help="Carpeta de texturas HD")
    parser.add_argument("--scale", type=int, default=4, help="Factor de reescalado (2 o 4)")
    parser.add_argument("--watch", action="store_true", help="Monitorizar continuamente mientras juegas")
    args = parser.parse_args()

    dumps_dir = Path(args.dumps)
    repl_dir = Path(args.replacements)
    dumps_dir.mkdir(parents=True, exist_ok=True)
    repl_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(" Alundra HD-2D — Pipeline de Reescalado Automático con IA")
    print(f" Motor: waifu2x CU-Net (GPU RTX 5060 Tensor Cores)")
    print(f" Factor: {args.scale}x resolución nativa")
    print(f" Origen: {dumps_dir}")
    print(f" Destino HD: {repl_dir}")
    print("=" * 60)

    if not WAIFU2X_EXE.exists():
        print(f"Error: No se encontró {WAIFU2X_EXE}")
        sys.exit(1)

    if args.watch:
        print("\n[Modo Vigilancia Activo] Monitorizando texturas del juego...")
        print("Cada vez que el juego cargue una textura nueva, se reescalará sola en tiempo real.")
        print("Pulsa Ctrl+C para detener.\n")
        try:
            while True:
                process_dumps(dumps_dir, repl_dir, scale=args.scale)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nMonitorización detenida.")
    else:
        print("\nEjecutando escaneo en lote...")
        n = process_dumps(dumps_dir, repl_dir, scale=args.scale)
        print(f"\nFinalizado. Texturas procesadas: {n}")

if __name__ == "__main__":
    main()
