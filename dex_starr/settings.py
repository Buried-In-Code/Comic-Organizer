from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

from yamale import YamaleError, make_data, make_schema
from yamale import validate as validate_yaml

from dex_starr import get_config_root, yaml_setup
from dex_starr.console import CONSOLE


class OutputFormatEnum(Enum):
    JSON = auto()
    YAML = auto()

    @staticmethod
    def get(name: str) -> "OutputFormatEnum":
        for entry in OutputFormatEnum:
            if entry.get_title().lower() == name.lower():
                return entry
        return OutputFormatEnum.JSON

    def get_title(self) -> str:
        return self.name.replace("_", " ").title()

    def __lt__(self, other):
        if not isinstance(other, OutputFormatEnum):
            raise NotImplementedError()
        return self.name < other.name


class Settings:
    def __init__(self):
        self.output_format = OutputFormatEnum.JSON
        self.delete_extras = False
        self.resolution_order: List[str] = []
        self.comicvine_api_key: Optional[str] = None
        self.league_api_key: Optional[str] = None
        self.league_client_id: Optional[str] = None
        self.metron_username: Optional[str] = None
        self.metron_password: Optional[str] = None

        root_folder = Path.home().joinpath("Comics").resolve()
        self.import_folder = root_folder / "Import"
        self.processing_folder = root_folder / "Processing"
        self.collection_folder = root_folder / "Collection"

        get_config_root().mkdir(parents=True, exist_ok=True)
        self.settings_file = get_config_root() / "settings.yaml"

        if not self.settings_file.exists():
            self.save()
        else:
            self.load()

        self.import_folder.mkdir(parents=True, exist_ok=True)
        self.processing_folder.mkdir(parents=True, exist_ok=True)
        self.collection_folder.mkdir(parents=True, exist_ok=True)

    def dump(self) -> Dict[str, Any]:
        return {
            "Output Format": self.output_format.get_title(),
            "Delete Extras": self.delete_extras,
            "Resolution Order": self.resolution_order,
            "Folders": {
                "Import": str(self.import_folder),
                "Processing": str(self.processing_folder),
                "Collection": str(self.collection_folder),
            },
            "Comicvine": {"API Key": self.comicvine_api_key},
            "League of Comic Geeks": {
                "API Key": self.league_api_key,
                "Client ID": self.league_client_id,
            },
            "Metron": {"Username": self.metron_username, "Password": self.metron_password},
        }

    def save(self) -> None:
        with self.settings_file.open("w", encoding="UTF-8") as yaml_file:
            yaml_setup().dump(self.dump(), yaml_file)

    def _validate(self) -> bool:
        schema_file = Path("schemas") / "settings.schema.yaml"
        data = make_data(self.settings_file, parser="ruamel")

        try:
            validate_yaml(make_schema(schema_file, parser="ruamel"), data)
            return True
        except YamaleError as ye:
            CONSOLE.print("Validation failed", style="logging.level.error")
            for result in ye.results:
                CONSOLE.print(
                    f"Error validating data '{result.data}' with '{result.schema}'",
                    style="logging.level.error",
                )
                for error in result.errors:
                    CONSOLE.print(f"- {error}", style="logging.level.error")
        return False

    def load(self):
        if not self._validate():
            CONSOLE.print("Shutting down Dex-Starr", style="logging.level.critical")
            exit(1)
        with self.settings_file.open("r", encoding="UTF-8") as stream:
            data = yaml_setup().load(stream)

            self.output_format = OutputFormatEnum.get(data["Output Format"])
            self.delete_extras = data["Delete Extras"]
            self.resolution_order = data["Resolution Order"]

            folders_data = data["Folders"]
            self.import_folder = Path(folders_data["Import"]).resolve()
            self.processing_folder = Path(folders_data["Processing"]).resolve()
            self.collection_folder = Path(folders_data["Collection"]).resolve()

            comicvine_data = data["Comicvine"]
            self.comicvine_api_key = comicvine_data["API Key"]

            league_of_comic_geeks_data = data["League of Comic Geeks"]
            self.league_api_key = league_of_comic_geeks_data["API Key"]
            self.league_client_id = league_of_comic_geeks_data["Client ID"]

            metron_data = data["Metron"]
            self.metron_username = metron_data["Username"]
            self.metron_password = metron_data["Password"]


SETTINGS = Settings()
