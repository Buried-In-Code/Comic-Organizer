from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import xmltodict
from pydantic import BaseModel as PyModel
from pydantic import Extra, Field

from dex_starr.console import CONSOLE
from dex_starr.metadata.metadata import Issue, Metadata, Publisher
from dex_starr.metadata.metadata import Series as MetadataSeries


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
    id: int = Field(alias="@id", gt=0, default=1)
    value: str = Field(alias="#text")


class Credit(BaseModel):
    creator: Resource
    roles: list[Resource] = Field(default_factory=list)

    def __init__(self, **data):
        if "Roles" in data:
            data["Roles"] = data["Roles"]["Role"]
        super().__init__(**data)


class GTIN(BaseModel):
    isbn: str | None = Field(alias="ISBN", default=None)
    upc: str | None = Field(alias="UPC", default=None)


class Reprint(BaseModel):
    name: Resource


class Arc(BaseModel):
    name: Resource
    number: int | None = Field(default=None, gt=0)


class Price(BaseModel):
    currency: str = Field(alias="@currency")
    value: float = Field(alias="#text")


class Series(BaseModel):
    lang: str = Field(alias="@lang", default="en")
    name: Resource
    sort_name: str | None = None
    volume: int | None = None
    format: str | None = None


class Source(BaseModel):
    source: str = Field(alias="@source")
    value: int = Field(alias="#text", gt=0)


class MetronInfo(BaseModel):
    id: Source | None = Field(alias="ID", default=None)
    publisher: str
    series: Series
    collection_title: str | None = None
    number: str | None = None
    stories: list[str] = Field(default_factory=list)
    summary: str | None = None
    price: Price | None = None
    cover_date: date
    store_date: date | None = None
    page_count: int | None = None
    notes: str | None = None
    genres: list[Resource] = Field(default_factory=list)
    tags: list[Resource] = Field(default_factory=list)
    arcs: list[Arc] = Field(default_factory=list)
    characters: list[Resource] = Field(default_factory=list)
    teams: list[Resource] = Field(default_factory=list)
    locations: list[Resource] = Field(default_factory=list)
    reprints: list[Reprint] = Field(default_factory=list)
    gtin: GTIN | None = Field(alias="GTIN", default=None)
    black_and_white: bool | None = False
    age_rating: str | None = "Unknown"
    url: str | None = Field(alias="URL", default=None)
    credits: list[Credit] = Field(default_factory=list)
    pages: list[Page] = Field(default_factory=list)

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
            publisher=Publisher(title=self.publisher),
            series=MetadataSeries(
                title=self.series.name.value,
                volume=self.series.volume,
            ),
            issue=Issue(
                characters=[c.value for c in self.characters],
                cover_date=self.cover_date,
                creators={c.creator.value: sorted(r.value for r in c.roles) for c in self.credits},
                format=self.series.format,
                genres=sorted({g.value for g in self.genres}),
                language_iso=self.series.lang,
                locations=[x.value for x in self.locations],
                number=self.number,
                page_count=self.page_count,
                sources={self.id.source: self.id.value} if self.id else {},
                store_date=self.store_date,
                story_arcs=self.stories,
                summary=self.summary,
                teams=[t.value for t in self.teams],
                title=self.collection_title,
            ),
        )

    @staticmethod
    def from_file(info_file: Path) -> MetronInfo:
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
            CONSOLE.print({k: content[k] for k in sorted(content)})

            xmltodict.unparse(
                {"MetronInfo": {k: content[k] for k in sorted(content)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
                indent=" " * 2,
            )


def int_to_str(content: dict[str, Any]) -> dict[str, Any]:
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
