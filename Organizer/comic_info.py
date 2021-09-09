import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup
from ruamel.yaml import YAML

from Organizer.comic_format import ComicFormat
from Organizer.utils import remove_extra, to_titlecase

LOGGER = logging.getLogger(__name__)


class IdentifierInfo:
    def __init__(self, site: str, _id: Optional[Union[str, int]] = None, url: Optional[str] = None):
        self.site = site
        self._id = _id
        self.url = url

    def __hash__(self):
        return hash(self.site)

    def __lt__(self, other):
        return self.site < other.site


class PublisherInfo:
    def __init__(self, title: str):
        self.title = title
        self.identifiers = {}

    def to_output(self) -> Dict[str, Any]:
        return {
            "Title": self.title,
            "Identifiers": {site: {"Id": str(x._id), "Url": x.url} for site, x in sorted(self.identifiers.items())},
        }

    def reset(self):
        self.identifiers = {}


class SeriesInfo:
    def __init__(
        self, publisher: PublisherInfo, title: str, start_year: Optional[int] = None, volume: Optional[int] = None
    ):
        self.publisher = publisher
        self.title = title
        self.start_year = start_year
        self.volume = volume
        self.identifiers = {}

    def to_output(self) -> Dict[str, Any]:
        return {
            "Publisher": self.publisher.to_output(),
            "Title": self.title,
            "Start Year": self.start_year,
            "Volume": self.volume,
            "Identifiers": {site: {"Id": str(x._id), "Url": x.url} for site, x in sorted(self.identifiers.items())},
        }

    def reset(self):
        self.publisher.reset()
        self.start_year = None
        self.volume = None
        self.identifiers = {}


class ArcInfo:
    def __init__(self):
        pass


