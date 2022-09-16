__all__ = [
    "Page",
    "Resource",
    "Credit",
    "GTIN",
    "Reprint",
    "Arc",
    "Price",
    "Series",
    "Source",
    "MetronInfo",
]

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import xmltodict
from pydantic import BaseModel as PyModel
from pydantic import Extra, Field

from .metadata import Creator, Issue, Metadata, Publisher
from .metadata import Series as MetadataSeries
from .metadata import StoryArc


def to_pascal_case(value: str) -> str:
    return value.replace("_", " ").title().replace(" ", "")


class BaseModel(PyModel):
    class Config:
        alias_generator = to_pascal_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.allow


class Page(BaseModel):
    image: int = Field(alias="@Image")
    type: str = Field(alias="@Type", default="Story")
    double_page: bool = Field(alias="@DoublePage", default=False)
    image_size: int = Field(alias="@ImageSize", default=0)
    key: str = Field(alias="@Key", default="")
    bookmark: str = Field(alias="@Bookmark", default="")
    image_width: int = Field(alias="@ImageWidth", default=-1)
    image_height: int = Field(alias="@ImageHeight", default=-1)


class Resource(BaseModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    value: str = Field(alias="#text")


class Credit(BaseModel):
    creator: Resource
    roles: List[Resource] = Field(default_factory=list)

    def __init__(self, **data):
        if "Roles" in data:
            data["Roles"] = data["Roles"]["Role"]
        super().__init__(**data)


class GTIN(BaseModel):
    isbn: Optional[str] = Field(alias="ISBN", default=None)
    upc: Optional[str] = Field(alias="UPC", default=None)


class Reprint(BaseModel):
    name: Resource


class Arc(BaseModel):
    name: Resource
    number: Optional[int] = Field(default=None, gt=0)


class Price(BaseModel):
    country: str = Field(alias="@country")
    value: float = Field(alias="#text")


class Series(BaseModel):
    lang: str = Field(alias="@lang", default="en")
    name: Resource
    sort_name: Optional[str] = None
    volume: int = 1
    format: Optional[str] = None


class Source(BaseModel):
    source: str = Field(alias="@source")
    value: int = Field(alias="#text", gt=0)


class MetronInfo(BaseModel):
    id: Optional[Source] = Field(alias="ID", default=None)
    publisher: Resource
    series: Series
    collection_title: Optional[str] = None
    number: Optional[str] = None
    stories: List[Resource] = Field(default_factory=list)
    summary: Optional[str] = None
    prices: Optional[Price] = None
    cover_date: date
    store_date: Optional[date] = None
    page_count: Optional[int] = None
    notes: Optional[str] = None
    genres: List[Resource] = Field(default_factory=list)
    tags: List[Resource] = Field(default_factory=list)
    story_arcs: List[Arc] = Field(alias="Arcs", default_factory=list)
    characters: List[Resource] = Field(default_factory=list)
    teams: List[Resource] = Field(default_factory=list)
    locations: List[Resource] = Field(default_factory=list)
    reprints: List[Reprint] = Field(default_factory=list)
    gtin: Optional[GTIN] = Field(alias="GTIN", default=None)
    black_and_white: Optional[bool] = False
    age_rating: Optional[str] = "Unknown"
    url: Optional[str] = Field(alias="URL", default=None)
    credits: List[Credit] = Field(default_factory=list)
    pages: List[Page] = Field(default_factory=list)

    def __init__(self, **data):
        mappings = {
            "Stories": "Story",
            "Genres": "Genre",
            "Tags": "Tag",
            "Arcs": "Arc",
            "Characters": "Character",
            "Teams": "Team",
            "Locations": "Location",
            "Reprints": "Reprint",
            "Credits": "Credit",
            "Pages": "Page",
        }
        for key, value in mappings.items():
            if key in data:
                data[key] = data[key][value]
        super().__init__(**data)

    def to_metadata(self) -> Metadata:
        return Metadata(
            publisher=Publisher(
                # Imprint
                sources={self.id.source: self.publisher.id} if self.id else {},
                title=self.publisher.value,
            ),
            series=MetadataSeries(
                sources={self.id.source: self.series.name.id} if self.id else {},
                # Start Year
                title=self.series.name.value,
                volume=self.series.volume,
            ),
            issue=Issue(
                characters=sorted(x.value for x in self.characters),
                cover_date=self.cover_date,
                creators=sorted(
                    Creator(name=x.creator.value, roles=sorted(r.value for r in x.roles))
                    for x in self.credits
                ),
                format=self.series.format,
                genres=sorted(x.value for x in self.genres),
                language=self.series.lang,
                locations=sorted(x.value for x in self.locations),
                number=self.number,
                page_count=self.page_count,
                sources={self.id.source: self.id.value} if self.id else {},
                store_date=self.store_date,
                story_arcs=sorted(
                    StoryArc(title=x.name.value, number=x.number) for x in self.story_arcs
                ),
                summary=self.summary,
                teams=sorted(x.value for x in self.teams),
                title=self.collection_title,
            ),
            notes=self.notes,
        )

    @staticmethod
    def from_file(info_file: Path) -> "MetronInfo":
        with info_file.open("rb") as stream:
            content = xmltodict.parse(
                stream,
                force_list=[
                    "Story",
                    "Genre",
                    "Tag",
                    "Arc",
                    "Character",
                    "Team",
                    "Location",
                    "Reprint",
                    "Credit",
                    "Role",
                    "Page",
                ],
            )["MetronInfo"]
            for key in content.copy().keys():
                if key.startswith("@xmlns"):
                    del content[key]
            return MetronInfo(**content)

    def to_file(self, info_file: Path):
        if self.black_and_white is False:
            self.black_and_white = None
        if self.age_rating == "Unknown":
            self.age_rating = None
        with info_file.open("w", encoding="UTF-8") as stream:
            content = self.dict(by_alias=True, exclude_none=True)
            content["@xmlns:xsd"] = "https://www.w3.org/2001/XMLSchema"
            content["@xmlns:xsi"] = "https://www.w3.org/2001/XMLSchema-instance"

            mappings = {
                "Stories": "Story",
                "Genres": "Genre",
                "Tags": "Tag",
                "Arcs": "Arc",
                "Characters": "Character",
                "Teams": "Team",
                "Locations": "Location",
                "Reprints": "Reprint",
                "Credits": "Credit",
                "Pages": "Page",
            }
            for key, value in mappings.items():
                if key in content and content[key]:
                    content[key] = {value: content[key]}
                else:
                    del content[key]
            if "Credits" in content:
                for credit in content["Credits"]["Credit"]:
                    if "Roles" in credit and credit["Roles"]:
                        credit["Roles"] = {"Role": credit["Roles"]}
                    else:
                        del credit["Roles"]

            content = int_to_str(content)

            xmltodict.unparse(
                {"MetronInfo": {k: content[k] for k in sorted(content)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
                indent=" " * 2,
            )


def int_to_str(content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in content.items():
        if isinstance(value, dict):
            content[key] = int_to_str(content[key])
        elif isinstance(value, list):
            for index, entry in enumerate(content[key]):
                if isinstance(entry, dict):
                    content[key][index] = int_to_str(content[key][index])
                elif isinstance(entry, int):
                    content[key][index] = str(content[key][index])
        elif isinstance(value, int):
            content[key] = str(content[key])
    return content
