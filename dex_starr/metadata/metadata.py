from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from pydantic import BaseModel as PyModel
from pydantic import Extra, Field

from dex_starr import __version__, yaml_setup


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
    imprint: str | None = None
    sources: dict[str, int] = Field(default_factory=dict)
    title: str

    @property
    def file_name(self) -> str:
        return sanitize(self.title)


class Series(BaseModel):
    sources: dict[str, int] = Field(default_factory=dict)
    start_year: int | None = Field(default=None, gt=1900)
    title: str
    volume: int = Field(default=1, gt=0)

    @property
    def file_name(self) -> str:
        if self.volume <= 1:
            return sanitize(self.title)
        return sanitize(f"{self.title} v{self.volume}")


class Issue(BaseModel):
    characters: list[str] = Field(default_factory=list)
    cover_date: date | None = None
    creators: dict[str, list[str]] = Field(default_factory=dict)
    format: str = "Comic"
    genres: list[str] = Field(default_factory=list)
    language_iso: str = "en"
    locations: list[str] = Field(default_factory=list)
    number: str
    page_count: int | None = Field(default=None, gt=0)
    sources: dict[str, int] = Field(default_factory=dict)
    store_date: date | None = None
    story_arcs: list[str] = Field(default_factory=list)
    summary: str | None = None
    teams: list[str] = Field(default_factory=list)
    title: str | None = None

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


class Metadata(BaseModel):
    publisher: Publisher
    series: Series
    issue: Issue
    notes: str | None = None

    @staticmethod
    def from_file(comic_info_file: Path) -> Metadata:
        with comic_info_file.open("r", encoding="UTF-8") as info_file:
            content = yaml_setup().load(info_file)
            return Metadata(**content["data"])

    def to_file(self, comic_info_file: Path):
        with comic_info_file.open("w", encoding="UTF-8") as info_file:
            json.dump(
                {"data": self.dict(by_alias=True), "meta": generate_meta()},
                info_file,
                sort_keys=True,
                default=str,
                indent=2,
                ensure_ascii=False,
            )


def generate_meta() -> dict[str, str]:
    return {"date": date.today().isoformat(), "tool": {"name": "Dex-Starr", "version": __version__}}
