import json
from datetime import date
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import xmltodict
from jsonschema import ValidationError
from jsonschema import validate as validate_json
from yamale import YamaleError, make_data, make_schema
from yamale import validate as validate_yaml

from dex_starr import __version__, get_field
from dex_starr.console import ConsoleLog

CONSOLE = ConsoleLog(__name__)


class FormatEnum(Enum):
    ANNUAL = auto()
    COMIC = auto()
    DIGITAL_CHAPTER = auto()
    HARDCOVER = auto()
    TRADE_PAPERBACK = auto()

    @staticmethod
    def select() -> Optional["FormatEnum"]:
        response = CONSOLE.prompt(
            "Enter Format", choices=[x.get_title() for x in sorted(FormatEnum)], default=FormatEnum.COMIC.get_title()
        )
        return FormatEnum.get(name=response)

    @staticmethod
    def get(name: str) -> Optional["FormatEnum"]:
        for entry in FormatEnum:
            if entry.get_title().lower() == name.lower():
                return entry
        return None

    def get_title(self) -> str:
        return self.name.replace("_", " ").title()

    def __lt__(self, other):
        if not isinstance(other, FormatEnum):
            raise NotImplementedError()
        return self.name < other.name


class Identifier:
    def __init__(self, service: str, id: Optional[Union[str, int]] = None, url: Optional[str] = None):
        self.service = service
        self.id = id
        self.url = url

    @staticmethod
    def load(data: Dict[str, Any]) -> "Identifier":
        return Identifier(service=data["Service"], id=data["ID"], url=data["URL"])

    def dump(self) -> Dict[str, Any]:
        return {"Service": self.service, "ID": self.id, "URL": self.url}


class Publisher:
    def __init__(self, title: str):
        self.title = title
        self.identifiers: List[Identifier] = []

    @staticmethod
    def load(data: Dict[str, Any]) -> "Publisher":
        publisher = Publisher(title=data["Title"])

        publisher.identifiers = [Identifier.load(x) for x in data["Identifiers"]]

        return publisher

    def dump(self) -> Dict[str, Any]:
        return {
            "Title": self.title,
            "Identifiers": [x.dump() for x in self.identifiers],
        }

    def set_pulled_metadata(self, pulled_metadata: Dict[str, Any], resolve_manually: bool = False):
        try:
            if "title" in pulled_metadata:
                self.title = get_field(pulled_metadata, "Publisher", "title", resolve_manually)
        except ValueError:
            pass


class Series:
    def __init__(self, title: str, volume: int = 1):
        self.title = title
        self.volume = volume
        self.identifiers: List[Identifier] = []
        self.start_year: Optional[int] = None

    @staticmethod
    def load(data: Dict[str, Any]) -> "Series":
        series = Series(title=data["Title"], volume=data["Volume"])

        series.identifiers = [Identifier.load(x) for x in data["Identifiers"]]
        series.start_year = data["Start Year"]

        return series

    def dump(self) -> Dict[str, Any]:
        return {
            "Title": self.title,
            "Volume": self.volume if self.volume >= 1 else 1,
            "Identifiers": [x.dump() for x in self.identifiers],
            "Start Year": self.start_year if self.start_year >= 1900 else 1900,
        }

    def set_pulled_metadata(self, pulled_metadata: Dict[str, Any], resolve_manually: bool = False):
        try:
            if "title" in pulled_metadata:
                self.title = get_field(pulled_metadata, "Series", "title", resolve_manually)
        except ValueError:
            pass
        try:
            if "volume" in pulled_metadata:
                self.volume = get_field(pulled_metadata, "Series", "volume", resolve_manually)
        except ValueError:
            pass
        try:
            if "start_year" in pulled_metadata:
                self.start_year = get_field(pulled_metadata, "Series", "start_year", resolve_manually)
        except ValueError:
            pass


class Creator:
    def __init__(self, name: str, roles: List[str]):
        self.name = name
        self.roles = roles

    @staticmethod
    def load(data: Dict[str, Any]) -> "Creator":
        creator = Creator(name=data["Name"], roles=data["Roles"])

        return creator

    def dump(self) -> Dict[str, Any]:
        return {"Name": self.name, "Roles": self.roles}


