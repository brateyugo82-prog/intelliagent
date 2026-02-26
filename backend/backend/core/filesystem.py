from pathlib import Path
import shutil

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
PLATFORM_SUFFIXES = ("", "_facebook", "_linkedin")

def move_variants(base_id: str, src: Path, dst: Path) -> bool:
    moved = False
    dst.mkdir(parents=True, exist_ok=True)
    for ext in ALLOWED_EXTS:
        for suf in PLATFORM_SUFFIXES:
            f = src / f"{base_id}{suf}{ext}"
            if f.exists():
                shutil.move(str(f), str(dst / f.name))
                moved = True
    return moved

def any_variants_exist(base_id: str, folder: Path) -> bool:
    for ext in ALLOWED_EXTS:
        for suf in PLATFORM_SUFFIXES:
            if (folder / f"{base_id}{suf}{ext}").exists():
                return True
    return False
