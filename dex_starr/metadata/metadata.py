__all__ = ["Publisher", "Series", "Creator", "StoryArc", "Issue", "Metadata"]

import json
import re
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel as PyModel
from pydantic import Extra, Field

from .. import __version__, yaml_setup


def sanitize(dirty: str) -> str:
    dirty = re.sub(r"[^0-9a-zA-Z& ]+", "", dirty.replace("-", " "))
    dirty = " ".join(dirty.split())
    return dirty.replace(" ", "-")


def to_camel_case(value: str) -> str:
    temp = value.replace("_", " ").title().replace(" ", "")
    return temp[0].lower() + temp[1:]


class BaseModel(PyModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore


class Publisher(BaseModel):
    imprint: Optional[str] = None
    sources: Dict[str, int] = Field(default_factory=dict)
    title: str

    @property
    def file_name(self) -> str:
        return sanitize(self.title)

    def __lt__(self, other):
        if not isinstance(other, Publisher):
            raise NotImplementedError()
        return self.title < other.title


class Series(BaseModel):
    sources: Dict[str, int] = Field(default_factory=dict)
    start_year: Optional[int] = Field(default=None, gt=1900)
    title: str
    volume: int = Field(default=1, gt=0)

    @property
    def file_name(self) -> str:
        if self.volume <= 1:
            return sanitize(self.title)
        return sanitize(f"{self.title} v{self.volume}")

    def __lt__(self, other):
        if not isinstance(other, Series):
            raise NotImplementedError()
        if self.title != other.title:
            return self.title < other.title
        if self.volume != other.volume:
            return self.volume < other.volume
        return self.start_year < other.start_year


class Creator(BaseModel):
    name: str
    roles: List[str] = Field(default_factory=list)

    def __lt__(self, other):
        if not isinstance(other, Creator):
            raise NotImplementedError()
        return self.name < other.name


class StoryArc(BaseModel):
    title: str
    number: Optional[int] = None

    def __lt__(self, other):
        if not isinstance(other, StoryArc):
            raise NotImplementedError()
        if self.title != other.title:
            return self.title < other.title
        return self.number < other.number


class Issue(BaseModel):
    characters: List[str] = Field(default_factory=list)
    cover_date: Optional[date] = None
    creators: List[Creator] = Field(default_factory=list)
    format: str = "Comic"
    genres: List[str] = Field(default_factory=list)
    language: str = "en"
    locations: List[str] = Field(default_factory=list)
    number: str
    page_count: Optional[int] = Field(default=None, gt=0)
    sources: Dict[str, int] = Field(default_factory=dict)
    store_date: Optional[date] = None
    story_arcs: List[StoryArc] = Field(default_factory=list)
    summary: Optional[str] = None
    teams: List[str] = Field(default_factory=list)
    title: Optional[str] = None

    @property
    def file_name(self) -> str:
        if self.format == "Annual":
            return f"-Annual-#{self.number.zfill(2)}"
        if self.format == "Digital Chapter":
            return f"-Chapter-#{self.number.zfill(2)}"
        if self.format == "Hardcover":
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-HC"
        if self.format == "Trade Paperback":
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-TP"
        return f"-#{self.number.zfill(3)}"

    def __lt__(self, other):
        if not isinstance(other, Issue):
            raise NotImplementedError()
        if self.format != other.format:
            return self.format < other.format
        if self.number != other.number:
            return self.number < other.number
        return self.cover_date < other.cover_date


class Metadata(BaseModel):
    publisher: Publisher
    series: Series
    issue: Issue
    notes: Optional[str] = None

    @staticmethod
    def from_file(comic_info_file: Path) -> "Metadata":
        with comic_info_file.open("r", encoding="UTF-8") as info_file:
            content = yaml_setup().load(info_file)
            return Metadata(**content["data"])

    def to_file(self, comic_info_file: Path):
        with comic_info_file.open("w", encoding="UTF-8") as info_file:
            json.dump(
                {"data": self.dict(by_alias=True), "meta": generate_meta()},
                info_file,
                sort_keys=True,
                default=str,
                indent=2,
                ensure_ascii=False,
            )

    def __lt__(self, other):
        if not isinstance(other, Metadata):
            raise NotImplementedError()
        if self.publisher != other.publisher:
            return self.publisher < other.publisher
        if self.series != other.series:
            return self.series < other.series
        return self.issue < other.issue


def generate_meta() -> Dict[str, str]:
    return {"date": date.today().isoformat(), "tool": {"name": "Dex-Starr", "version": __version__}}
