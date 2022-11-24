__all__ = [
    "Resource",
    "Publisher",
    "Series",
    "Creator",
    "StoryArc",
    "Issue",
    "Page",
    "Metadata",
]

import json
import re
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, validator

from dex_starr import __version__
from dex_starr.models import CamelModel
from dex_starr.models.metadata.enums import Format, Genre, PageType, Role, Source


def sanitize(dirty: str) -> str:
    dirty = re.sub(r"[^0-9a-zA-Z& ]+", "", dirty.replace("-", " "))
    dirty = " ".join(dirty.split())
    return dirty.replace(" ", "-")


class Resource(CamelModel):
    source: Source
    value: int

    @validator("source", pre=True)
    def to_source_enum(cls, v) -> Source:
        if isinstance(v, Source):
            return v
        return Source.load(str(v))

    def __lt__(self, other):
        if not isinstance(other, Resource):
            raise NotImplementedError()
        return self.source < other.source

    def __eq__(self, other):
        if not isinstance(other, Resource):
            raise NotImplementedError()
        return self.source == other.source

    def __hash__(self):
        return hash((type(self), self.source))


class Publisher(CamelModel):
    imprint: Optional[str] = None
    resources: List[Resource] = Field(default_factory=list)
    title: str

    @property
    def file_name(self) -> str:
        return sanitize(self.title)

    def __lt__(self, other):
        if not isinstance(other, Publisher):
            raise NotImplementedError()
        return self.title < other.title

    def __eq__(self, other):
        if not isinstance(other, Publisher):
            raise NotImplementedError()
        return self.title == other.title

    def __hash__(self):
        return hash((type(self), self.title))


class Series(CamelModel):
    resources: List[Resource] = Field(default_factory=list)
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

    def __eq__(self, other):
        if not isinstance(other, Series):
            raise NotImplementedError()
        return (self.title, self.volume, self.start_year) == (
            other.title,
            other.volume,
            other.start_year,
        )

    def __hash__(self):
        return hash((type(self), self.title, self.volume, self.start_year))


class Creator(CamelModel):
    name: str
    roles: List[Role] = Field(default_factory=list)

    @validator("roles", pre=True, each_item=True)
    def to_role_enum(cls, v) -> Role:
        if isinstance(v, Role):
            return v
        return Role.load(str(v))

    def __lt__(self, other):
        if not isinstance(other, Creator):
            raise NotImplementedError()
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, Creator):
            raise NotImplementedError()
        return self.name == other.name

    def __hash__(self):
        return hash((type(self), self.name))


class StoryArc(CamelModel):
    title: str
    number: Optional[int] = None

    def __lt__(self, other):
        if not isinstance(other, StoryArc):
            raise NotImplementedError()
        if self.title != other.title:
            return self.title < other.title
        return self.number < other.number

    def __eq__(self, other):
        if not isinstance(other, StoryArc):
            raise NotImplementedError()
        return (self.title, self.number) == (other.title, other.number)

    def __hash__(self):
        return hash((type(self), self.title, self.number))


class Issue(CamelModel):
    characters: List[str] = Field(default_factory=list)
    cover_date: Optional[date] = None
    creators: List[Creator] = Field(default_factory=list)
    format: Format = Format.COMIC
    genres: List[Genre] = Field(default_factory=list)
    language: str = "en"
    locations: List[str] = Field(default_factory=list)
    number: str
    page_count: int = Field(default=0, ge=0)
    resources: List[Resource] = Field(default_factory=list)
    store_date: Optional[date] = None
    story_arcs: List[StoryArc] = Field(default_factory=list)
    summary: Optional[str] = None
    teams: List[str] = Field(default_factory=list)
    title: Optional[str] = None

    @validator("format", pre=True)
    def to_format_enum(cls, v) -> Format:
        if isinstance(v, Format):
            return v
        return Format.load(str(v))

    @validator("genres", pre=True, each_item=True)
    def to_genre_enum(cls, v) -> Genre:
        if isinstance(v, Genre):
            return v
        return Genre.load(str(v))

    @property
    def file_name(self) -> str:
        if self.format == Format.ANNUAL:
            return f"-Annual-#{self.number.zfill(2)}"
        if self.format == Format.DIGITAL_CHAPTER:
            return f"-Chapter-#{self.number.zfill(2)}"
        if self.format == Format.HARDCOVER:
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-HC"
        if self.format == Format.TRADE_PAPERBACK:
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-TP"
        if self.format == Format.GRAPHIC_NOVEL:
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

    def __eq__(self, other):
        if not isinstance(other, Issue):
            raise NotImplementedError()
        return (self.format, self.number, self.cover_date) == (
            other.format,
            other.number,
            other.cover_date,
        )

    def __hash__(self):
        return hash((type(self), self.format, self.number, self.cover_date))


class Page(CamelModel):
    image: int
    page_type: PageType = PageType.STORY
    double_page: bool = False
    key: Optional[str] = None
    bookmark: Optional[str] = None
    image_size: int = Field(default=0, ge=0)
    image_width: int = Field(default=0, ge=0)
    image_height: int = Field(default=0, ge=0)

    @validator("page_type", pre=True)
    def to_page_type_enum(cls, v) -> PageType:
        if isinstance(v, PageType):
            return v
        return PageType.load(str(v))

    def __lt__(self, other):
        if not isinstance(other, Page):
            raise NotImplementedError()
        return self.image < other.image

    def __eq__(self, other):
        if not isinstance(other, Page):
            raise NotImplementedError()
        return self.image == other.image

    def __hash__(self):
        return hash((type(self), self.image))


class Metadata(CamelModel):
    publisher: Publisher
    series: Series
    issue: Issue
    pages: List[Page] = Field(default_factory=list)
    notes: Optional[str] = None

    @staticmethod
    def from_file(metadata_file: Path) -> "Metadata":
        with metadata_file.open("r", encoding="UTF-8") as stream:
            content = json.load(stream)
            return Metadata(**content["content"])

    def to_file(self, metadata_file: Path):
        content = self.dict(by_alias=True)
        content = clean_contents(content)

        with metadata_file.open("w", encoding="UTF-8") as stream:
            json.dump(
                {"content": content, "meta": generate_meta()},
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

    def __eq__(self, other):
        if not isinstance(other, Metadata):
            raise NotImplementedError()
        return (self.publisher, self.series, self.issue) == (
            other.publisher,
            other.series,
            other.issue,
        )

    def __hash__(self):
        return hash((type(self), self.publisher, self.series, self.issue))


def generate_meta() -> Dict[str, str]:
    return {"date": date.today().isoformat(), "tool": {"name": "Dex-Starr", "version": __version__}}


def clean_contents(content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in content.copy().items():
        if isinstance(key, Enum):
            content[str(key)] = value
            del content[key]
        if isinstance(value, Enum):
            content[key] = str(value)
        elif isinstance(value, dict):
            content[key] = clean_contents(value)
        elif isinstance(value, list):
            for index, entry in enumerate(value):
                if isinstance(entry, Enum):
                    content[key][index] = str(entry)
                elif isinstance(entry, dict):
                    content[key][index] = clean_contents(entry)
    return content
