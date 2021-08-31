import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from ruamel.yaml import YAML

from .comic_format import ComicFormat
from .comic_genre import ComicGenre
from .utils import remove_extra, str_to_list

LOGGER = logging.getLogger(__name__)


class IdentifierInfo:
    def __init__(self, website: str, identifier: Optional[str] = None, url: Optional[str] = None):
        self.website = website
        self.identifier = identifier
        self.url = url

    def __hash__(self):
        return hash(self.website)

    def __lt__(self, other):
        return self.website < other.website


class PublisherInfo:
    def __init__(self, title: str):
        self.title = title
        self.identifiers = []

    def to_output(self) -> Dict[str, Any]:
        return {
            "Title": self.title,
            "Identifiers": {
                x.website: {"Id": str(x.identifier), "Url": x.url}
                for x in sorted(list(dict.fromkeys(self.identifiers)))
            },
        }

    def reset(self):
        self.identifiers = []


class SeriesInfo:
    def __init__(
        self, publisher: PublisherInfo, title: str, start_year: Optional[int] = None, volume: Optional[int] = None
    ):
        self.publisher = publisher
        self.start_year = start_year
        self.title = title
        self.volume = volume
        self.identifiers = []

    def to_output(self) -> Dict[str, Any]:
        return {
            "Publisher": self.publisher.to_output(),
            "Start Year": self.start_year,
            "Title": self.title,
            "Volume": self.volume,
            "Identifiers": {
                x.website: {"Id": str(x.identifier), "Url": x.url}
                for x in sorted(list(dict.fromkeys(self.identifiers)))
            },
        }

    def reset(self):
        self.publisher.reset()
        self.start_year = None
        self.volume = None
        self.identifiers = []


class ArcInfo:
    def __init__(self):
        pass


class ComicInfo:
    def __init__(
        self,
        series: SeriesInfo,
        number: str,
        title: Optional[str] = None,
        variant: Optional[str] = None,
        summary: Optional[str] = None,
        cover_date: Optional[date] = None,
        language_iso: str = "EN",
        comic_format: str = "Comic",
        genres: List[str] = None,
        page_count: int = 1,
        creators: Dict[str, List[str]] = None,
        notes: str = None,
    ):
        self.series = series
        self.number = number
        self.title = title
        self.cover_date = cover_date
        self.creators = creators or {}
        self.comic_format = comic_format
        self.genres = genres or []
        self.language_iso = language_iso
        self.page_count = page_count
        self.summary = summary
        self.variant = variant
        self.identifiers = []
        self.notes = notes

    def to_output(self) -> Dict[str, Any]:
        return {
            "Series": self.series.to_output(),
            "Issue": {"Number": self.number, "Title": self.title},
            "Cover Date": self.cover_date.strftime("%Y-%m-%d") if self.cover_date else None,
            "Creators": {key: sorted(list(dict.fromkeys(values))) for key, values in self.creators.items()},
            "Format": self.comic_format,
            "Genres": sorted(list(dict.fromkeys(self.genres))),
            "Language ISO": self.language_iso,
            "Page Count": self.page_count,
            "Summary": self.summary,
            "Variant": self.variant,
            "Identifiers": {
                x.website: {"Id": str(x.identifier), "Url": x.url}
                for x in sorted(list(dict.fromkeys(self.identifiers)))
            },
            "Notes": self.notes,
        }

    def reset(self):
        self.series.reset()
        self.title = None
        self.variant = None
        self.summary = None
        self.cover_date = None
        self.language_iso = "EN"
        self.comic_format = "Comic"
        self.genres = []
        self.page_count = 1
        self.creators = {}
        self.identifiers = []
        self.notes = None


def load_info(file: Path) -> Optional[ComicInfo]:
    if file.suffix == ".xml":
        return load_xml_info(file)
    if file.suffix == ".json":
        return load_json_info(file)
    if file.suffix == ".yaml":
        return load_yaml_info(file)
    return None


def load_json_info(file: Path) -> Optional[ComicInfo]:
    with open(file, "r", encoding="UTF-8") as json_info:
        info = json.load(json_info)
        LOGGER.debug(f"Loaded {file.stem}")

        publisher = PublisherInfo(
            title=info["Series"]["Publisher"]["Title"]
            if "Series" in info and "Publisher" in info["Series"] and "Title" in info["Series"]["Publisher"]
            else ""
        )
        # region Identifiers
        if "Series" in info and "Publisher" in info["Series"] and "Identifiers" in info["Series"]["Publisher"]:
            for website, details in info["Series"]["Publisher"]["Identifiers"].items():
                publisher.identifiers.append(
                    IdentifierInfo(website=website, identifier=details["Id"], url=details["Url"])
                )
        # endregion
        series = SeriesInfo(
            publisher=publisher,
            start_year=info["Series"]["Start Year"] if "Series" in info and "Start Year" in info["Series"] else None,
            title=info["Series"]["Title"] if "Series" in info and "Title" in info["Series"] else "",
            volume=info["Series"]["Volume"] if "Series" in info and "Volume" in info["Series"] else None,
        )
        # region Identifiers
        if "Series" in info and "Identifiers" in info["Series"]:
            for website, details in info["Series"]["Identifiers"].items():
                series.identifiers.append(IdentifierInfo(website=website, identifier=details["Id"], url=details["Url"]))
        # endregion
        comic_info = ComicInfo(
            series=series,
            number=info["Issue"]["Number"] if "Issue" in info and "Number" in info["Issue"] else "",
            title=info["Issue"]["Title"] if "Issue" in info and "Title" in info["Issue"] else None,
            creators=info["Creators"] if "Creators" in info else {},
            cover_date=datetime.strptime(info["Cover Date"], "%Y-%m-%d").date() if "Cover Date" in info else None,
            comic_format=ComicFormat.from_string(info["Format"]).get_title() if "Format" in info else "Comic",
            genres=[x.get_title() for x in [ComicGenre.from_string(x) for x in info["Genres"]] if x]
            if "Genres" in info
            else [],
            language_iso=info["Language ISO"] if "Language ISO" in info else "EN",
            page_count=info["Page Count"] if "Page Count" in info else 1,
            summary=info["Summary"] if "Summary" in info else None,
            variant=info["Variant"] if "Variant" in info else None,
            notes=info["Notes"] if "Notes" in info else None,
        )
        # region Identifiers
        if "Identifiers" in info:
            for website, details in info["Identifiers"].items():
                comic_info.identifiers.append(
                    IdentifierInfo(website=website, identifier=details["Id"], url=details["Url"])
                )
        # endregion
        return comic_info


