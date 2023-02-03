__version__ = "0.2.0"
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
import os
from pathlib import Path
from typing import Any, List

from natsort import humansorted as sorted
from natsort import ns
from rich.logging import RichHandler
from rich.traceback import install

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


def get_cache_root() -> Path:
    cache_home = os.getenv("XDG_CACHE_HOME", default=str(Path.home() / ".cache"))
    folder = Path(cache_home).resolve() / "dex-starr"
    folder.mkdir(exist_ok=True, parents=True)
    return folder


def get_config_root() -> Path:
    config_home = os.getenv("XDG_CONFIG_HOME", default=str(Path.home() / ".config"))
    folder = Path(config_home).resolve() / "dex-starr"
    folder.mkdir(exist_ok=True, parents=True)
    return folder


def get_data_root() -> Path:
    data_home = os.getenv("XDG_DATA_HOME", default=str(Path.home() / ".local" / "share"))
    folder = Path(data_home).resolve() / "dex-starr"
    folder.mkdir(exist_ok=True, parents=True)
    return folder


def get_project_root() -> Path:
    return Path(__file__).parent.parent


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


def safe_list_get(list_: List[Any], index: int = 0, default: Any = None) -> Any:
    try:
        return list_[index]
    except IndexError:
        return default


def setup_logging(debug: bool = False) -> None:
    install(show_locals=True, max_frames=5, console=CONSOLE)

    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)-8s] {%(name)s} | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                omit_repeated_times=False,
                show_level=False,
                show_time=False,
                show_path=False,
                console=CONSOLE,
            ),
        ],
    )
