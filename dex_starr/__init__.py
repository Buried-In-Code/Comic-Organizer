from __future__ import annotations

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
    "yaml_setup",
]

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

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


def filter_files(folder: Path, filter_: list[str] = None) -> list[Path]:
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


def list_files(folder: Path) -> list[Path]:
    files = []
    for file in folder.iterdir():
        if file.is_dir():
            files.extend(list_files(folder=file))
        else:
            files.append(file)
    return sorted(files)


def safe_list_get(list_: list[Any], index: int = 0, default: Any = None) -> Any:
    try:
        return list_[index]
    except IndexError:
        return default


def yaml_setup() -> YAML:
    def null_representer(self, data):
        return self.represent_scalar("tag:yaml.org,2002:null", "~")

    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.width = 2147483647
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.representer.add_representer(type(None), null_representer)
    # yaml.emitter.alt_null = '~'
    yaml.version = (1, 2)
    return yaml
