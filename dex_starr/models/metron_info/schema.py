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
    "Page",
]

from datetime import date
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

import xmltodict
from natsort import humansorted as sorted
from natsort import ns
from pydantic import Field, validator

from dex_starr.models import PascalModel, clean_contents, from_xml_list, to_xml_list, to_xml_text
from dex_starr.models.comic_info.schema import Page
from dex_starr.models.metadata.schema import Metadata
from dex_starr.models.metron_info.enums import AgeRating, Format, Genre, InformationSource, Role


class Resource(PascalModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    value: str = Field(alias="#text")

    def __lt__(self, other):
        if not isinstance(other, Resource):
            raise NotImplementedError()
        if (self.id or -1) != (other.id or -1):
            return (self.id or -1) < (other.id or -1)
        return self.value < other.value

    def __eq__(self, other):
        if not isinstance(other, Resource):
            raise NotImplementedError()
        return ((self.id or -1), self.value) == ((other.id or -1), other.value)

    def __hash__(self):
        return hash((type(self), self.id, self.value))


class RoleResource(PascalModel):
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

    def __eq__(self, other):
        if not isinstance(other, RoleResource):
            raise NotImplementedError()
        return self.value == other.value

    def __hash__(self):
        return hash((type(self), self.value))


class Credit(PascalModel):
    creator: Resource
    roles: List[RoleResource] = Field(default_factory=list)

    list_fields: ClassVar[Dict[str, str]] = {"Roles": "Role"}
    text_fields: ClassVar[List[str]] = ["Creator", "Roles"]

    def __init__(self, **data):
        from_xml_list(mappings=Credit.list_fields, content=data)
        to_xml_text(mappings=Credit.text_fields, content=data)
        super().__init__(**data)

    def __lt__(self, other):
        if not isinstance(other, Credit):
            raise NotImplementedError()
        return self.creator < other.creator

    def __eq__(self, other):
        if not isinstance(other, Credit):
            raise NotImplementedError()
        return self.creator == other.creator

    def __hash__(self):
        return hash((type(self), self.creator))


class GTIN(PascalModel):
    isbn: Optional[str] = Field(alias="ISBN", default=None)
    upc: Optional[str] = Field(alias="UPC", default=None)

    def __lt__(self, other):
        if not isinstance(other, GTIN):
            raise NotImplementedError()
        if (self.isbn or "") != (other.isbn or ""):
            return (self.isbn or "") < (other.isbn or "")
        return (self.upc or "") < (other.upc or "")

    def __eq__(self, other):
        if not isinstance(other, GTIN):
            raise NotImplementedError()
        return ((self.isbn or ""), (self.upc or "")) == ((other.isbn or ""), (other.upc or ""))

    def __hash__(self):
        return hash((type(self), self.isbn, self.upc))


class Arc(PascalModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    name: str
    number: Optional[int] = Field(default=None, gt=0)

    def __lt__(self, other):
        if not isinstance(other, Arc):
            raise NotImplementedError()
        if (self.id or -1) != (other.id or -1):
            return (self.id or -1) < (other.id or -1)
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, Arc):
            raise NotImplementedError()
        return ((self.id or -1), self.name) == ((other.id or -1), other.name)

    def __hash__(self):
        return hash((type(self), self.id, self.name))


class GenreResource(PascalModel):
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    value: Genre = Field(alias="#text")

    @validator("value", pre=True)
    def value_to_enum(cls, v) -> Genre:
        if isinstance(v, str):
            return Genre.load(v)
        return v

    def __lt__(self, other):
        if not isinstance(other, GenreResource):
            raise NotImplementedError()
        return self.value < other.value

    def __eq__(self, other):
        if not isinstance(other, GenreResource):
            raise NotImplementedError()
        return self.value == other.value

    def __hash__(self):
        return hash((type(self), self.value))


class Price(PascalModel):
    country: str = Field(alias="@country")
    value: float = Field(alias="#text")

    def __lt__(self, other):
        if not isinstance(other, Price):
            raise NotImplementedError()
        return self.country < other.country

    def __eq__(self, other):
        if not isinstance(other, Price):
            raise NotImplementedError()
        return self.country == other.country

    def __hash__(self):
        return hash((type(self), self.country))


class Series(PascalModel):
    lang: str = Field(alias="@lang", default="en")
    id: Optional[int] = Field(alias="@id", gt=0, default=None)
    name: str
    sort_name: Optional[str] = None
    volume: int = 1
    format: Format = Format.SERIES

    @validator("format", pre=True)
    def format_to_enum(cls, v) -> Format:
        if isinstance(v, str):
            return Format.load(v)
        return v

    def __lt__(self, other):
        if not isinstance(other, Resource):
            raise NotImplementedError()
        if (self.id or -1) != (other.id or -1):
            return (self.id or -1) < (other.id or -1)
        if self.name != other.name:
            return self.name < other.name
        if self.volume != other.volume:
            return self.volume < other.volume
        return self.format < other.format

    def __eq__(self, other):
        if not isinstance(other, Series):
            raise NotImplementedError()
        return ((self.id or -1), self.name, self.volume, self.format) == (
            (other.id or -1),
            other.name,
            other.volume,
            other.format,
        )

    def __hash__(self):
        return hash((type(self), self.id, self.name, self.volume, self.format))


class Source(PascalModel):
    source: InformationSource = Field(alias="@source")
    value: int = Field(alias="#text", gt=0)

    @validator("source", pre=True)
    def source_to_enum(cls, v) -> InformationSource:
        if isinstance(v, str):
            return InformationSource.load(v)
        return v

    def __lt__(self, other):
        if not isinstance(other, Source):
            raise NotImplementedError()
        if self.source != other.source:
            return self.source < other.source
        return self.value < other.value

    def __eq__(self, other):
        if not isinstance(other, Source):
            raise NotImplementedError()
        return (self.source, self.value) == (other.source, other.value)

    def __hash__(self):
        return hash((type(self), self.source, self.value))


class MetronInfo(PascalModel):
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

    list_fields: ClassVar[Dict[str, str]] = {
        **Credit.list_fields,
        "Stories": "Story",
        "Prices": "Price",
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
    text_fields: ClassVar[List[str]] = [
        *Credit.text_fields,
        "Stories",
        "Genres",
        "Tags",
        "Characters",
        "Teams",
        "Locations",
        "Reprints",
    ]

    def __init__(self, **data):
        from_xml_list(mappings=MetronInfo.list_fields, content=data)
        to_xml_text(mappings=MetronInfo.text_fields, content=data)
        super().__init__(**data)

    @validator("age_rating", pre=True)
    def age_rating_to_enum(cls, v) -> AgeRating:
        if isinstance(v, str):
            return AgeRating.load(v)
        return v

    def to_metadata(self) -> Metadata:
        from dex_starr.models.metadata.enums import Format as MetadataFormat
        from dex_starr.models.metadata.enums import PageType as MetadataPageType
        from dex_starr.models.metadata.enums import Role as MetadataRole
        from dex_starr.models.metadata.schema import Creator, Issue
        from dex_starr.models.metadata.schema import Page as MetadataPage
        from dex_starr.models.metadata.schema import Publisher
        from dex_starr.models.metadata.schema import Series as MetadataSeries
        from dex_starr.models.metadata.schema import StoryArc

        return Metadata(
            publisher=Publisher(
                # TODO: Imprint
                sources=[],  # TODO: Convert Sources
                title=self.publisher.value,
            ),
            series=MetadataSeries(
                sources=[],  # TODO: Convert Sources
                # TODO: Start Year
                title=self.series.name,
                volume=self.series.volume,
            ),
            issue=Issue(
                characters=sorted({x.value for x in self.characters}, alg=ns.NA | ns.G),
                cover_date=self.cover_date,
                creators=sorted(
                    {
                        Creator(
                            name=x.creator.value,
                            roles=sorted(
                                {Role.load(str(r.value)) for r in x.roles}, alg=ns.NA | ns.G
                            ),
                        )
                        for x in self.credits
                    },
                    alg=ns.NA | ns.G,
                ),
                format=Format.load(str(self.series.format)),
                genres=sorted({Genre.load(str(x.value)) for x in self.genres}, alg=ns.NA | ns.G),
                language=self.series.lang,
                locations=sorted({x.value for x in self.locations}, alg=ns.NA | ns.G),
                number=self.number,
                page_count=self.page_count,
                sources=[],  # TODO: Convert Sources
                store_date=self.store_date,
                story_arcs=sorted(
                    {StoryArc(title=x.name, number=x.number) for x in self.story_arcs},
                    alg=ns.NA | ns.G,
                ),
                summary=self.summary,
                teams=sorted({x.value for x in self.teams}, alg=ns.NA | ns.G),
                title=self.collection_title,
            ),
            pages=sorted(
                {
                    MetadataPage(
                        image=x.image,
                        page_type=MetadataPageType.load(str(x.page_type)),
                        double_page=x.double_page,
                        image_size=x.image_size,
                        key=x.key,
                        bookmark=x.bookmark,
                        image_width=x.image_width,
                        image_height=x.image_height,
                    )
                    for x in self.pages
                },
                alg=ns.NA | ns.G,
            ),
            notes=self.notes,
        )

    @staticmethod
    def from_file(info_file: Path) -> "MetronInfo":
        with info_file.open("rb") as stream:
            content = xmltodict.parse(stream, force_list=list(MetronInfo.list_fields.values()))
            return MetronInfo(**content["MetronInfo"])

    def to_file(self, info_file: Path):
        content = self.dict(by_alias=True, exclude_none=True)
        to_xml_list(mappings=MetronInfo.list_fields, content=content)
        content = clean_contents(content)

        content["@xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        content["@xsi:noNamespaceSchemaLocation"] = (
            "https://raw.githubusercontent.com/"
            "Metron-Project/metroninfo/master/drafts/"
            "v1.0/MetronInfo.xsd"
        )

        with info_file.open("w", encoding="UTF-8") as stream:
            xmltodict.unparse(
                {"MetronInfo": {k: content[k] for k in sorted(content, alg=ns.NA | ns.G)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
            )
