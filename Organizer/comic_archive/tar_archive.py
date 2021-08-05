import logging
from pathlib import Path
from typing import Optional

import patoolib

LOGGER = logging.getLogger(__name__)


def extract_archive(src: Path, dest: Path) -> Optional[Path]:
    process_folder = dest.joinpath(src.stem)
    if process_folder.exists():
        LOGGER.error(f"{process_folder.name} already exists in {process_folder.parent.name}")
        return None
    process_folder.mkdir(parents=True)
    LOGGER.debug(f"Started unpacking of `{src}` to `{process_folder}`")
    output = patoolib.extract_archive(str(src), outdir=str(process_folder), verbosity=-1, interactive=False)
    LOGGER.debug(f"Finished unpacking of `{src}` to `{process_folder}`")
    return Path(output).resolve()
