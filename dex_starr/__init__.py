from importlib.metadata import version

__version__ = version(__package__)
__all__ = [
    "__version__",
    "del_folder",
    "get_config_root",
    "get_project_root",
    "INFO_EXTENSIONS",
    "list_files",
    "sanitize",
    "yaml_setup",
]

from pathlib import Path
from typing import List

from pathvalidate import sanitize_filename
from ruamel.yaml import YAML

INFO_EXTENSIONS = [".json", ".xml", ".yaml"]


def yaml_setup() -> YAML:
    def null_representer(self, data):
        return self.represent_scalar("tag:yaml.org,2002:null", "~")

    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.width = 2147483647
    yaml.representer.add_representer(type(None), null_representer)
    # yaml.emitter.alt_null = '~'
    yaml.version = (1, 2)
    return yaml


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_config_root() -> Path:
    return Path.home() / ".config" / "dex-starr"


def list_files(folder: Path, filter_: List[str] = None) -> List[Path]:
    if filter_ is None:
        filter_ = []
    files = []
    for file in folder.iterdir():
        if file.is_dir():
            files.extend(list_files(folder=file, filter_=filter_))
        elif file.suffix in filter_:
            files.append(file)
    return files


def del_folder(folder: Path):
    for child in folder.iterdir():
        if child.is_file():
            child.unlink(missing_ok=True)
        else:
            del_folder(folder=child)
    folder.rmdir()


def sanitize(filename: str) -> str:
    return " ".join(sanitize_filename(filename).replace("-", " ").split()).replace(" ", "-")
