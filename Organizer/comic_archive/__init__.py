from pathlib import Path
from typing import Optional

from .ace_archive import extract_archive as extract_ace_archive
from .rar_archive import extract_archive as extract_rar_archive
from .sevenz_archive import extract_archive as extract_7z_archive
from .tar_archive import extract_archive as extract_tar_archive
from .zip_archive import extract_archive as extract_zip_archive, create_archive


def extract_archive(src: Path, dest: Path) -> Optional[Path]:
    if src.suffix in ['.cbz', '.zip']:
        return extract_zip_archive(src, dest)
    if src.suffix in ['.cb7', '.7z']:
        return extract_7z_archive(src, dest)
    if src.suffix in ['.cba', '.ace']:
        return extract_ace_archive(src, dest)
    if src.suffix in ['.cbr', '.rar']:
        return extract_rar_archive(src, dest)
    if src.suffix in ['.cbt', '.tar']:
        return extract_tar_archive(src, dest)
    return None
