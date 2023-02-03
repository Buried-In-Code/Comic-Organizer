__all__ = ["ComicInfo", "Page"]

from datetime import date
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

import xmltodict
from natsort import humansorted as sorted
from natsort import ns
from pydantic import Field, validator
from rich.prompt import Prompt

from dex_starr.console import CONSOLE
from dex_starr.models import PascalModel, clean_contents, from_xml_list, to_xml_list
from dex_starr.models.comic_info.enums import AgeRating, Manga, PageType, YesNo
from dex_starr.models.metadata.schema import Metadata


class Page(PascalModel):
    image: int = Field(alias="@Image")
    page_type: PageType = Field(alias="@Type", default=PageType.STORY)
    double_page: bool = Field(alias="@DoublePage", default=False)
    image_size: int = Field(alias="@ImageSize", default=0)
    key: Optional[str] = Field(alias="@Key", default=None)
    bookmark: Optional[str] = Field(alias="@Bookmark", default=None)
    image_width: Optional[int] = Field(alias="@ImageWidth", default=None)
    image_height: Optional[int] = Field(alias="@ImageHeight", default=None)

    @validator("page_type", pre=True)
    def to_page_type_enum(cls, v) -> PageType:
        if isinstance(v, PageType):
            return v
        return PageType.load(str(v))

    def __lt__(self, other):
        if not isinstance(other, Page):
            raise NotImplementedError()
        return self.image < other.image

    def __eq__(self, other):
        if not isinstance(other, Page):
            raise NotImplementedError()
        return self.image == other.image

    def __hash__(self):
        return hash((type(self), self.image))