def load_xml_info(file: Path) -> Optional[ComicInfo]:
    with open(file, "r", encoding="UTF-8") as xml_info:
        soup = BeautifulSoup(xml_info, "xml")
        info = soup.find("ComicInfo")
        LOGGER.debug(f"Loaded {file.stem}")

        publisher = PublisherInfo(title=info.find("Publisher").string if info.find("Publisher") else "")
        series = SeriesInfo(
            publisher=publisher,
            title=info.find("Series").string if info.find("Series") else "",
            start_year=int(info.find("Volume").string) if info.find("Volume") else None,
        )
        # region Cover-Date
        year = int(info.find("Year").string) if info.find("Year") else None
        month = int(info.find("Month").string) if info.find("Month") else 1 if year else None
        day = int(info.find("Day").string) if info.find("Day") else 1 if month else None
        # endregion
        # region Creators
        creators = {}
        roles = ["Artist", "Writer", "Penciller", "Inker", "Colourist", "Colorist", "Letterer", "CoverArtist", "Editor"]
        for role in roles:
            creator_list = str_to_list(info, role)
            if creator_list:
                creators[role] = creator_list
        # endregion
        comic_info = ComicInfo(
            series=series,
            number=info.find("Number").string if info.find("Number") else "",
            # Title
            creators=creators,
            cover_date=date(year, month, day) if year else None,
            # Format
            genres=[x.get_title() for x in [ComicGenre.from_string(x) for x in str_to_list(info, "Genre")] if x],
            language_iso=info.find("LanguageISO").string.upper() if info.find("LanguageISO") else None,
            page_count=int(info.find("PageCount").string) if info.find("PageCount") else 0,
            summary=remove_extra(info.find("Summary").string) if info.find("Summary") else None,
            # Variant
            # notes=remove_extra(info.find('Notes').string) if info.find('Notes') else None
            notes=None,
        )
        # region Identifiers
        if info.find("Web") and "comixology" in info.find("Web").string.lower():
            comic_info.identifiers.append(IdentifierInfo(website="Comixology", url=info.find("Web").string))
        # endregion
        return comic_info


def load_yaml_info(file: Path) -> Optional[ComicInfo]:
    with open(file, "r", encoding="UTF-8") as yaml_info:
        info = yaml_setup().load(yaml_info)["Comic Info"]
        LOGGER.debug(f"Loaded {file.stem}")

        publisher = PublisherInfo(title=info["Series"]["Publisher"]["Title"])
        # region Identifiers
        for website, details in info["Series"]["Publisher"]["Identifiers"].items():
            publisher.identifiers.append(IdentifierInfo(website=website, identifier=details["Id"], url=details["Url"]))
        # endregion
        series = SeriesInfo(
            publisher=publisher,
            start_year=info["Series"]["Start Year"],
            title=info["Series"]["Title"],
            volume=info["Series"]["Volume"],
        )
        # region Identifiers
        for website, details in info["Series"]["Identifiers"].items():
            series.identifiers.append(IdentifierInfo(website=website, identifier=details["Id"], url=details["Url"]))
        # endregion
        comic_info = ComicInfo(
            series=series,
            number=info["Issue"]["Number"],
            title=info["Issue"]["Title"],
            creators=info["Creators"],
            cover_date=datetime.strptime(info["Cover Date"], "%Y-%m-%d").date(),
            comic_format=ComicFormat.from_string(info["Format"]).get_title(),
            genres=[x.get_title() for x in [ComicGenre.from_string(x) for x in info["Genres"]] if x],
            language_iso=info["Language ISO"],
            page_count=info["Page Count"],
            summary=info["Summary"],
            variant=info["Variant"],
            notes=info["Notes"],
        )
        # region Identifiers
        for website, details in info["Identifiers"].items():
            comic_info.identifiers.append(IdentifierInfo(website=website, identifier=details["Id"], url=details["Url"]))
        # endregion
        return comic_info


def yaml_setup() -> YAML:
    def null_representer(self, data):
        return self.represent_scalar("tag:yaml.org,2002:null", "~")

    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.width = 2147483647
    yaml.representer.add_representer(type(None), null_representer)
    # yaml.emitter.alt_null = '~'
    yaml.version = (1, 2)
    return yaml


def save_info(file: Path, comic_info: ComicInfo):
    with open(file, "w", encoding="UTF-8") as json_info:
        json.dump(comic_info.to_output(), json_info, default=str, indent=2, ensure_ascii=False)
