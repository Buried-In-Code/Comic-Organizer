__all__ = [
    "Publisher",
    "Series",
    "Creator",
    "StoryArc",
    "Issue",
    "Metadata",
    "SourceResource",
    "Page",
]

import re
from datetime import date
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

import xmltodict
from natsort import humansorted as sorted
from natsort import ns
from pydantic import Field, validator

from dex_starr import __version__
from dex_starr.models import CamelModel, clean_contents, from_xml_list, to_xml_list
from dex_starr.models.metadata.enums import ComicPageType, Format, Genre, Role, Source


def sanitize(dirty: str) -> str:
    dirty = re.sub(r"[^0-9a-zA-Z& ]+", "", dirty.replace("-", " "))
    dirty = " ".join(dirty.split())
    return dirty.replace(" ", "-")


class SourceResource(CamelModel):
    source: Source = Field(alias="@location")
    value: int = Field(alias="#text")

    def __lt__(self, other):
        if not isinstance(other, SourceResource):
            raise NotImplementedError()
        return self.source < other.source

    def __eq__(self, other):
        if not isinstance(other, SourceResource):
            raise NotImplementedError()
        return self.source == other.source

    def __hash__(self):
        return hash((type(self), self.source))


class Publisher(CamelModel):
    imprint: Optional[str] = None
    sources: List[SourceResource] = Field(default_factory=list)
    title: str

    listable_fields: ClassVar[Dict[str, str]] = {"sources": "source"}

    def __init__(self, **data):
        from_xml_list(mappings=Publisher.listable_fields, content=data)
        super().__init__(**data)

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
    sources: List[SourceResource] = Field(default_factory=list)
    start_year: Optional[int] = Field(default=None, gt=1900)
    title: str
    volume: int = Field(default=1, gt=0)

    listable_fields: ClassVar[Dict[str, str]] = {"sources": "source"}

    def __init__(self, **data):
        from_xml_list(mappings=Series.listable_fields, content=data)
        super().__init__(**data)

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

    listable_fields: ClassVar[Dict[str, str]] = {"roles": "role"}

    def __init__(self, **data):
        from_xml_list(mappings=Creator.listable_fields, content=data)
        super().__init__(**data)

    @validator("roles", pre=True, each_item=True)
    def role_to_enum(cls, v) -> Role:
        if isinstance(v, str):
            return Role.load(v)
        return v

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
    title: str = Field(alias="#text")
    number: Optional[int] = Field(alias="@number", default=None)

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
    language: str = Field(alias="@language", default="en")
    locations: List[str] = Field(default_factory=list)
    number: str
    page_count: int = Field(default=0, ge=0)
    sources: List[SourceResource] = Field(default_factory=list)
    store_date: Optional[date] = None
    story_arcs: List[StoryArc] = Field(default_factory=list)
    summary: Optional[str] = None
    teams: List[str] = Field(default_factory=list)
    title: Optional[str] = None

    listable_fields: ClassVar[Dict[str, str]] = {
        **Creator.listable_fields,
        "characters": "character",
        "creators": "creator",
        "genres": "genre",
        "locations": "location",
        "sources": "source",
        "storyArcs": "storyArc",
        "teams": "team",
    }

    def __init__(self, **data):
        from_xml_list(mappings=Issue.listable_fields, content=data)
        text_fields = ["storyArcs"]
        for text_field in text_fields:
            if text_field in data:
                if isinstance(data[text_field], str):
                    data[text_field] = {"#text": data[text_field]}
                elif isinstance(data[text_field], list):
                    for index, entry in enumerate(data[text_field]):
                        if isinstance(entry, str):
                            data[text_field][index] = {"#text": entry}
        super().__init__(**data)

    @validator("format", pre=True)
    def format_to_enum(cls, v) -> Format:
        if isinstance(v, str):
            return Format.load(v)
        return v

    @validator("genres", pre=True, each_item=True)
    def genre_to_enum(cls, v) -> Genre:
        if isinstance(v, str):
            return Genre.load(v)
        return v

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
    image: int = Field(alias="@image")
    page_type: ComicPageType = Field(alias="@type", default=ComicPageType.STORY)
    double_page: bool = Field(alias="@doublePage", default=False)
    image_size: int = Field(alias="@imageSize", default=0)
    key: Optional[str] = Field(alias="@key", default=None)
    bookmark: Optional[str] = Field(alias="@bookmark", default=None)
    image_width: Optional[int] = Field(alias="@imageWidth", default=None)
    image_height: Optional[int] = Field(alias="@imageHeight", default=None)

    @validator("page_type", pre=True)
    def page_type_to_enum(cls, v) -> ComicPageType:
        if isinstance(v, str):
            return ComicPageType.load(v)
        return v

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

    listable_fields: ClassVar[Dict[str, str]] = {
        **Publisher.listable_fields,
        **Series.listable_fields,
        **Issue.listable_fields,
        "pages": "page",
    }

    def __init__(self, **data):
        from_xml_list(mappings=Metadata.listable_fields, content=data)
        super().__init__(**data)

    @staticmethod
    def from_file(metadata_file: Path) -> "Metadata":
        with metadata_file.open("rb") as stream:
            content = xmltodict.parse(stream, force_list=list(Metadata.listable_fields.values()))[
                "metadata"
            ]
            return Metadata(**content["content"])

    def to_file(self, metadata_file: Path):
        content = self.dict(by_alias=True, exclude_none=True)
        to_xml_list(mappings=Metadata.listable_fields, content=content)
        content = clean_contents(content)

        with metadata_file.open("w", encoding="UTF-8") as stream:
            xmltodict.unparse(
                {
                    "metadata": {
                        "content": {k: content[k] for k in sorted(content, alg=ns.NA | ns.G)},
                        "meta": generate_meta(),
                    }
                },
                output=stream,
                short_empty_elements=True,
                pretty=True,
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
    return {
        "date": date.today().isoformat(),
        "tool": {"#text": "Dex-Starr", "@version": __version__},
    }
