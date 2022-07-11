from datetime import date
from pathlib import Path
from typing import List, Optional

import xmltodict
from pydantic import BaseModel, Extra, Field

from dex_starr.metadata.metadata import Issue, Metadata, Publisher
from dex_starr.metadata.metadata import Series as MetadataSeries


def to_pascal_case(value: str) -> str:
    return value.replace("_", " ").title().replace(" ", "")


class Page(BaseModel):
    image: int = Field(alias="@Image")
    type: str = Field(alias="@Type", default="Story")
    double_page: bool = Field(alias="@DoublePage", default=False)
    image_size: int = Field(alias="@ImageSize", default=0)
    key: str = Field(alias="@Key", default="")
    bookmark: str = Field(alias="@Bookmark", default="")
    image_width: int = Field(alias="@ImageWidth", default=-1)
    image_height: int = Field(alias="@ImageHeight", default=-1)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Credit(BaseModel):
    creator: str
    roles: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        data["Roles"] = data["Roles"]["Role"]
        super().__init__(**data)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class GTIN(BaseModel):
    isbn: Optional[str] = Field(alias="ISBN", default=None)
    upc: Optional[str] = Field(alias="UPC", default=None)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Source(BaseModel):
    source: str = Field(alias="@source")
    value: int = Field(alias="#text", gt=0)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Reprint(BaseModel):
    id: Optional[Source] = Field(alias="ID", default=None)
    name: str

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Arc(BaseModel):
    name: str
    number: Optional[int] = Field(default=None, gt=0)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Price(BaseModel):
    currency: str = Field(alias="@currency")
    value: float = Field(alias="#text")

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Series(BaseModel):
    lang: str = Field(alias="@lang", default="EN")
    name: str
    sort_name: str
    type: str

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class MetronInfo(BaseModel):
    id: Optional[Source] = Field(alias="ID", default=None)
    publisher: str
    series: Series
    volume: Optional[int] = None
    collection_title: Optional[str] = None
    number: Optional[str] = None
    stories: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    price: Optional[Price] = None
    cover_date: Optional[date] = None
    store_date: Optional[date] = None
    page_count: Optional[int] = None
    genres: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    arcs: List[Arc] = Field(default_factory=list)
    characters: List[str] = Field(default_factory=list)
    teams: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    reprints: List[Reprint] = Field(default_factory=list)
    gtin: Optional[GTIN] = Field(alias="GTIN", default=None)
    black_and_white: bool = False
    age_rating: str = "Unknown"
    url: Optional[str] = Field(alias="URL", default=None)
    credits: List[Credit] = Field(default_factory=list)
    pages: List[Page] = Field(default_factory=list)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    def __init__(self, **data):
        if "Stories" in data:
            data["Stories"] = data["Stories"]["Story"]
        if "Generes" in data:
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
            series=MetadataSeries(title=self.series.name, volume=self.volume),
            issue=Issue(
                characters=self.characters,
                cover_date=self.cover_date,
                creators={c.creator: sorted(r.value for r in c.roles) for c in self.credits},
                format=self.series.type,
                genres=sorted({g.value for g in self.genres}),
                language_iso=self.series.lang,
                locations=self.locations,
                number=self.number,
                page_count=self.page_count,
                # TODO: Sources
                store_date=self.store_date,
                story_arcs=self.stories,
                summary=self.summary,
                teams=self.teams,
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

            if "Stories" in content and content["Stories"]:
                content["Stories"] = {"Story": content["Stories"]}
            else:
                del content["Stories"]
            if "Genres" in content and content["Genres"]:
                content["Genres"] = {"Genre": content["Genres"]}
            else:
                del content["Genres"]
            if "Tags" in content and content["Tags"]:
                content["Tags"] = {"Tag": content["Tags"]}
            else:
                del content["Tags"]
            if "Arcs" in content and content["Arcs"]:
                content["Arcs"] = {"Arc": content["Arcs"]}
            else:
                del content["Arcs"]
            if "Characters" in content and content["Characters"]:
                content["Characters"] = {"Character": content["Characters"]}
            else:
                del content["Characters"]
            if "Teams" in content and content["Teams"]:
                content["Teams"] = {"Team": content["Teams"]}
            else:
                del content["Teams"]
            if "Locations" in content and content["Locations"]:
                content["Locations"] = {"Location": content["Locations"]}
            else:
                del content["Locations"]
            if "Reprints" in content and content["Reprints"]:
                content["Reprints"] = {"Reprint": content["Reprints"]}
            else:
                del content["Reprints"]
            if "Credits" in content and content["Credits"]:
                content["Credits"] = {"Credit": content["Credits"]}
            else:
                del content["Credits"]
            if "Pages" in content and content["Pages"]:
                content["Pages"] = {"Page": content["Pages"]}
            else:
                del content["Pages"]

            xmltodict.unparse(
                {"MetronInfo": {k: content[k] for k in sorted(content)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
                indent=" " * 2,
            )