class ComicInfo(PascalModel):
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
    page_count: int = 0
    language_iso: Optional[str] = Field(alias="LanguageISO", default=None)
    format: Optional[str] = None
    black_and_white: YesNo = Field(default=YesNo.UNKNOWN)
    manga: Manga = Field(default=Manga.UNKNOWN)
    characters: Optional[str] = None
    teams: Optional[str] = None
    locations: Optional[str] = None
    scan_information: Optional[str] = None
    story_arc: Optional[str] = None
    series_group: Optional[str] = None
    age_rating: AgeRating = Field(default=AgeRating.UNKNOWN)
    pages: List[Page] = Field(default_factory=list)
    community_rating: Optional[float] = Field(default=None, ge=0, le=5)

    list_fields: ClassVar[Dict[str, str]] = {"Pages": "Page"}

    def __init__(self, **data):
        from_xml_list(mappings=ComicInfo.list_fields, content=data)
        super().__init__(**data)

    @validator("black_and_white", pre=True)
    def to_yes_no_enum(cls, v) -> YesNo:
        if isinstance(v, YesNo):
            return v
        return YesNo.load(str(v))

    @validator("manga", pre=True)
    def to_manga_enum(cls, v) -> Manga:
        if isinstance(v, Manga):
            return v
        return Manga.load(str(v))

    @validator("age_rating", pre=True)
    def to_age_rating_enum(cls, v) -> AgeRating:
        if isinstance(v, AgeRating):
            return v
        return AgeRating.load(str(v))

    @property
    def story_arc_list(self) -> List[str]:
        if not self.alternate_series and not self.story_arc:
            return []
        if not self.alternate_series:
            return sorted({x.strip() for x in self.story_arc.split(",")}, alg=ns.NA | ns.G)
        if not self.story_arc:
            return sorted({x.strip() for x in self.alternate_series.split(",")}, alg=ns.NA | ns.G)
        return sorted(
            {
                *[x.strip() for x in self.alternate_series.split(",")],
                *[x.strip() for x in self.story_arc.split(",")],
            },
            alg=ns.NA | ns.G,
        )

    @property
    def cover_date(self) -> Optional[date]:
        if not self.year:
            return None
        return date(self.year, self.month or 1, self.day or 1)

    @property
    def writer_list(self) -> List[str]:
        if not self.writer:
            return []
        return sorted({x.strip() for x in self.writer.split(",")}, alg=ns.NA | ns.G)

    @property
    def penciller_list(self) -> List[str]:
        if not self.penciller:
            return []
        return sorted({x.strip() for x in self.penciller.split(",")}, alg=ns.NA | ns.G)

    @property
    def inker_list(self) -> List[str]:
        if not self.inker:
            return []
        return sorted({x.strip() for x in self.inker.split(",")}, alg=ns.NA | ns.G)

    @property
    def colourist_list(self) -> List[str]:
        if not self.colorist:
            return []
        return sorted({x.strip() for x in self.colorist.split(",")}, alg=ns.NA | ns.G)

    @property
    def colorist_list(self) -> List[str]:
        return self.colourist_list

    @property
    def letterer_list(self) -> List[str]:
        if not self.letterer:
            return []
        return sorted({x.strip() for x in self.letterer.split(",")}, alg=ns.NA | ns.G)

    @property
    def cover_artist_list(self) -> List[str]:
        if not self.cover_artist:
            return []
        return sorted({x.strip() for x in self.cover_artist.split(",")}, alg=ns.NA | ns.G)

    @property
    def editor_list(self) -> List[str]:
        if not self.editor:
            return []
        return sorted({x.strip() for x in self.editor.split(",")}, alg=ns.NA | ns.G)

    @property
    def genre_list(self) -> List[str]:
        if not self.genre:
            return []
        return sorted({x.strip() for x in self.genre.split(",")}, alg=ns.NA | ns.G)

    @property
    def character_list(self) -> List[str]:
        if not self.characters:
            return []
        return sorted({x.strip() for x in self.characters.split(",")}, alg=ns.NA | ns.G)

    @property
    def team_list(self) -> List[str]:
        if not self.teams:
            return []
        return sorted({x.strip() for x in self.teams.split(",")}, alg=ns.NA | ns.G)

    @property
    def location_list(self) -> List[str]:
        if not self.locations:
            return []
        return sorted({x.strip() for x in self.locations.split(",")}, alg=ns.NA | ns.G)

    def to_metadata(self, enter_missing: bool = True) -> Metadata:
        from dex_starr.models.metadata.enums import Format, Role
        from dex_starr.models.metadata.schema import (
            Creator,
            Issue,
            Page,
            Publisher,
            Series,
            StoryArc,
        )

        # region Parse Creators
        creators = {}
        creator_mappings = {
            Role.WRITER: self.writer_list,
            Role.PENCILLER: self.penciller_list,
            Role.INKER: self.inker_list,
            Role.COLOURIST: self.colourist_list,
            Role.LETTERER: self.letterer_list,
            Role.COVER_ARTIST: self.cover_artist_list,
            Role.EDITOR: self.editor_list,
        }
        for key, value in creator_mappings.items():
            for creator in value:
                if creator not in creators:
                    creators[creator] = []
                creators[creator].append(key)
        # endregion
        return Metadata(
            publisher=Publisher(
                imprint=self.imprint,
                # TODO: Resources
                title=self.publisher or Prompt.ask("Publisher title", console=CONSOLE),
            ),
            series=Series(
                # TODO: Resources
                start_year=self.volume if self.volume and self.volume > 1900 else None,
                title=self.series or Prompt.ask("Series title", console=CONSOLE),
                volume=self.volume if self.volume and self.volume < 1900 else 1,
            ),
            issue=Issue(
                characters=self.character_list,
                cover_date=self.cover_date,
                creators=sorted(
                    {
                        Creator(name=name, roles=sorted(roles, alg=ns.NA | ns.G))
                        for name, roles in creators.items()
                    },
                    alg=ns.NA | ns.G,
                ),
                format=self.format or Format.COMIC,
                genres=self.genre_list,
                language=self.language_iso.lower() if self.language_iso else "en",
                locations=self.location_list,
                number=self.number or "1",
                page_count=self.page_count,
                # TODO: Resources
                # TODO: Store date
                story_arcs=sorted(
                    {StoryArc(title=x) for x in self.story_arc_list}, alg=ns.NA | ns.G
                ),
                summary=self.summary,
                teams=self.team_list,
                title=self.title,
            ),
            pages=sorted(
                {
                    Page(
                        image=x.image,
                        page_type=str(x.page_type),
                        double_page=x.double_page,
                        key=x.key,
                        bookmark=x.bookmark,
                        image_size=x.image_size,
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
    def from_file(info_file: Path) -> "ComicInfo":
        with info_file.open("rb") as stream:
            content = xmltodict.parse(stream, force_list=list(ComicInfo.list_fields.values()))
            return ComicInfo(**content["ComicInfo"])

    def to_file(self, info_file: Path):
        content = self.dict(by_alias=True, exclude_none=True)
        to_xml_list(mappings=ComicInfo.list_fields, content=content)
        content = clean_contents(content)

        content["@xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        content["@xsi:noNamespaceSchemaLocation"] = (
            "https://raw.githubusercontent.com/"
            "Buried-In-Code/Dex-Starr/main/schemas/"
            "ComicInfo.xsd"
        )

        with info_file.open("w", encoding="UTF-8") as stream:
            xmltodict.unparse(
                {"ComicInfo": {k: content[k] for k in sorted(content, alg=ns.NA | ns.G)}},
                output=stream,
                short_empty_elements=True,
                pretty=True,
            )
