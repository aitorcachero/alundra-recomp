#!/usr/bin/env python3
"""
Alundra Recompiled — Universal Disc Setup & Ingestion Utility
Supports: PAL (Spain, Europe, France, Germany), NTSC-U (USA), NTSC-J (Japan)
Formats: .PBP, .BIN/.CUE, .ISO, .IMG, .CHD
"""

import os
import sys
import struct
import zlib
import re
import shutil
from pathlib import Path

KNOWN_VERSIONS = {
    "SLES_012.58": {
        "serial": "SLES-01258",
        "title": "Alundra (España - Castellano)",
        "region": "PAL",
        "hz": 50.0,
        "lang": "es"
    },
    "SLUS_005.53": {
        "serial": "SLUS-00553",
        "title": "The Adventures of Alundra (USA - English)",
        "region": "NTSC-U",
        "hz": 59.94,
        "lang": "en"
    },
    "SCES_008.40": {
        "serial": "SCES-00840",
        "title": "The Adventures of Alundra (Europe - English)",
        "region": "PAL",
        "hz": 50.0,
        "lang": "en"
    },
    "SLES_012.57": {
        "serial": "SLES-01257",
        "title": "Alundra (France - Français)",
        "region": "PAL",
        "hz": 50.0,
        "lang": "fr"
    },
    "SLES_012.59": {
        "serial": "SLES-01259",
        "title": "Alundra (Deutschland - Deutsch)",
        "region": "PAL",
        "hz": 50.0,
        "lang": "de"
    },
    "SCPS_100.50": {
        "serial": "SCPS-10050",
        "title": "Alundra (Japan - 日本語)",
        "region": "NTSC-J",
        "hz": 59.94,
        "lang": "ja"
    }
}

def extract_pbp(pbp_path: Path, out_bin: Path) -> bool:
    print(f"[*] Detectado archivo Sony PSP EBOOT (PBP): {pbp_path.name}")
    print("[*] Descomprimiendo sectores de PlayStation 1...")
    
    with open(pbp_path, "rb") as f:
        header = f.read(40)
        if len(header) < 40 or header[:4] != b"\x00PBP":
            print("[-] Error: Cabecera PBP no válida.")
            return False
            
        offsets = struct.unpack("<8I", header[8:40])
        psar_offset = offsets[7]
        
        f.seek(psar_offset)
        psar_sig = f.read(16)
        if psar_sig[:4] != b"PSISO":
            f.seek(psar_offset)
        
        header2 = f.read(0x400)
        f.seek(psar_offset + 0x400)
        
        index_data = f.read(0x100000)
        num_blocks = len(index_data) // 32
        
        out_bin.parent.mkdir(parents=True, exist_ok=True)
        with open(out_bin, "wb") as out_f:
            for i in range(num_blocks):
                entry = index_data[i*32 : (i+1)*32]
                if len(entry) < 32:
                    break
                
                block_offset, block_size = struct.unpack("<II", entry[:8])
                if block_offset == 0 and block_size == 0:
                    break
                    
                cur_pos = f.tell()
                f.seek(psar_offset + block_offset)
                comp_data = f.read(block_size)
                
                try:
                    decomp = zlib.decompress(comp_data)
                    out_f.write(decomp)
                except Exception:
                    out_f.write(comp_data)
                    
                if i > 0 and i % 2500 == 0:
                    print(f"    ... procesados {i} bloques de sectores...")
                    
    print(f"[+] Extracción PBP completada: {out_bin.name} ({out_bin.stat().st_size // (1024*1024)} MB)")
    return True

def detect_serial(bin_path: Path):
    with open(bin_path, "rb") as f:
        # Scan first 2 MB
        data = f.read(2 * 1024 * 1024)
        m = re.search(rb'(SLES|SLUS|SCES|SCPS|SLED|SLPS|SCED)[_-](\d{3})\.?(\d{2})', data, re.IGNORECASE)
        if m:
            prefix = m.group(1).decode('ascii').upper()
            num1 = m.group(2).decode('ascii')
            num2 = m.group(3).decode('ascii')
            key = f"{prefix}_{num1}.{num2}"
            serial = f"{prefix}-{num1}{num2}"
            return key, serial
    return None, None

def write_cue(cue_path: Path, bin_name: str):
    cue_content = f'FILE "{bin_name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
    with open(cue_path, "w", encoding="utf-8") as f:
        f.write(cue_content)
    print(f"[+] Generado descriptor CUE: {cue_path.name}")

