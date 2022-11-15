__all__ = ["Publisher", "Series", "Creator", "StoryArc", "Issue", "Metadata"]

import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel as PyModel
from pydantic import Extra, Field

from dex_starr import __version__
from dex_starr.schemas.comic_info.enums import ComicPageType
from dex_starr.schemas.metadata.enums import FormatType, Genre, Role

LOGGER = logging.getLogger(__name__)


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
    roles: List[Role] = Field(default_factory=list)

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

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Issue(BaseModel):
    characters: List[str] = Field(default_factory=list)
    cover_date: Optional[date] = None
    creators: List[Creator] = Field(default_factory=list)
    format: FormatType = FormatType.COMIC
    genres: List[Genre] = Field(default_factory=list)
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
        if self.format == FormatType.ANNUAL:
            return f"-Annual-#{self.number.zfill(2)}"
        if self.format == FormatType.DIGITAL_CHAPTER:
            return f"-Chapter-#{self.number.zfill(2)}"
        if self.format == FormatType.HARDCOVER:
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-HC"
        if self.format == FormatType.TRADE_PAPERBACK:
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-TP"
        if self.format == FormatType.GRAPHIC_NOVEL:
            return f"-{self.title}" if self.title else ""
        return f"-#{self.number.zfill(3)}"

    def __lt__(self, other):
        if not isinstance(other, Issue):
            raise NotImplementedError()
        if self.format != other.format:
            return self.format < other.format
        if self.number != other.number:
            return self.number < other.number
        return self.cover_date < other.cover_date


class Page(BaseModel):
    image: int
    page_type: ComicPageType = ComicPageType.STORY
    double_page: bool = False
    image_size: int = 0
    key: Optional[str] = None
    bookmark: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None


class Metadata(BaseModel):
    publisher: Publisher
    series: Series
    issue: Issue
    pages: List[Page] = Field(default_factory=list)
    notes: Optional[str] = None

    @staticmethod
    def from_file(metadata_file: Path) -> "Metadata":
        with metadata_file.open("r", encoding="UTF-8") as stream:
            content = json.load(stream)
            return Metadata(**content["data"])

    def to_file(self, metadata_file: Path):
        with metadata_file.open("w", encoding="UTF-8") as stream:
            json.dump(
                {"data": self.dict(by_alias=True), "meta": generate_meta()},
                stream,
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
