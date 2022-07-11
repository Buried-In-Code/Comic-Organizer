from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from dex_starr import get_config_root, yaml_setup

_settings_file = get_config_root() / "settings.yaml"


def to_space_case(value: str) -> str:
    return value.replace("_", " ").title()


class LeagueOfComicGeeks(BaseModel):
    api_key: Optional[str] = Field(alias="API Key", default=None)
    client_id: Optional[str] = None

    class Config:
        alias_generator = to_space_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.ignore


class MetronSettings(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    generate_info_file: bool = True

    class Config:
        alias_generator = to_space_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.ignore


class ComicvineSettings(BaseModel):
    api_key: Optional[str] = Field(alias="API Key", default=None)

    class Config:
        alias_generator = to_space_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.ignore


class GeneralSettings(BaseModel):
    generate_metadata_file: bool = True
    generate_comic_info_file: bool = True
    resolution_order: List[str] = Field(default_factory=list)
    collection_folder: Path = Path.home() / "comics" / "collection"

    class Config:
        alias_generator = to_space_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.ignore


class Settings(BaseModel):
    general: GeneralSettings = GeneralSettings()
    comicvine: ComicvineSettings = ComicvineSettings()
    metron: MetronSettings = MetronSettings()
    league_of_comic_geeks: LeagueOfComicGeeks = Field(
        alias="League of Comic Geeks", default=LeagueOfComicGeeks()
    )

    class Config:
        alias_generator = to_space_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.ignore

    @staticmethod
    def load() -> "Settings":
        if not _settings_file.exists():
            Settings().save()
        with _settings_file.open("r", encoding="UTF-8") as stream:
            content = yaml_setup().load(stream)
        return Settings(**content)

    def save(self):
        with _settings_file.open("w", encoding="UTF-8") as stream:
            content = self.dict(by_alias=True)
            content["General"]["Collection Folder"] = str(content["General"]["Collection Folder"])
            yaml_setup().dump(content, stream)
