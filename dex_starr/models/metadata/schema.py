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

import re
from datetime import date
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

import xmltodict
from natsort import humansorted as sorted
from natsort import ns
from pydantic import Field, validator

from dex_starr import __version__
from dex_starr.models import CamelModel, clean_contents, from_xml_list, to_xml_list, to_xml_text
from dex_starr.models.metadata.enums import Format, Genre, PageType, Role, Source


def sanitize(dirty: str) -> str:
    dirty = re.sub(r"[^0-9a-zA-Z& ]+", "", dirty.replace("-", " "))
    dirty = " ".join(dirty.split())
    return dirty.replace(" ", "-")


class Resource(CamelModel):
    source: Source = Field(alias="@source")
    value: int = Field(alias="#text")

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

    list_fields: ClassVar[Dict[str, str]] = {"resources": "resource"}

    def __init__(self, **data):
        from_xml_list(mappings=Publisher.list_fields, content=data)
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
    resources: List[Resource] = Field(default_factory=list)
    start_year: Optional[int] = Field(default=None, gt=1900)
    title: str
    volume: int = Field(default=1, gt=0)

    list_fields: ClassVar[Dict[str, str]] = {"resources": "resource"}

    def __init__(self, **data):
        from_xml_list(mappings=Series.list_fields, content=data)
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

    list_fields: ClassVar[Dict[str, str]] = {"roles": "role"}

    def __init__(self, **data):
        from_xml_list(mappings=Creator.list_fields, content=data)
        super().__init__(**data)

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

    list_fields: ClassVar[Dict[str, str]] = {
        **Creator.list_fields,
        "characters": "character",
        "creators": "creator",
        "genres": "genre",
        "locations": "location",
        "resources": "resource",
        "storyArcs": "storyArc",
        "teams": "team",
    }
    text_fields: ClassVar[List[str]] = ["storyArcs"]

    def __init__(self, **data):
        from_xml_list(mappings=Issue.list_fields, content=data)
        to_xml_text(mappings=Issue.text_fields, content=data)
        super().__init__(**data)

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
    image: int = Field(alias="@image")
    page_type: PageType = Field(alias="@pageType", default=PageType.STORY)
    double_page: bool = Field(alias="@doublePage", default=False)
    key: Optional[str] = Field(alias="@key", default=None)
    bookmark: Optional[str] = Field(alias="@bookmark", default=None)
    image_size: int = Field(alias="@imageSize", default=0, ge=0)
    image_width: int = Field(alias="@imageWidth", default=0, ge=0)
    image_height: int = Field(alias="@imageHeight", default=0, ge=0)

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

    list_fields: ClassVar[Dict[str, str]] = {
        **Publisher.list_fields,
        **Series.list_fields,
        **Issue.list_fields,
        "pages": "page",
    }

    def __init__(self, **data):
        from_xml_list(mappings=Metadata.list_fields, content=data)
        super().__init__(**data)

    @staticmethod
    def from_file(metadata_file: Path) -> "Metadata":
        with metadata_file.open("rb") as stream:
            content = xmltodict.parse(stream, force_list=list(Metadata.list_fields.values()))
            return Metadata(**content["metadata"]["content"])

    def to_file(self, metadata_file: Path):
        content = self.dict(by_alias=True, exclude_none=True)
        to_xml_list(mappings=Metadata.list_fields, content=content)
        content = clean_contents(content)

        with metadata_file.open("wb") as stream:
            xmltodict.unparse(
                {
                    "metadata": {
                        "content": {k: content[k] for k in sorted(content, alg=ns.NA | ns.G)},
                        "meta": generate_meta(),
                        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                        "@xsi:noNamespaceSchemaLocation": "https://raw.githubusercontent.com/"
                        "Buried-In-Code/Dex-Starr/use-xml/"
                        "schemas/Metadata.xsd",
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
        "@date": date.today().isoformat(),
        "tool": {"#text": "Dex-Starr", "@version": __version__},
    }
