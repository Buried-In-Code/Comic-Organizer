__all__ = ["ComicInfo"]

import logging
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import xmltodict
from pydantic import BaseModel, Extra, Field, validator
from rich.prompt import Prompt

from ..console import CONSOLE, create_menu
from .metadata import Creator, Issue, Metadata, Publisher, Series, StoryArc

LOGGER = logging.getLogger(__name__)


def to_pascal_case(value: str) -> str:
    return value.replace("_", " ").title().replace(" ", "")


class ComicInfo(BaseModel):
    title: Optional[str] = None
    series: Optional[str] = None
    number: Optional[str] = None
    count: Optional[int] = None
    volume: Optional[int] = None
    alternate_series: Optional[str] = None
    alternate_number: Optional[str] = None
    alternate_count: Optional[int] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    writer: Optional[str] = None
    penciller: Optional[str] = None
    inker: Optional[str] = None
    colorist: Optional[str] = None
    letterer: Optional[str] = None
    cover_artist: Optional[str] = None
    editor: Optional[str] = None
    publisher: Optional[str] = None
    imprint: Optional[str] = None
    genre: Optional[str] = None
    web: Optional[str] = None
    page_count: Optional[int] = None
    language_iso: Optional[str] = Field(alias="LanguageISO", default=None)
    format: Optional[str] = None
    black_and_white: Optional[bool] = None
    manga: Optional[bool] = False
    right_to_left: Optional[bool] = False
    characters: Optional[str] = None
    teams: Optional[str] = None
    locations: Optional[str] = None
    scan_information: Optional[str] = None
    story_arc: Optional[str] = None
    series_group: Optional[str] = None
    age_rating: Optional[str] = None
    pages: List[Dict[str, str]] = Field(default_factory=list)
    community_rating: Optional[float] = None

    class Config:
        alias_generator = to_pascal_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.allow

    def __init__(self, **data):
        if "Pages" in data:
            data["Pages"] = data["Pages"]["Page"]
        data["RightToLeft"] = data["Manga"] if "Manga" in data else False
        super().__init__(**data)

    @validator("black_and_white", "manga", pre=True)
    def validate_optional_bool(cls, v) -> Optional[bool]:
        if v:
            if v in ["Yes", "YesAndRightToLeft"]:
                return True
            return False
        return None

    @validator("right_to_left", pre=True)
    def validate_rtl(cls, v) -> Optional[bool]:
        if v:
            if v == "YesAndRightToLeft":
                return True
            return False
        return None

    @property
    def story_arc_list(self) -> List[str]:
        if not self.alternate_series and not self.story_arc:
            return []
        if not self.alternate_series:
            return sorted(x.strip() for x in self.story_arc.split(","))
        if not self.story_arc:
            return sorted(x.strip() for x in self.alternate_series.split(","))
        return [
            *sorted(x.strip() for x in self.alternate_series.split(",")),
            *sorted(x.strip() for x in self.story_arc.split(",")),
        ]

    @property
    def cover_date(self) -> Optional[date]:
        if not self.year:
            return None
        return date(self.year, self.month or 1, self.day or 1)

    @property
    def writer_list(self) -> List[str]:
        if not self.writer:
            return []
        return sorted(x.strip() for x in self.writer.split(","))

    @property
    def penciller_list(self) -> List[str]:
        if not self.penciller:
            return []
        return sorted(x.strip() for x in self.penciller.split(","))

    @property
    def inker_list(self) -> List[str]:
        if not self.inker:
            return []
        return sorted(x.strip() for x in self.inker.split(","))

    @property
    def colorist_list(self) -> List[str]:
        if not self.colorist:
            return []
        return sorted(x.strip() for x in self.colorist.split(","))

    @property
    def colourist_list(self) -> List[str]:
        return self.colorist_list

    @property
    def letterer_list(self) -> List[str]:
        if not self.letterer:
            return []
        return sorted(x.strip() for x in self.letterer.split(","))

    @property
    def cover_artist_list(self) -> List[str]:
        if not self.cover_artist:
            return []
        return sorted(x.strip() for x in self.cover_artist.split(","))

    @property
    def editor_list(self) -> List[str]:
        if not self.editor:
            return []
        return sorted(x.strip() for x in self.editor.split(","))

    @property
    def genre_list(self) -> List[str]:
        if not self.genre:
            return []
        return sorted(x.strip() for x in self.genre.split(","))

    @property
    def character_list(self) -> List[str]:
        if not self.characters:
            return []
        return sorted(x.strip() for x in self.characters.split(","))

    @property
    def team_list(self) -> List[str]:
        if not self.teams:
            return []
        return sorted(x.strip() for x in self.teams.split(","))

    @property
    def location_list(self) -> List[str]:
        if not self.locations:
            return []
        return sorted(x.strip() for x in self.locations.split(","))

    def _fill_missing_fields(self):
        LOGGER.info("Fill in missing fields")
        if self.publisher is None:
            self.publisher = Prompt.ask("Publisher title", console=CONSOLE)
        if self.series is None:
            self.series = Prompt.ask("Series title", console=CONSOLE)
        if self.number is None:
            self.number = Prompt.ask("Issue number", console=CONSOLE)
        formats = ["Annual", "Comic", "Digital Chapter", "Hardcover", "Trade Paperback"]
        format_index = create_menu(options=formats, prompt="Issue format", default="Comic")
        self.format = "Comic"
        if format_index != 0:
            self.format = formats[format_index - 1]

    def to_metadata(self) -> Metadata:
        self._fill_missing_fields()

        # region Parse Creators
        creators = {}
        for writer in self.writer_list:
            if writer in creators:
                creators[writer].append("Writer")
            else:
                creators[writer] = ["Writer"]
        for penciller in self.penciller_list:
            if penciller in creators:
                creators[penciller].append("Penciller")
            else:
                creators[penciller] = ["Penciller"]
        for inker in self.inker_list:
            if inker in creators:
                creators[inker].append("Inker")
            else:
                creators[inker] = ["Inker"]
        for colourist in self.colourist_list:
            if colourist in creators:
                creators[colourist].append("Colourist")
            else:
                creators[colourist] = ["Colourist"]
        for letterer in self.letterer_list:
            if letterer in creators:
                creators[letterer].append("Letterer")
            else:
                creators[letterer] = ["Letterer"]
        for cover_artist in self.cover_artist_list:
            if cover_artist in creators:
                creators[cover_artist].append("Cover Artist")
            else:
                creators[cover_artist] = ["Cover Artist"]
        for editor in self.editor_list:
            if editor in creators:
                creators[editor].append("Editor")
            else:
                creators[editor] = ["Editor"]
        # endregion
        return Metadata(
            publisher=Publisher(
                imprint=self.imprint,
                # Sources
                title=self.publisher,
            ),
            series=Series(
                # Sources
                start_year=self.volume if self.volume and self.volume > 1900 else None,
                title=self.series,
                volume=self.volume if self.volume and self.volume < 1900 else 1,
            ),
            issue=Issue(
                characters=self.character_list,
                cover_date=self.cover_date,
                creators=sorted(
                    Creator(name=name, roles=sorted(roles)) for name, roles in creators.items()
                ),
                format=self.format,
                genres=self.genre_list,
                language=self.language_iso.lower() if self.language_iso else "en",
                locations=self.location_list,
                number=self.number,
                page_count=self.page_count,
                # Sources
                # Store date
                story_arcs=sorted({StoryArc(title=x) for x in self.story_arc_list}),
                summary=self.summary,
                teams=self.team_list,
                title=self.title,
            ),
            notes=self.notes,
        )

    @staticmethod
    def from_file(info_file: Path) -> "ComicInfo":
        with info_file.open("rb") as stream:
            content = xmltodict.parse(stream, force_list=["Page"])["ComicInfo"]
            return ComicInfo(**content)

    def to_file(self, info_file: Path):
        if self.manga is False:
            self.manga = None
        if self.right_to_left is False:
            self.right_to_left = None
        with info_file.open("w", encoding="UTF-8") as stream:
            content = self.dict(by_alias=True, exclude_none=True)
            content["@xmlns:xsd"] = "https://www.w3.org/2001/XMLSchema"
            content["@xmlns:xsi"] = "https://www.w3.org/2001/XMLSchema-instance"

            if "Pages" in content and content["Pages"]:
                content["Pages"] = {"Page": content["Pages"]}
            else:
                del content["Pages"]

            xmltodict.unparse(
                {"ComicInfo": {k: content[k] for k in sorted(content)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
            )
