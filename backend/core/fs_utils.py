from pathlib import Path
import shutil

ALLOWED_EXTS = (".png", ".jpg", ".jpeg", ".webp")
PLATFORM_SUFFIXES = ("", "_facebook", "_linkedin")

def move_variants(base_id: str, src_dir: Path, dst_dir: Path) -> bool:
    moved = False
    dst_dir.mkdir(parents=True, exist_ok=True)

    for ext in ALLOWED_EXTS:
        for suffix in PLATFORM_SUFFIXES:
            src = src_dir / f"{base_id}{suffix}{ext}"
            if src.exists():
                shutil.move(str(src), str(dst_dir / src.name))
                moved = True

    return moved
