__version__ = "2022.1.0"
__all__ = [
    "__version__",
    "SUPPORTED_IMAGE_EXTENSIONS",
    "SUPPORTED_FILE_EXTENSIONS",
    "SUPPORTED_INFO_FILES",
    "del_folder",
    "get_cache_root",
    "get_config_root",
    "get_project_root",
    "list_files",
    "safe_list_get",
    "setup_logging",
]

import logging
from pathlib import Path
from typing import Any, List

from natsort import humansorted as sorted
from natsort import ns
from rich.logging import RichHandler

from dex_starr.console import CONSOLE

SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
SUPPORTED_FILE_EXTENSIONS = [".cbz", ".cbr", ".cbt", ".cb7"]
SUPPORTED_INFO_FILES = ["Metadata.json", "MetronInfo.xml", "ComicInfo.xml"]


def del_folder(folder: Path):
    for child in folder.iterdir():
        if child.is_file():
            child.unlink(missing_ok=True)
        else:
            del_folder(folder=child)
    folder.rmdir()


def list_files(folder: Path, filter_: List[str] = None) -> List[Path]:
    if filter_ is None:
        filter_ = []
    files = []
    for file in folder.iterdir():
        if file.is_dir():
            files.extend(list_files(folder=file, filter_=filter_))
        else:
            if filter_ and file.suffix in filter_:
                files.append(file)
            elif not filter_:
                files.append(file)
    return sorted(files, alg=ns.NA | ns.G | ns.P)


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_config_root() -> Path:
    root = Path.home() / ".config" / "dex-starr"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_cache_root() -> Path:
    root = Path.home() / ".cache" / "dex-starr"
    root.mkdir(parents=True, exist_ok=True)
    return root


def safe_list_get(list_: List[Any], index: int = 0, default: Any = None) -> Any:
    try:
        return list_[index]
    except IndexError:
        return default


def setup_logging(debug: bool = False):
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                omit_repeated_times=False,
                console=CONSOLE,
            )
        ],
    )
