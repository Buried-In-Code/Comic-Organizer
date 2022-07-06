from datetime import date
from enum import Enum
from pathlib import Path
from typing import List, Optional

import xmltodict
from pydantic import BaseModel, Extra, Field, validator

from dex_starr.metadata.metadata import FormatEnum as MetadataFormatEnum
from dex_starr.metadata.metadata import Issue, Metadata, Publisher
from dex_starr.metadata.metadata import Series as MetadataSeries


def to_pascal_case(value: str) -> str:
    return value.replace("_", " ").title().replace(" ", "")


class ComicPageEnum(Enum):
    FRONT_COVER = "FrontCover"
    INNER_COVER = "InnerCover"
    ROUNDUP = "Roundup"
    STORY = "Story"
    ADVERTISEMENT = "Advertisement"
    EDITORIAL = "Editorial"
    LETTERS = "Letters"
    PREVIEW = "Preview"
    BACK_COVER = "BackCover"
    OTHER = "Other"
    DELETED = "Deleted"


class Page(BaseModel):
    image: int = Field(alias="@Image")
    type: ComicPageEnum = Field(alias="@Type", default=ComicPageEnum.STORY)
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


class RoleEnum(Enum):
    WRITER = "Writer"
    SCRIPT = "Script"
    STORY = "Story"
    PLOT = "Plot"
    INTERVIEWER = "Interviewer"
    ARTIST = "Artist"
    PENCILLER = "Penciller"
    BREAKDOWNS = "Breakdowns"
    ILLUSTRATOR = "Illustrator"
    LAYOUTS = "Layouts"
    INKER = "Inker"
    EMBELLISHER = "Embellisher"
    FINISHES = "Finishes"
    INK_ASSISTS = "Ink Assists"
    COLORIST = "Colorist"
    COLOR_SEPARATIONS = "Color Separations"
    COLOR_ASSISTS = "Color Assists"
    COLOR_FLATS = "Color Flats"
    DIGITAL_ART_TECHNICIAN = "Digital Art Technician"
    GRAY_TONE = "Gray Tone"
    LETTERER = "Letterer"
    COVER = "Cover"
    EDITOR = "Editor"
    CONSULTING_EDITOR = "Consulting Editor"
    ASSISTANT_EDITOR = "Assistant Editor"
    ASSOCIATE_EDITOR = "Associate Editor"
    GROUP_EDITOR = "Group Editor"
    SENIOR_EDITOR = "Senior Editor"
    MANAGING_EDITOR = "Managing Editor"
    COLLECTION_EDITOR = "Collection Editor"
    PRODUCTION = "Production"
    DESIGNER = "Designer"
    LOGO_DESIGN = "Logo Design"
    TRANSLATOR = "Translator"
    SUPERVISING_EDITOR = "Supervising Editor"
    EXECUTIVE_EDITOR = "Executive Editor"
    EDITOR_IN_CHIEF = "Editor In Chief"
    PRESIDENT = "President"
    PUBLISHER = "Publisher"
    CHIEF_CREATIVE_OFFICER = "Chief Creative Officer"
    EXECUTIVE_PRODUCER = "Executive Producer"
    OTHER = "Other"


class Credit(BaseModel):
    creator: str
    roles: List[RoleEnum] = Field(default_factory=list)

    def __init__(self, **data):
        data["Roles"] = data["Roles"]["Role"]
        super().__init__(**data)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    @validator("roles", pre=True, each_item=True)
    def role_to_enum(cls, v: str) -> RoleEnum:
        return RoleEnum(v)


class AgeRatingEnum(Enum):
    UNKNOWN = "Unknown"
    ADULTS_ONLY_18 = "Adults Only 18+"
    EARLY_CHILDHOOD = "Early Childhood"
    EVERYONE = "Everyone"
    EVERYONE_10 = "Everyone 10+"
    G = "G"
    KIDS_TO_ADULTS = "Kids to Adults"
    M = "M"
    MA15 = "MA15+"
    MATURE_17 = "Mature 17+"
    PG = "PG"
    R18 = "R18+"
    RATING_PENDING = "Rating Pending"
    TEEN = "Teen"
    X18 = "X18+"


class GTIN(BaseModel):
    isbn: Optional[str] = Field(alias="ISBN", default=None)
    upc: Optional[str] = Field(alias="UPC", default=None)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class InformationSourceEnum(Enum):
    COMICVINE = "Comic Vine"
    GRAND_COMICS_DATABASE = "Grand Comics Database"
    METRON = "Metron"
    LEAGUE_OF_COMIC_GEEKS = "League of Comic Geeks"


class Source(BaseModel):
    source: InformationSourceEnum = Field(alias="@source")
    value: int = Field(alias="#text", gt=0)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    @validator("source", pre=True)
    def source_to_enum(cls, v: str) -> InformationSourceEnum:
        return InformationSourceEnum(v)


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