class ComicInfo:
    def __init__(
        self,
        series: SeriesInfo,
        number: str,
        title: Optional[str] = None,
        cover_date: Optional[date] = None,
        comic_format: ComicFormat = ComicFormat.COMIC,
        language_iso: str = "EN",
        page_count: int = 0,
        store_date: Optional[date] = None,
        summary: Optional[str] = None,
        variant: bool = False,
        notes: str = None,
    ):
        self.series = series
        self.number = number
        self.title = title
        self.cover_date = cover_date
        self.comic_format = comic_format
        self.language_iso = language_iso
        self.page_count = page_count
        self.store_date = store_date
        self.summary = summary
        self.variant = variant
        self.identifiers = {}
        self.notes = notes

    def to_output(self) -> Dict[str, Any]:
        return {
            "Series": self.series.to_output(),
            "Issue": {"Number": self.number, "Title": self.title},
            "Cover Date": self.cover_date.strftime("%Y-%m-%d") if self.cover_date else None,
            "Format": self.comic_format.get_title(),
            "Language ISO": self.language_iso,
            "Page Count": self.page_count,
            "Store Date": self.store_date.strftime("%Y-%m-%d") if self.store_date else None,
            "Summary": self.summary,
            "Variant": self.variant,
            "Identifiers": {site: {"Id": str(x._id), "Url": x.url} for site, x in sorted(self.identifiers.items())},
            "Notes": self.notes,
        }

    def reset(self):
        self.series.reset()
        self.title = None
        self.cover_date = None
        self.comic_format = ComicFormat.COMIC
        self.language_iso = "EN"
        self.page_count = 0
        self.store_date = None
        self.summary = None
        self.variant = False
        self.identifiers = {}
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
            for site, details in info["Series"]["Publisher"]["Identifiers"].items():
                publisher.identifiers[to_titlecase(site)] = IdentifierInfo(
                    site=to_titlecase(site), _id=details["Id"], url=details["Url"]
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
            for site, details in info["Series"]["Identifiers"].items():
                series.identifiers[to_titlecase(site)] = IdentifierInfo(
                    site=to_titlecase(site), _id=details["Id"], url=details["Url"]
                )
        # endregion
        comic_info = ComicInfo(
            series=series,
            number=info["Issue"]["Number"] if "Issue" in info and "Number" in info["Issue"] else "1",
            title=info["Issue"]["Title"] if "Issue" in info and "Title" in info["Issue"] else None,
            cover_date=datetime.strptime(info["Cover Date"], "%Y-%m-%d").date() if "Cover Date" in info else None,
            comic_format=ComicFormat.from_string(info["Format"]) if "Format" in info else ComicFormat.COMIC,
            language_iso=info["Language ISO"] if "Language ISO" in info else "EN",
            page_count=info["Page Count"] if "Page Count" in info else 1,
            store_date=datetime.strptime(info["Store Date"], "%Y-%m-%d").date() if "Store Date" in info else None,
            summary=info["Summary"] if "Summary" in info else None,
            variant=info["Variant"] if "Variant" in info else False,
            notes=info["Notes"] if "Notes" in info else None,
        )
        # region Identifiers
        if "Identifiers" in info:
            for site, details in info["Identifiers"].items():
                comic_info.identifiers[to_titlecase(site)] = IdentifierInfo(
                    site=to_titlecase(site), _id=details["Id"], url=details["Url"]
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
            # TODO: Volume
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
            # TODO: Title
            cover_date=date(year, month, day) if year else None,
            # TODO: Format
            language_iso=info.find("LanguageISO").string.upper() if info.find("LanguageISO") else None,
            page_count=int(info.find("PageCount").string) if info.find("PageCount") else 0,
            # TODO: Store Date
            summary=remove_extra(info.find("Summary").string) if info.find("Summary") else None,
            # TODO: Variant
            notes=None,
        )
        # region Identifiers
        if info.find("Web") and "comixology" in info.find("Web").string.lower():
            comic_info.identifiers["Comixology"] = IdentifierInfo(site="Comixology", url=info.find("Web").string)
        # endregion
        return comic_info


def load_yaml_info(file: Path) -> Optional[ComicInfo]:
    with open(file, "r", encoding="UTF-8") as yaml_info:
        info = yaml_setup().load(yaml_info)["Comic Info"]
        LOGGER.debug(f"Loaded {file.stem}")

        publisher = PublisherInfo(
            title=info["Series"]["Publisher"]["Title"]
            if "Series" in info and "Publisher" in info["Series"] and "Title" in info["Series"]["Publisher"]
            else ""
        )
        # region Identifiers
        if "Series" in info and "Publisher" in info["Series"] and "Identifiers" in info["Series"]["Publisher"]:
            for site, details in info["Series"]["Publisher"]["Identifiers"].items():
                publisher.identifiers[to_titlecase(site)] = IdentifierInfo(
                    site=to_titlecase(site), _id=details["Id"], url=details["Url"]
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
            for site, details in info["Series"]["Identifiers"].items():
                series.identifiers[to_titlecase(site)] = IdentifierInfo(
                    site=to_titlecase(site), _id=details["Id"], url=details["Url"]
                )
        # endregion
        comic_info = ComicInfo(
            series=series,
            number=info["Issue"]["Number"] if "Issue" in info and "Number" in info["Issue"] else "1",
            title=info["Issue"]["Title"] if "Issue" in info and "Title" in info["Issue"] else None,
            cover_date=datetime.strptime(info["Cover Date"], "%Y-%m-%d").date() if "Cover Date" in info else None,
            comic_format=ComicFormat.from_string(info["Format"]) if "Format" in info else ComicFormat.COMIC,
            language_iso=info["Language ISO"] if "Language ISO" in info else "EN",
            page_count=info["Page Count"] if "Page Count" in info else 1,
            store_date=datetime.strptime(info["Store Date"], "%Y-%m-%d").date() if "Store Date" in info else None,
            summary=info["Summary"] if "Summary" in info else None,
            variant=info["Variant"] if "Variant" in info else False,
            notes=info["Notes"] if "Notes" in info else None,
        )
        # region Identifiers
        if "Identifiers" in info:
            for site, details in info["Identifiers"].items():
                comic_info.identifiers[to_titlecase(site)] = IdentifierInfo(
                    site=to_titlecase(site), _id=details["Id"], url=details["Url"]
                )
        # endregion
        return comic_info


def str_to_list(soup, key: str) -> List[str]:
    return [x.strip() for x in (str(soup.find(key).string) if soup.find(key) else "").split(",") if x]


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
