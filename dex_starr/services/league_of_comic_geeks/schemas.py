from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Extra, Field


class ComicResult(BaseModel):
    comic_id: int = Field(alias="id")
    format: str
    description: Optional[str] = None
    modified_date: datetime = Field(alias="date_modified")
    parent_id: int
    parent_title: Optional[str] = None
    publisher_id: int
    publisher_name: str
    release_date: date = Field(alias="date_release")
    series_begin: int
    series_end: int
    series_id: int
    series_name: str
    series_volume: int
    title: str
    variant: int

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Series(BaseModel):
    comic_id: int
    date_added: datetime
    date_modified: datetime
    description: str
    publisher_id: int
    publisher_name: str
    series_id: int = Field(alias="id")
    title: str
    volume: int
    year_begin: int
    year_end: int

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Details(BaseModel):
    comic_id: int = Field(alias="id")
    date_added: datetime
    date_modified: datetime
    description: str
    format: str
    pages: int
    parent_id: int
    parent_title: Optional[str] = None
    price: float
    publisher_id: int
    publisher_name: str
    publisher_slug: str
    release_date: date = Field(alias="date_release")
    series_id: int
    title: str
    variant: int

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Creator(BaseModel):
    creator_id: int = Field(alias="id")
    name: str
    role_id: str
    role: str

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow

    @property
    def roles(self) -> Dict[int, str]:
        role_dict = {}
        id_list = self.role_id.split(",")
        role_list = self.role.split(",")
        for index, id in enumerate(id_list):
            role_dict[int(id)] = role_list[index].strip().title()
        return role_dict


class Character(BaseModel):
    character_id: int = Field(alias="id")
    date_added: datetime
    date_modified: datetime
    full_name: str
    name: str
    parent_id: int
    parent_name: Optional[str] = None

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow


class Comic(BaseModel):
    characters: List[Character]
    creators: List[Creator]
    details: Details
    series: Series

    class Config:
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        extra = Extra.allow
