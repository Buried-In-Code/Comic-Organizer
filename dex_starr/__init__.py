__version__ = "0.2.0"
__all__ = ["__version__", "SETTINGS", "list_files", "del_folder", "sanitize", "merge_dicts", "get_field"]

from pathlib import Path
from typing import Any, Dict, List, Optional

from pathvalidate import sanitize_filename
from ruamel.yaml import YAML


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


from dex_starr.console import ConsoleLog  # noqa
from dex_starr.settings import Settings  # noqa

CONSOLE = ConsoleLog(__name__)
SETTINGS = Settings()


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


def merge_dicts(input_1: Dict[str, Any], input_2: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in input_1.items():
        if isinstance(value, dict):
            if key in input_2:
                input_2[key] = merge_dicts(input_1[key], input_2[key])
    return {**input_1, **input_2}


def get_field(
    pulled_metadata: Dict[str, Any], section: str, field: str, resolve_manually: bool = False
) -> Optional[Any]:
    if len(pulled_metadata[field]) == 1:
        return list(pulled_metadata[field].values())[0]
    if len(pulled_metadata[field]) > 1:
        if len(set(pulled_metadata[field].values())) == 1:
            return list(pulled_metadata[field].values())[0]
        if not resolve_manually:
            for entry in SETTINGS.resolution_order:
                if entry in pulled_metadata[field]:
                    return pulled_metadata[field][entry]
        selected_index = CONSOLE.menu(
            options=[f"{k} - {v}" for k, v in pulled_metadata[field].items()],
            prompt=f"Select {section} {field.replace('_', ' ').title()}",
            none_option=False,
        )
        if selected_index is not None and selected_index != 0:
            return list(pulled_metadata[field].values())[selected_index - 1]
    raise ValueError
