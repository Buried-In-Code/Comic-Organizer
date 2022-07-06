import json
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from dex_starr import __version__, yaml_setup
from dex_starr.metadata import sanitize


def to_camel_case(value: str) -> str:
    temp = value.replace("_", " ").title().replace(" ", "")
    return temp[0].lower() + temp[1:]


class FormatEnum(Enum):
    ANNUAL = "Annual"
    COMIC = "Comic"
    DIGITAL_CHAPTER = "Digital Chapter"
    HARDCOVER = "Hardcover"
    TRADE_PAPERBACK = "Trade Paperback"
    UNSET = "Unset"


class Publisher(BaseModel):
    imprint: Optional[str] = None
    sources: Dict[str, int] = Field(default_factory=dict)
    title: str

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True

    @property
    def file_name(self) -> str:
        return sanitize(self.title)


class Series(BaseModel):
    sources: Dict[str, int] = Field(default_factory=dict)
    start_year: Optional[int] = None
    title: str
    volume: int = 1

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True

    @property
    def file_name(self) -> str:
        if self.volume <= 1:
            return sanitize(self.title)
        return sanitize(f"{self.title} v{self.volume}")


class Issue(BaseModel):
    characters: List[str] = Field(default_factory=list)
    cover_date: Optional[date] = None
    creators: Dict[str, List[str]] = Field(default_factory=dict)
    format: FormatEnum
    genres: List[str] = Field(default_factory=list)
    language_iso: Optional[str] = None
    locations: List[str] = Field(default_factory=list)
    number: str
    page_count: Optional[int] = None
    sources: Dict[str, int] = Field(default_factory=dict)
    store_date: Optional[date] = None
    story_arcs: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    teams: List[str] = Field(default_factory=list)
    title: Optional[str] = None

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True

    @property
    def file_name(self) -> str:
        if self.format == FormatEnum.ANNUAL:
            return f"-Annual-#{self.number.zfill(2)}"
        if self.format == FormatEnum.DIGITAL_CHAPTER:
            return f"-Chapter-#{self.number.zfill(2)}"
        if self.format == FormatEnum.HARDCOVER:
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-HC"
        if self.format == FormatEnum.TRADE_PAPERBACK:
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-TP"
        return f"-#{self.number.zfill(3)}"


class Metadata(BaseModel):
    issue: Issue
    notes: Optional[str] = None
    publisher: Publisher
    series: Series

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True

    @staticmethod
    def from_file(comic_info_file: Path) -> "Metadata":
        with comic_info_file.open("r", encoding="UTF-8") as info_file:
            if comic_info_file.suffix == ".json":
                content = json.load(info_file)
            elif comic_info_file.suffix == ".yaml":
                content = yaml_setup().load(info_file)
            else:
                raise NotImplementedError(f"Unsupported extension found: {comic_info_file.suffix}")
            if "comicInfo" in content:
                return Metadata(**content["comicInfo"])
            return Metadata(**content["metadata"])

    def to_file(self, comic_info_file: Path):
        with comic_info_file.open("w", encoding="UTF-8") as info_file:
            json.dump(
                {"metadata": self.dict(by_alias=True), "meta": generate_meta()},
                info_file,
                sort_keys=True,
                default=str,
                indent=2,
                ensure_ascii=False,
            )


def generate_meta() -> Dict[str, str]:
    return {"date": date.today().isoformat(), "tool": {"name": "Dex-Starr", "version": __version__}}