class GenreEnum(Enum):
    ADULT = "Adult"
    CRIME = "Crime"
    ESPIONAGE = "Espionage"
    FANTASY = "Fantasy"
    HISTORICAL = "Historical"
    HORROR = "Horror"
    HUMOR = "Humor"
    MANGA = "Manga"
    PARODY = "Parody"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"
    SPORT = "Sport"
    SUPER_HERO = "Super-Hero"
    WAR = "War"
    WESTERN = "Western"


class CurrencyEnum(Enum):
    POUNDS = "pounds"
    EUROS = "euros"
    DOLLARS = "dollars"


class Price(BaseModel):
    currency: CurrencyEnum = Field(alias="@currency")
    value: float = Field(alias="#text")

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    @validator("currency", pre=True)
    def currency_to_enum(cls, v: str) -> CurrencyEnum:
        return CurrencyEnum(v)


class FormatEnum(Enum):
    ANNUAL = "Annual"
    GRAPHIC_NOVEL = "Graphic Novel"
    LIMITED = "Limited"
    ONE_SHOT = "One-Shot"
    SERIES = "Series"
    TRADE_PAPERBACK = "Trade Paperback"

    def to_metadata(self) -> MetadataFormatEnum:
        if self == FormatEnum.ANNUAL:
            return MetadataFormatEnum.ANNUAL
        elif self == FormatEnum.TRADE_PAPERBACK:
            return MetadataFormatEnum.TRADE_PAPERBACK
        return MetadataFormatEnum.COMIC


class Series(BaseModel):
    lang: str = Field(alias="@lang", default="EN")
    name: str
    sort_name: str
    type: FormatEnum

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    @validator("type", pre=True)
    def type_to_enum(cls, v: str) -> FormatEnum:
        return FormatEnum(v)


class MetronInfo(BaseModel):
    id: Optional[Source] = Field(alias="ID", default=None)
    publisher: str
    series: Series
    volume: Optional[int] = None
    collection_title: Optional = None
    number: Optional[str] = None
    stories: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    price: Optional[Price] = None
    cover_date: date
    store_date: Optional[date] = None
    page_count: Optional[int] = None
    genres: List[GenreEnum] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    arcs: List[Arc] = Field(default_factory=list)
    characters: List[str] = Field(default_factory=list)
    teams: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    reprints: List[Reprint] = Field(default_factory=list)
    gtin: Optional[GTIN] = Field(alias="GTIN", default=None)
    black_and_white: bool = False
    age_rating: AgeRatingEnum = AgeRatingEnum.UNKNOWN
    url: Optional[str] = Field(alias="URL", default=None)
    credits: List[Credit] = Field(default_factory=list)
    pages: List[Page] = Field(default_factory=list)

    class Config:
        alias_generator = to_pascal_case
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    def __init__(self, **data):
        data["Stories"] = data["Stories"]["Story"]
        data["Genres"] = data["Genres"]["Genre"]
        data["Tags"] = data["Tags"]["Tag"]
        data["Arcs"] = data["Arcs"]["Arc"]
        data["Characters"] = data["Characters"]["Character"]
        data["Teams"] = data["Teams"]["Team"]
        data["Locations"] = data["Locations"]["Location"]
        data["Reprints"] = data["Reprints"]["Reprint"]
        data["Credits"] = data["Credits"]["Credit"]
        data["Pages"] = data["Pages"]["Page"]
        super().__init__(**data)

    @validator("genres", pre=True, each_item=True)
    def genre_to_enum(cls, v: str) -> GenreEnum:
        return GenreEnum(v)

    @validator("age_rating", pre=True)
    def age_rating_to_enum(cls, v: str) -> AgeRatingEnum:
        return AgeRatingEnum(v)

    def to_metadata(self) -> Metadata:
        return Metadata(
            publisher=Publisher(title=self.publisher),
            series=MetadataSeries(title=self.series.name, volume=self.volume),
            issue=Issue(
                characters=self.characters,
                cover_date=self.cover_date,
                creators={c.creator: sorted(r.value for r in c.roles) for c in self.credits},
                format=self.series.type.to_metadata(),
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
            content = xmltodict.parse(stream)["MetronInfo"]
            for key in content.copy().keys():
                if key.startswith("@xmlns"):
                    del content[key]
            return MetronInfo(**content)

    def to_file(self, info_file: Path):
        with info_file.open("w", encoding="UTF-8") as stream:
            unsorted = self.dict(by_alias=True)
            xmltodict.unparse(
                {"MetronInfo": {k: unsorted[k] for k in sorted(unsorted)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
                indent=" " * 2,
            )