class Comic:
    def __init__(self, number: str, format_: FormatEnum = FormatEnum.COMIC):
        self.format_ = format_
        self.number = number

        self.cover_date: Optional[date] = None
        self.creators: List[Creator] = []
        self.genres: List[str] = []
        self.identifiers: List[Identifier] = []
        self.language_iso: Optional[str] = None
        self.page_count: Optional[int] = None
        self.store_date: Optional[date] = None
        self.summary: Optional[str] = None
        self.title: Optional[str] = None

    @staticmethod
    def load(data: Dict[str, Any]) -> "Comic":
        comic = Comic(
            format_=FormatEnum.get(data["Format"]) or FormatEnum.COMIC,
            number=data["Number"],
        )

        comic.cover_date = date.fromisoformat(data["Cover Date"]) if data["Cover Date"] else None
        comic.creators = [Creator.load(x) for x in data["Creators"]]
        comic.genres = data["Genres"]
        comic.identifiers = [Identifier.load(x) for x in data["Identifiers"]]
        comic.language_iso = data["Language ISO"]
        comic.page_count = data["Page Count"]
        comic.store_date = date.fromisoformat(data["Store Date"]) if data["Store Date"] else None
        comic.summary = data["Summary"]
        comic.title = data["Title"]

        return comic

    def dump(self) -> Dict[str, Any]:
        return {
            "Format": self.format_.get_title(),
            "Number": self.number,
            "Cover Date": self.cover_date.isoformat() if self.cover_date else None,
            "Creators": [x.dump() for x in self.creators],
            "Genres": self.genres,
            "Identifiers": [x.dump() for x in self.identifiers],
            "Language ISO": self.language_iso,
            "Page Count": self.page_count if self.page_count >= 1 else 1,
            "Store Date": self.store_date.isoformat() if self.store_date else None,
            "Summary": self.summary,
            "Title": self.title,
        }

    def set_pulled_metadata(self, pulled_metadata: Dict[str, Any], resolve_manually: bool = False):
        try:
            if "format" in pulled_metadata:
                self.format_ = get_field(pulled_metadata, "Comic", "format", resolve_manually)
        except ValueError:
            pass
        try:
            if "number" in pulled_metadata:
                self.number = get_field(pulled_metadata, "Comic", "number", resolve_manually)
        except ValueError:
            pass
        try:
            if "cover_date" in pulled_metadata:
                self.cover_date = get_field(pulled_metadata, "Comic", "cover_date", resolve_manually)
        except ValueError:
            pass
        # TODO: Creators
        # TODO: Genres
        try:
            if "page_count" in pulled_metadata:
                self.page_count = get_field(pulled_metadata, "Comic", "page_count", resolve_manually)
        except ValueError:
            pass
        try:
            if "store_date" in pulled_metadata:
                self.store_date = get_field(pulled_metadata, "Comic", "store_date", resolve_manually)
        except ValueError:
            pass
        try:
            if "summary" in pulled_metadata:
                self.summary = get_field(pulled_metadata, "Comic", "summary", resolve_manually)
        except ValueError:
            pass
        try:
            if "title" in pulled_metadata:
                self.title = get_field(pulled_metadata, "Comic", "title", resolve_manually)
        except ValueError:
            pass


class Metadata:
    def __init__(self, publisher: Publisher, series: Series, comic: Comic, notes: Optional[str] = None):
        self.publisher = publisher
        self.series = series
        self.comic = comic
        self.notes = notes

    @staticmethod
    def create() -> "Metadata":
        metadata = Metadata(
            publisher=Publisher(title=CONSOLE.prompt("Publisher Title")),
            series=Series(title=CONSOLE.prompt("Series Title"), volume=CONSOLE.prompt_int("Series Volume", default=1)),
            comic=Comic(
                format_=FormatEnum.select() or FormatEnum.COMIC, number=CONSOLE.prompt("Issue Number", default="0")
            ),
        )
        if (
            metadata.comic.format_ in [FormatEnum.TRADE_PAPERBACK, FormatEnum.HARDCOVER]
            and metadata.comic.number == "0"
        ):
            metadata.comic.title = CONSOLE.prompt("Issue Title") or None
        return metadata

    @staticmethod
    def load(data: Dict[str, Any]) -> "Metadata":
        return Metadata(
            publisher=Publisher.load(data["Data"]["Publisher"]),
            series=Series.load(data["Data"]["Series"]),
            comic=Comic.load(data["Data"]["Comic"]),
            notes=data["Meta"]["Notes"] if "Notes" in data["Meta"] else None,
        )

    def dump(self) -> Dict[str, Any]:
        output = {
            "Data": {
                "Publisher": self.publisher.dump(),
                "Series": self.series.dump(),
                "Comic": self.comic.dump(),
            },
            "Meta": {"Date": date.today().isoformat(), "Tool": {"Name": "Dex-Starr", "Version": __version__}},
        }
        if self.notes:
            output["Meta"]["Notes"] = self.notes
        return output

    def set_pulled_metadata(self, pulled_metadata: Dict[str, Any], resolve_manually: bool = False):
        self.publisher.set_pulled_metadata(pulled_metadata["publisher"], resolve_manually)
        self.series.set_pulled_metadata(pulled_metadata["series"], resolve_manually)
        self.comic.set_pulled_metadata(pulled_metadata["comic"], resolve_manually)


