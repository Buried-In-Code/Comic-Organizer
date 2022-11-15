__all__ = ["Publisher", "Series", "Creator", "StoryArc", "Issue", "Metadata"]

import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from pydantic import BaseModel as PyModel
from pydantic import Extra, Field

from dex_starr import __version__
from dex_starr.console import create_menu

LOGGER = logging.getLogger(__name__)


def sanitize(dirty: str) -> str:
    dirty = re.sub(r"[^0-9a-zA-Z& ]+", "", dirty.replace("-", " "))
    dirty = " ".join(dirty.split())
    return dirty.replace(" ", "-")


def to_camel_case(value: str) -> str:
    temp = value.replace("_", " ").title().replace(" ", "")
    return temp[0].lower() + temp[1:]


class BaseModel(PyModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore


class Publisher(BaseModel):
    imprint: Optional[str] = None
    sources: Dict[str, int] = Field(default_factory=dict)
    title: str

    @property
    def file_name(self) -> str:
        return sanitize(self.title)

    def __lt__(self, other):
        if not isinstance(other, Publisher):
            raise NotImplementedError()
        return self.title < other.title


class Series(BaseModel):
    sources: Dict[str, int] = Field(default_factory=dict)
    start_year: Optional[int] = Field(default=None, gt=1900)
    title: str
    volume: int = Field(default=1, gt=0)

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


class Creator(BaseModel):
    name: str
    roles: List[str] = Field(default_factory=list)

    def __lt__(self, other):
        if not isinstance(other, Creator):
            raise NotImplementedError()
        return self.name < other.name


class StoryArc(BaseModel):
    title: str
    number: Optional[int] = None

    def __lt__(self, other):
        if not isinstance(other, StoryArc):
            raise NotImplementedError()
        if self.title != other.title:
            return self.title < other.title
        return self.number < other.number

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Issue(BaseModel):
    characters: List[str] = Field(default_factory=list)
    cover_date: Optional[date] = None
    creators: List[Creator] = Field(default_factory=list)
    format: str = "Comic"
    genres: List[str] = Field(default_factory=list)
    language: str = "en"
    locations: List[str] = Field(default_factory=list)
    number: str
    page_count: Optional[int] = Field(default=None, gt=0)
    sources: Dict[str, int] = Field(default_factory=dict)
    store_date: Optional[date] = None
    story_arcs: List[StoryArc] = Field(default_factory=list)
    summary: Optional[str] = None
    teams: List[str] = Field(default_factory=list)
    title: Optional[str] = None

    @property
    def file_name(self) -> str:
        if self.format == "Annual":
            return f"-Annual-#{self.number.zfill(2)}"
        if self.format == "Digital Chapter":
            return f"-Chapter-#{self.number.zfill(2)}"
        if self.format == "Hardcover":
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-HC"
        if self.format == "Trade Paperback":
            if self.number != "0":
                filename = f"-#{self.number.zfill(2)}"
            elif self.title:
                filename = "-" + sanitize(self.title)
            else:
                filename = ""
            return f"{filename}-TP"
        return f"-#{self.number.zfill(3)}"

    def __lt__(self, other):
        if not isinstance(other, Issue):
            raise NotImplementedError()
        if self.format != other.format:
            return self.format < other.format
        if self.number != other.number:
            return self.number < other.number
        return self.cover_date < other.cover_date


class Metadata(BaseModel):
    publisher: Publisher
    series: Series
    issue: Issue
    notes: Optional[str] = None

    @staticmethod
    def from_file(comic_info_file: Path) -> "Metadata":
        with comic_info_file.open("r", encoding="UTF-8") as info_file:
            content = json.load(info_file)
            return Metadata(**content["data"])

    def to_file(self, comic_info_file: Path):
        self.issue.creators = uniform_creators(self.issue.creators)
        self.issue.genres = uniform_genres(self.issue.genres)
        with comic_info_file.open("w", encoding="UTF-8") as info_file:
            json.dump(
                {"data": self.dict(by_alias=True), "meta": generate_meta()},
                info_file,
                sort_keys=True,
                default=str,
                indent=2,
                ensure_ascii=False,
            )

    def __lt__(self, other):
        if not isinstance(other, Metadata):
            raise NotImplementedError()
        if self.publisher != other.publisher:
            return self.publisher < other.publisher
        if self.series != other.series:
            return self.series < other.series
        return self.issue < other.issue


def generate_meta() -> Dict[str, str]:
    return {"date": date.today().isoformat(), "tool": {"name": "Dex-Starr", "version": __version__}}


valid_creator_roles = [
    "Artist",
    "Assistant Editor",
    "Associate Editor",
    "Breakdowns",
    "Chief Creative Officer",
    "Collection Editor",
    "Colour Assists",
    "Colour Flats",
    "Colour Separations",
    "Colourist",
    "Consulting Editor",
    "Cover Artist",
    "Creator",
    "Designer",
    "Digital Art Technician",
    "Editor",
    "Editor In Chief",
    "Embellisher",
    "Executive Editor",
    "Executive Producer",
    "Finishes",
    "Gray Tone",
    "Group Editor",
    "Illustrator",
    "Ink Assists",
    "Inker",
    "Interviewer",
    "Layouts",
    "Letterer",
    "Logo Design",
    "Managing Editor",
    "Other",
    "Penciller",
    "Plot",
    "President",
    "Production",
    "Publisher",
    "Script",
    "Senior Editor",
    "Story",
    "Supervising Editor",
    "Translator",
    "Variant Cover Artist",
    "Writer",
]
valid_genres = [
    "Action",
    "Adult",
    "Adventure",
    "Crime",
    "Espionage",
    "Fantasy",
    "Historical",
    "Horror",
    "Humor",
    "Manga",
    "Parody",
    "Romance",
    "Science Fiction",
    "Sport",
    "Super-Hero",
    "Video Games",
    "War",
    "Western",
]


def uniform_creators(creators: Iterable[Creator]) -> List[Creator]:
    auto_resolve = {
        "Colorist": "Colourist",
        "Penciler": "Penciller",
        "Editor-In-Chief": "Editor In Chief",
    }
    for creator in creators:
        unknown_creator_roles = []
        for role in creator.roles:
            if role in valid_creator_roles:
                continue
            unknown_creator_roles.append(role)
        for role in unknown_creator_roles:
            if role in auto_resolve:
                LOGGER.debug(f"Resolving '{role}' to '{auto_resolve[role]}' for {creator.name}")
                creator.roles.append(auto_resolve[role])
                continue
            LOGGER.info(f"Unknown Creator role found for {creator.name}: '{role}'")
            if index := create_menu(
                options=valid_creator_roles,
                prompt="Select a replacement role",
                default="None of the Above",
            ):
                creator.roles.append(valid_creator_roles[index - 1])
        creator.roles = {x for x in creator.roles if x in valid_creator_roles}
    return sorted(x for x in creators if x.roles)


def uniform_genres(genres: Iterable[str]) -> List[str]:
    genres = list(genres)
    unknown_genres = []
    for genre in genres:
        if genre in valid_genres:
            continue
        unknown_genres.append(genre)
    for genre in unknown_genres:
        if genre == "Comedy":
            LOGGER.debug("Resolved 'Comedy' to 'Humor'")
            genres.append("Humor")
            continue
        LOGGER.info(f"Unknown genre found: '{genre}'")
        if index := create_menu(
            options=valid_genres, prompt="Select a replacement genre", default="None of the Above"
        ):
            genres.append(valid_genres[index - 1])
    return sorted(x for x in set(genres) if x in valid_genres)
