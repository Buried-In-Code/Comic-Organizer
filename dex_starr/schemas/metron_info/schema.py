__all__ = [
    "Resource",
    "RoleResource",
    "Credit",
    "GTIN",
    "Arc",
    "GenreResource",
    "Price",
    "Series",
    "Source",
    "MetronInfo",
]

from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import xmltodict
from pydantic import Field, validator
from rich import print

from dex_starr.schemas import XmlModel
from dex_starr.schemas.comic_info.schema import Page
from dex_starr.schemas.metadata.enums import FormatType as MetadataFormat
from dex_starr.schemas.metadata.enums import Role as MetadataRole
from dex_starr.schemas.metadata.enums import Source as MetadataSource
from dex_starr.schemas.metadata.schema import Creator, Issue, Metadata, Publisher
from dex_starr.schemas.metadata.schema import Series as MetadataSeries
from dex_starr.schemas.metadata.schema import StoryArc
from dex_starr.schemas.metron_info.enums import (
    AgeRating,
    FormatType,
    Genre,
    InformationSource,
    Role,
)


class Resource(XmlModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    value: str = Field(alias="#text")


class RoleResource(XmlModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    value: Role = Field(alias="#text")

    @validator("value", pre=True)
    def value_to_enum(cls, v) -> Role:
        if isinstance(v, str):
            return Role.load(v)
        return v

    def __lt__(self, other):
        if not isinstance(other, RoleResource):
            raise NotImplementedError()
        return self.value < other.value

    def __hash__(self):
        return hash((type(self),) + (self.value,))


class Credit(XmlModel):
    creator: Resource
    roles: List[RoleResource] = Field(default_factory=list)

    def __init__(self, **data):
        if "Roles" in data:
            data["Roles"] = data["Roles"]["Role"]
        super().__init__(**data)


class GTIN(XmlModel):
    isbn: Optional[str] = Field(alias="ISBN", default=None)
    upc: Optional[str] = Field(alias="UPC", default=None)


class Arc(XmlModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    name: str
    number: Optional[int] = Field(default=None, gt=0)


class GenreResource(XmlModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    value: Genre = Field(alias="#text")

    @validator("value", pre=True)
    def value_to_enum(cls, v) -> Genre:
        if isinstance(v, str):
            return Genre.load(v)
        return v


class Price(XmlModel):
    country: str = Field(alias="@country")
    value: float = Field(alias="#text")


class Series(XmlModel):
    lang: str = Field(alias="@lang", default="en")
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    name: str
    sort_name: Optional[str] = None
    volume: int = 1
    format: Optional[FormatType] = None

    @validator("format", pre=True)
    def format_to_enum(cls, v) -> FormatType:
        if isinstance(v, str):
            return FormatType.load(v)
        return v


class Source(XmlModel):
    source: InformationSource = Field(alias="@source")
    value: int = Field(alias="#text", gt=0)

    @validator("source", pre=True)
    def source_to_enum(cls, v) -> InformationSource:
        if isinstance(v, str):
            return InformationSource.load(v)
        return v


class MetronInfo(XmlModel):
    id: Optional[Source] = Field(alias="ID", default=None)
    publisher: Resource
    series: Series
    collection_title: Optional[str] = None
    number: Optional[str] = None
    stories: List[Resource] = Field(default_factory=list)
    summary: Optional[str] = None
    prices: List[Price] = Field(default_factory=list)
    cover_date: date
    store_date: Optional[date] = None
    page_count: int = 0
    notes: Optional[str] = None
    genres: List[GenreResource] = Field(default_factory=list)
    tags: List[Resource] = Field(default_factory=list)
    story_arcs: List[Arc] = Field(alias="Arcs", default_factory=list)
    characters: List[Resource] = Field(default_factory=list)
    teams: List[Resource] = Field(default_factory=list)
    locations: List[Resource] = Field(default_factory=list)
    reprints: List[Resource] = Field(default_factory=list)
    gtin: Optional[GTIN] = Field(alias="GTIN", default=None)
    black_and_white: bool = False
    age_rating: AgeRating = AgeRating.UNKNOWN
    url: Optional[str] = Field(alias="URL", default=None)
    credits: List[Credit] = Field(default_factory=list)
    pages: List[Page] = Field(default_factory=list)

    def __init__(self, **data):
        if "Stories" in data:
            data["Stories"] = data["Stories"]["Story"]
        if "Prices" in data:
            data["Prices"] = data["Prices"]["Price"]
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

    @validator("age_rating", pre=True)
    def age_rating_to_enum(cls, v) -> AgeRating:
        if isinstance(v, str):
            return AgeRating.load(v)
        return v

    def to_metadata(self) -> Metadata:
        creators = []
        for credit in self.credits:
            roles = set()
            for role in credit.roles:
                try:
                    roles.add(MetadataRole.load(role.value.value))
                except ValueError as err:
                    print(err)
                    roles.add(MetadataRole.OTHER)
            creators.append(Creator(name=credit.creator.value, roles=sorted(roles)))
        try:
            format = MetadataFormat.load(self.series.format.value)
        except ValueError as err:
            print(err)
            format = MetadataFormat.COMIC
        return Metadata(
            publisher=Publisher(
                # Imprint
                sources={MetadataSource.load(self.id.source.value): self.publisher.id}
                if self.id
                else {},
                title=self.publisher.value,
            ),
            series=MetadataSeries(
                sources={MetadataSource.load(self.id.source.value): self.series.id}
                if self.id
                else {},
                # Start Year
                title=self.series.name,
                volume=self.series.volume,
            ),
            issue=Issue(
                characters=sorted(x.value for x in self.characters),
                cover_date=self.cover_date,
                creators=sorted(creators),
                format=format,
                genres=sorted(x.value for x in self.genres),
                language=self.series.lang,
                locations=sorted(x.value for x in self.locations),
                number=self.number,
                page_count=self.page_count,
                sources={MetadataSource.load(self.id.source.value): self.id.value}
                if self.id
                else {},
                store_date=self.store_date,
                story_arcs=sorted(StoryArc(title=x.name, number=x.number) for x in self.story_arcs),
                summary=self.summary,
                teams=sorted(x.value for x in self.teams),
                title=self.collection_title,
            ),
            pages=sorted(
                Page(
                    image=x.image,
                    page_type=x.page_type,
                    double_page=x.double_page,
                    image_size=x.image_size,
                    key=x.key,
                    bookmark=x.bookmark,
                    image_width=x.image_width,
                    image_height=x.image_height,
                )
                for x in self.pages
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
                    "Price",
                ],
            )["MetronInfo"]
            mappings = {
                "Stories": "Story",
                "Genres": "Genre",
                "Tags": "Tag",
                "Characters": "Character",
                "Teams": "Team",
                "Locations": "Location",
                "Reprints": "Reprint",
            }
            for key, value in mappings.items():
                if key in content and value in content[key]:
                    for index, entry in enumerate(content[key][value].copy()):
                        if isinstance(entry, str):
                            content[key][value][index] = {"#text": entry}
            if "Credits" in content and "Credit" in content["Credits"]:
                for index, entry in enumerate(content["Credits"]["Credit"].copy()):
                    if isinstance(entry["Creator"], str):
                        content["Credits"]["Credit"][index]["Creator"] = {"#text": entry["Creator"]}
                    if "Roles" in entry and "Role" in entry["Roles"]:
                        for role_index, role in enumerate(entry["Roles"]["Role"]):
                            if isinstance(role, str):
                                content["Credits"]["Credit"][index]["Roles"]["Role"][role_index] = {
                                    "#text": role
                                }
            return MetronInfo(**content)

    def to_file(self, info_file: Path):
        with info_file.open("w", encoding="UTF-8") as stream:
            content = self.dict(by_alias=True, exclude_none=True)
            content["@xmlns:noNamespaceSchemaLocation"] = "MetronInfo.xsd"
            content["@xmlns:xsi"] = "https://www.w3.org/2001/XMLSchema-instance"

            for index, page in enumerate(content["Pages"].copy()):
                if not page["@DoublePage"]:
                    del content["Pages"][index]["@DoublePage"]
            if not content["BlackAndWhite"]:
                del content["BlackAndWhite"]

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
                "Prices": "Price",
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

            content = to_str(content)

            xmltodict.unparse(
                {"MetronInfo": {k: content[k] for k in sorted(content)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
            )


def to_str(content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in content.items():
        if isinstance(value, dict):
            content[key] = to_str(content[key])
        elif isinstance(value, list):
            for index, entry in enumerate(content[key]):
                if isinstance(entry, dict):
                    content[key][index] = to_str(content[key][index])
                elif isinstance(entry, int):
                    content[key][index] = str(content[key][index])
                elif isinstance(entry, Enum):
                    content[key][index] = str(content[key][index])
        elif isinstance(value, int):
            content[key] = str(content[key])
        elif isinstance(value, Enum):
            content[key] = str(content[key])
    return content
