__version__ = "0.2.0"
__all__ = [
    "__version__",
    "IMAGE_EXTENSIONS",
    "SUPPORTED_EXTENSIONS",
    "SUPPORTED_INFO_FILES",
    "del_folder",
    "filter_files",
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

from rich.logging import RichHandler

from dex_starr.console import CONSOLE

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
SUPPORTED_EXTENSIONS = [".cbz", ".cbr", ".cbt", ".cb7"]
SUPPORTED_INFO_FILES = ["Metadata.json", "MetronInfo.xml", "ComicInfo.xml"]


def del_folder(folder: Path):
    for child in folder.iterdir():
        if child.is_file():
            child.unlink(missing_ok=True)
        else:
            del_folder(folder=child)
    folder.rmdir()


def filter_files(folder: Path, filter_: List[str] = None) -> List[Path]:
    if filter_ is None:
        filter_ = []
    files = []
    for file in folder.iterdir():
        if file.is_dir():
            files.extend(filter_files(folder=file, filter_=filter_))
        elif file.suffix in filter_:
            files.append(file)
    return sorted(files)


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


def list_files(folder: Path) -> List[Path]:
    files = []
    for file in folder.iterdir():
        if file.is_dir():
            files.extend(list_files(folder=file))
        else:
            files.append(file)
    return sorted(files)


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
                log_time_format="[%Y-%m-%d %H:%M:%S]",
                omit_repeated_times=False,
                console=CONSOLE,
            )
        ],
    )
