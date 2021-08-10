import logging
from pathlib import Path
from typing import Optional, Tuple, List
from zipfile import ZipFile, ZIP_DEFLATED

LOGGER = logging.getLogger(__name__)


def extract_archive(src: Path, dest: Path) -> Optional[Path]:
    dest_folder = dest.joinpath(src.stem)
    if dest_folder.exists():
        LOGGER.error(f"{dest_folder.name} already exists in {dest_folder.parent.name}")
        return None
    dest_folder.mkdir(parents=True)
    LOGGER.debug(f"Started unpacking of `{src}` to `{dest_folder}`")
    with ZipFile(src, 'r') as zip_stream:
        zip_stream.extractall(path=dest_folder)
    LOGGER.debug(f"Finished unpacking of `{src}` to `{dest_folder}`")
    return dest_folder


def create_archive(src: Path, filename: str) -> Optional[Path]:
    files = []
    for index, img_file in enumerate(list_files(src, ('.jpg',))):
        files.append(img_file.rename(src.joinpath(f"{filename}-{index:03}{img_file.suffix}")))
    if src.joinpath('ComicInfo.json').exists():
        files.append(src.joinpath('ComicInfo.json'))
    zip_file = src.parent.joinpath(f"{filename}.cbz")
    if zip_file.exists():
        LOGGER.error(f"{zip_file.name} already exists in {zip_file.parent.name}")
        return None
    LOGGER.debug(f"Started packing of `{zip_file}`")
    with ZipFile(zip_file, 'w', ZIP_DEFLATED) as zip_stream:
        for file in files:
            zip_stream.write(file, file.relative_to(src))
    LOGGER.debug(f"Finished packing of `{zip_file}`")
    return zip_file


def list_files(folder: Path, filter: Tuple[str, ...] = ()) -> List[Path]:
    files = []
    for file in folder.iterdir():
        if file.is_dir():
            files.extend(list_files(file, filter))
        elif file.suffix in filter:
            files.append(file)
    return files