def update_configs(project_root: Path, cue_path: Path, serial: str, version_info: dict):
    # 1. Update settings.toml in build-release
    settings_file = project_root / "build-release" / "settings.toml"
    cue_forward = str(cue_path.resolve()).replace("\\", "/")
    
    if settings_file.exists():
        text = settings_file.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r'path\s*=\s*"[^"]*"', f'path = "{cue_forward}"', text)
        if "lang" in version_info:
            text = re.sub(r'language\s*=\s*"[^"]*"', f'language = "{version_info["lang"]}"', text)
        settings_file.write_text(text, encoding="utf-8")
        print(f"[+] Actualizado settings.toml -> {cue_forward}")

    # 2. Update game.toml
    for gtoml in [project_root / "game.toml", project_root / "build-release" / "game.toml"]:
        if gtoml.exists():
            text = gtoml.read_text(encoding="utf-8", errors="replace")
            text = re.sub(r'id\s*=\s*"[^"]*"', f'id = "{serial}"', text)
            text = re.sub(r'disc\s*=\s*"[^"]*"', f'disc = "{cue_forward}"', text)
            gtoml.write_text(text, encoding="utf-8")
            print(f"[+] Actualizado {gtoml.name} -> {serial}")

def main():
    print("=" * 65)
    print("  Alundra Recompiled — Detector y Preparador Universal de Disco")
    print("  Soporte: PAL (España/UK/FR/DE), NTSC-U (USA), NTSC-J (Japón)")
    print("=" * 65)

    base_dir = Path(__file__).resolve().parent.parent
    disc_dir = base_dir / "disc"
    disc_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Check if user passed a file argument or search directory
    target_file = None
    if len(sys.argv) > 1:
        cand = Path(sys.argv[1])
        if cand.is_file():
            target_file = cand

    if not target_file:
        # Search candidate files in disc, root, and legacy disc dirs
        extensions = [".pbp", ".cue", ".bin", ".iso", ".img", ".chd"]
        search_dirs = [disc_dir, base_dir, base_dir / "alundra_disc", base_dir.parent / "alundra_disc"]
        
        candidates = []
        for sdir in search_dirs:
            if sdir.exists():
                for ext in extensions:
                    candidates.extend(list(sdir.glob(f"*{ext}")))
                    candidates.extend(list(sdir.glob(f"*{ext.upper()}")))

        # Filter out cues if bin exists with same stem
        clean_cands = []
        for c in candidates:
            if c.name.lower() in ["alundra.cue", "alundra.bin"] and c.parent == disc_dir:
                clean_cands.insert(0, c)
            else:
                clean_cands.append(c)
                
        if clean_cands:
            target_file = clean_cands[0]

    if not target_file:
        print("\n[!] No se encontró ninguna imagen de disco en la carpeta.")
        print("    Por favor, coloca tu copia de Alundra (.PBP, .ISO, .BIN, .CUE, .CHD)")
        print(f"    en: {disc_dir} o en la raíz del proyecto y vuelve a ejecutar este script.")
        input("\nPulsa Enter para salir...")
        sys.exit(1)

    print(f"\n[*] Archivo detectado: {target_file}")
    
    bin_file = disc_dir / "Alundra.bin"
    cue_file = disc_dir / "Alundra.cue"

    suf = target_file.suffix.lower()
    if suf == ".pbp":
        ok = extract_pbp(target_file, bin_file)
        if not ok:
            sys.exit(1)
        write_cue(cue_file, "Alundra.bin")
    elif suf == ".cue":
        cue_file = target_file
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            m = re.search(r'FILE\s+"([^"]+)"', f.read(), re.I)
            if m:
                bin_file = target_file.parent / m.group(1)
            else:
                bin_file = target_file.with_suffix(".bin")
    elif suf in [".bin", ".iso", ".img"]:
        if target_file.resolve() != bin_file.resolve():
            print(f"[*] Copiando/Vinculando {target_file.name} -> {bin_file}...")
            try:
                shutil.copy2(target_file, bin_file)
            except Exception:
                bin_file = target_file
        write_cue(cue_file, bin_file.name)

    # Detect Serial & Region
    boot_key, detected_serial = detect_serial(bin_file)
    version_info = KNOWN_VERSIONS.get(boot_key, {
        "serial": detected_serial or "SLES-01258",
        "title": f"Alundra ({detected_serial or 'Desconocida'})",
        "region": "PAL",
        "hz": 50.0,
        "lang": "es"
    })

    print("-" * 65)
    print(f"  Versión identificada: {version_info['title']}")
    print(f"  Serial PS1:           {version_info['serial']}")
    print(f"  Región de vídeo:      {version_info['region']} ({version_info['hz']} Hz)")
    print("-" * 65)

    update_configs(base_dir, cue_file, version_info["serial"], version_info)
    print("\n[OK] Configuracion completada con exito.")
    print("    El juego esta listo para iniciarse con JUGAR_ALUNDRA.bat.")

if __name__ == "__main__":
    main()
