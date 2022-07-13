from datetime import date
from pathlib import Path
from typing import List, Optional

import xmltodict
from pydantic import BaseModel, Extra, Field

from dex_starr.metadata.metadata import Issue, Metadata, Publisher
from dex_starr.metadata.metadata import Series as MetadataSeries


def to_pascal_case(value: str) -> str:
    return value.replace("_", " ").title().replace(" ", "")


class MetronModel(BaseModel):
    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Page(MetronModel):
    image: int = Field(alias="@Image")
    type: str = Field(alias="@Type", default="Story")
    double_page: bool = Field(alias="@DoublePage", default=False)
    image_size: int = Field(alias="@ImageSize", default=0)
    key: str = Field(alias="@Key", default="")
    bookmark: str = Field(alias="@Bookmark", default="")
    image_width: int = Field(alias="@ImageWidth", default=-1)
    image_height: int = Field(alias="@ImageHeight", default=-1)


class Resource(MetronModel):
    id: Optional[str] = Field(alias="@id", default=None)
    value: str = Field(alias="#text")


class Credit(MetronModel):
    creator: Resource
    roles: List[Resource] = Field(default_factory=list)

    def __init__(self, **data):
        if "Roles" in data:
            data["Roles"] = data["Roles"]["Role"]
        super().__init__(**data)


class GTIN(MetronModel):
    isbn: Optional[str] = Field(alias="ISBN", default=None)
    upc: Optional[str] = Field(alias="UPC", default=None)


class Reprint(MetronModel):
    name: Resource


class Arc(MetronModel):
    name: Resource
    number: Optional[int] = Field(default=None, gt=0)


class Price(MetronModel):
    currency: str = Field(alias="@currency")
    value: float = Field(alias="#text")


class Series(MetronModel):
    lang: str = Field(alias="@lang", default="EN")
    name: Resource
    sort_name: Optional[str] = None
    format: Optional[str] = None
    volume: Optional[int] = None


class Source(MetronModel):
    source: str = Field(alias="@source")
    value: str = Field(alias="#text")


class MetronInfo(MetronModel):
    id: Optional[Source] = Field(alias="ID", default=None)
    publisher: str
    series: Series
    collection_title: Optional[str] = None
    number: Optional[str] = None
    stories: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    price: Optional[Price] = None
    cover_date: Optional[date] = None
    store_date: Optional[date] = None
    page_count: Optional[int] = None
    genres: List[Resource] = Field(default_factory=list)
    tags: List[Resource] = Field(default_factory=list)
    arcs: List[Arc] = Field(default_factory=list)
    characters: List[Resource] = Field(default_factory=list)
    teams: List[Resource] = Field(default_factory=list)
    locations: List[Resource] = Field(default_factory=list)
    reprints: List[Reprint] = Field(default_factory=list)
    gtin: Optional[GTIN] = Field(alias="GTIN", default=None)
    black_and_white: bool = False
    age_rating: str = "Unknown"
    url: Optional[str] = Field(alias="URL", default=None)
    credits: List[Credit] = Field(default_factory=list)
    pages: List[Page] = Field(default_factory=list)

    def __init__(self, **data):
        if "Stories" in data:
            data["Stories"] = data["Stories"]["Story"]
        if "Genres" in data:
            data["Genres"] = data["Genres"]["Genre"]
        if "Tags" in data:
            data["Tags"] = data["Tags"]["Tag"]
        if "Arcs" in data:
            data["Arcs"] = data["Arcs"]["Arc"]
        if "Characters" in data:
            data["Characters"] = data["Characters"]["Character"]
        if "Teams" in data:
            data["Teams"] = data["Teams"]["Team"]
        if "Locations" in data:
            data["Locations"] = data["Locations"]["Location"]
        if "Reprints" in data:
            data["Reprints"] = data["Reprints"]["Reprint"]
        if "Credits" in data:
            data["Credits"] = data["Credits"]["Credit"]
        if "Pages" in data:
            data["Pages"] = data["Pages"]["Page"]
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
            if "Roles" in content["Credits"]["Credit"] and content["Credits"]["Credit"]["Roles"]:
                content["Credits"]["Credit"]["Roles"] = {
                    "Role": content["Credits"]["Credit"]["Roles"]
                }
            else:
                del content["Credits"]["Credit"]["Roles"]

            xmltodict.unparse(
                {"MetronInfo": {k: content[k] for k in sorted(content)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
                indent=" " * 2,
            )