def parse_yaml(info_file: Path) -> Optional[Metadata]:
    schema_file = Path("schemas").joinpath("ComicInfo.schema.yaml")
    data = make_data(content=info_file.read_text(encoding="UTF-8"), parser="ruamel")

    try:
        validate_yaml(make_schema(content=schema_file.read_text(encoding="UTF-8"), parser="ruamel"), data)
        return Metadata.load(data[0][0])
    except YamaleError as ye:
        CONSOLE.print_dict(data[0][0], title="Validation Error", subtitle=ye.message)
    return None


def parse_json(info_file: Path) -> Optional[Metadata]:
    schema_file = Path("schemas").joinpath("ComicInfo.schema.json")
    with schema_file.open("r", encoding="UTF-8") as schema_stream:
        schema_data = json.load(schema_stream)
    with info_file.open("r", encoding="UTF-8") as info_stream:
        info_data = json.load(info_stream)
    try:
        validate_json(instance=info_data, schema=schema_data)
        return Metadata.load(info_data)
    except ValidationError as ve:
        CONSOLE.print_dict(info_data, title="Validation Error", subtitle=ve.message)
    return None


def parse_xml(info_file: Path) -> Optional[Metadata]:
    with info_file.open("rb") as stream:
        data = xmltodict.parse(stream, dict_constructor=dict, xml_attribs=False)["ComicInfo"]

    year = int(data["Year"]) if "Year" in data else None
    month = int(data["Month"]) if "Month" in data else 1 if year else None
    day = int(data["Day"]) if "Day" in data else 1 if month else None

    creators = {}
    roles = ["Artist", "Writer", "Penciller", "Inker", "Colourist", "Colorist", "Letterer", "CoverArtist", "Editor"]
    for role in roles:
        if role not in data:
            continue
        creator_str = data[role]
        if creator_str:
            role = "Cover Artist" if role == "CoverArtist" else role
            role = "Colourist" if role == "Colorist" else role
            creator_list = [x.strip() for x in creator_str.split(",")]
            for creator in creator_list:
                if creator in creators:
                    creators[creator]["Roles"].append(role)
                else:
                    creators[creator] = {"Name": creator, "Roles": [role]}

    if "Web" in data and data["Web"] and "comixology" in data["Web"].lower():
        identifier = [{"Service": "Comixology", "ID": None, "URL": data["Web"]}]
    else:
        identifier = []

    output = {
        "Publisher": {
            "Title": data["Publisher"] if "Publisher" in data else CONSOLE.prompt("Publisher Title"),
            "Identifiers": [],
        },
        "Series": {
            "Title": data["Series"] if "Series" in data else CONSOLE.prompt("Series Title"),
            "Volume": CONSOLE.prompt_int("Series Volume", default=1),
            "Identifiers": [],
            "Start Year": int(data["Volume"]) if "Volume" in data else None,
        },
        "Comic": {
            "Format": (FormatEnum.select() or FormatEnum.COMIC).get_title(),
            "Number": data["Number"] if "Number" in data else CONSOLE.prompt("Issue Number", default="0"),
            "Cover Date": date(year, month, day).isoformat() if year else None,
            "Creators": list(creators.values()),
            "Genres": [x.strip() for x in data["Genre"].split(",")] if "Genre" in data else [],
            "Identifiers": identifier,
            "Language ISO": data["LanguageISO"].upper() if "LanguageISO" in data else None,
            "Page Count": int(data["PageCount"]) if "PageCount" in data else None,
            "Store Date": None,
            "Summary": data["Summary"] if "Summary" in data else None,
            "Title": None,
        },
    }
    if (
        output["Comic"]["Format"] in [FormatEnum.TRADE_PAPERBACK.get_title(), FormatEnum.HARDCOVER.get_title()]
        and output["Comic"]["Number"] == "0"
    ):
        output["Comic"]["Title"] = CONSOLE.prompt("Issue Title") or None

    return Metadata.load({"Data": output, "Meta": {}})
