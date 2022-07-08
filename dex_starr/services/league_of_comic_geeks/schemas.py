from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Extra, Field, validator

from dex_starr.metadata.metadata import FormatEnum


class ComicResult(BaseModel):
    comic_id: int = Field(alias="id")
    parent_id: int
    publisher_id: int
    publisher_name: str
    series_id: int
    series_name: str
    series_volume: int
    series_end: int
    series_begin: int
    title: str
    parent_title: Optional[str] = None
    release_date: date = Field(alias="date_release")
    description: Optional[str] = None
    format: FormatEnum
    variant: int
    price: float
    modified_date: datetime = Field(alias="date_modified")

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    @validator("format", pre=True)
    def format_to_enum(cls, v: str) -> FormatEnum:
        return FormatEnum(v)


class Series(BaseModel):
    series_id: int = Field(alias="id")
    publisher_id: int
    title: str
    description: str
    volume: int
    year_begin: int
    year_end: int
    date_added: datetime
    date_modified: datetime
    publisher_name: str
    publisher_slug: str
    comic_id: int
    series_string: int

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Details(BaseModel):
    comic_id: int = Field(alias="id")
    parent_id: int
    publisher_id: int
    series_id: int
    title: str
    release_date: date = Field(alias="date_release")
    format: FormatEnum
    variant: int
    pages: int
    price: float
    date_added: datetime
    date_modified: datetime
    description: str
    parent_title: Optional[str] = None
    publisher_name: str
    publisher_slug: str

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    @validator("format", pre=True)
    def format_to_enum(cls, v: str) -> FormatEnum:
        return FormatEnum(v)


class Creator(BaseModel):
    creator_id: int = Field(alias="id")
    name: str
    slug: str
    role_id: int
    role: str

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Character(BaseModel):
    character_id: int = Field(alias="id")
    parent_id: int
    type_id: int
    name: str
    universe_id: Optional[int] = None
    date_added: datetime
    date_modified: datetime
    parent_name: Optional[str] = None
    full_name: str
    universe_name: str
    publisher_name: str

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Comic(BaseModel):
    details: Details
    creators: List[Creator]
    characters: List[Character]
    series: Series

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow
