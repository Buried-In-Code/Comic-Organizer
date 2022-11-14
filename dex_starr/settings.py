__all__ = [
    "Settings",
    "GeneralSettings",
    "ComicvineSettings",
    "LeagueOfComicGeeks",
    "MarvelSettings",
    "MetronSettings",
]

from pathlib import Path
from typing import ClassVar, List, Optional

from pydantic import BaseModel, Extra, Field, validator

from dex_starr import get_config_root

try:
    import tomllib as tomlreader  # Python >= 3.11
except ModuleNotFoundError:
    import tomli as tomlreader  # Python < 3.11

import tomli_w as tomlwriter


def to_space_case(value: str) -> str:
    return value.replace("_", " ").title()


class SettingsModel(BaseModel):
    class Config:
        alias_generator = to_space_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.ignore


class MetronSettings(SettingsModel):
    generate_info_file: bool = True
    password: Optional[str] = None
    username: Optional[str] = None


class MarvelSettings(SettingsModel):
    public_key: Optional[str] = None
    private_key: Optional[str] = None


class LeagueOfComicGeeks(SettingsModel):
    api_key: Optional[str] = Field(alias="API Key", default=None)
    client_id: Optional[str] = None


class ComicvineSettings(SettingsModel):
    api_key: Optional[str] = Field(alias="API Key", default=None)


class GeneralSettings(SettingsModel):
    collection_folder: Path = Path.home() / "comics" / "collection"
    generate_comicinfo_file: bool = Field(alias="Generate ComicInfo File", default=True)
    generate_metadata_file: bool = True
    output_format: str = "cbz"
    resolution_order: List[str] = Field(default_factory=list)

    @validator("output_format", pre=True)
    def validate_output_format(cls, v):
        if v in ["cbz", "cb7"]:
            return v
        raise NotImplementedError(f"Unsupported output format: {v}")


class Settings(SettingsModel):
    FILENAME: ClassVar = get_config_root() / "settings.toml"
    general: GeneralSettings = GeneralSettings()
    comicvine: ComicvineSettings = ComicvineSettings()
    league_of_comic_geeks: LeagueOfComicGeeks = Field(
        alias="League of Comic Geeks", default=LeagueOfComicGeeks()
    )
    marvel: MarvelSettings = MarvelSettings()
    metron: MetronSettings = MetronSettings()

    @classmethod
    def load(cls) -> "Settings":
        if not cls.FILENAME.exists():
            Settings().save()
        with cls.FILENAME.open("rb") as stream:
            content = tomlreader.load(stream)
        return Settings(**content)

    def save(self):
        with self.FILENAME.open("wb") as stream:
            content = self.dict(by_alias=False)
            content["general"]["collection_folder"] = str(content["general"]["collection_folder"])
            tomlwriter.dump(content, stream)
