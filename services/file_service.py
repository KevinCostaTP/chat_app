# services/file_service.py

import shutil
import os
from pathlib import Path

UPLOADS_DIR = Path("assets/uploads")


def ensure_uploads_dir():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def save_file(source_path: str) -> str:
    try:
        source = Path(source_path)
        if not source.exists():
            return None
        destination = UPLOADS_DIR / source.name
        counter = 1
        while destination.exists():
            destination = UPLOADS_DIR / f"{source.stem}_{counter}{source.suffix}"
            counter += 1
        shutil.copy2(source_path, destination)
        return str(destination)
    except Exception as e:
        print(f"Erro ao guardar ficheiro: {e}")
        return None


def is_image(file_path: str) -> bool:
    if not file_path:
        return False
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    return Path(file_path).suffix.lower() in image_extensions


def get_file_name(file_path: str) -> str:
    return Path(file_path).name


def get_file_size(file_path: str) -> str:
    try:
        size = os.path.getsize(file_path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "Tamanho desconhecido"