import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from Simyan import SqliteCache

from Organizer.comic_format import ComicFormat
from Organizer.comic_info import ComicInfo, IdentifierInfo
from Organizer.console import Console
from Organizer.league_of_comic_geeks_api.session import Session
from Organizer.utils import LEAGUE_API_KEY, LEAGUE_CLIENT_ID, remove_extra

LOGGER = logging.getLogger(__name__)
MINUTE = 60


class Talker:
    def __init__(self, api_key: str, client_id: str, cache=None) -> None:
        if not cache:
            cache = SqliteCache()
        self.session = Session(api_key=api_key, client_id=client_id, cache=cache)

    def get_series(self, volume_id: int) -> Dict[str, Any]:
        LOGGER.debug("Getting Series")
        return self.session.series(volume_id)

    def search_comics(self, search_terms: Tuple[str, str], comic_format: str, show_variants: bool) -> Optional[int]:
        LOGGER.debug("Search Comics")

        results_1 = self.session.comic_list(search_terms[0])
        results_2 = []
        if search_terms[0] != search_terms[1]:
            results_2 = self.session.comic_list(search_terms[0])

        results = results_1 + results_2
        if not results:
            return None
        results = filter(lambda x: x["format"] == comic_format, results)
        results = sorted(
            results if show_variants else filter(lambda x: x["variant"] == "0", results),
            key=lambda x: (x["publisher_name"], x["series_name"], x["series_volume"], x["title"]),
        )
        if len(results) >= 1:
            index = Console.display_menu(
                items=[
                    f"{item['id']} | [{item['publisher_name']}] {item['series_name']} v{item['series_volume']} - "
                    f"{item['title']} - {item['format']}"
                    for item in results
                ],
                exit_text="None of the Above",
                prompt="Select Comic",
            )
            if 1 <= index <= len(results):
                return results[index - 1]["id"]
        return None

    def get_comic(self, comic_id: int) -> Dict[str, Any]:
        LOGGER.debug("Getting Comic")
        return self.session.comic(comic_id)


def add_info(comic_info: ComicInfo, show_variants: bool = False) -> ComicInfo:
    talker = Talker(LEAGUE_API_KEY, LEAGUE_CLIENT_ID, SqliteCache("Comic-Organizer.sqlite"))

    if "League of Comic Geeks" in comic_info.identifiers.keys():
        comic_id = comic_info.identifiers["League of Comic Geeks"]._id
    else:
        comic_id = talker.search_comics(
            search_terms=__calculate_search_terms(
                series_title=comic_info.series.title, comic_format=comic_info.comic_format, number=comic_info.number
            ),
            comic_format=comic_info.comic_format,
            show_variants=show_variants,
        )
    if not comic_id:
        return comic_info

    return parse_comic_result(result=talker.get_comic(comic_id=comic_id), comic_info=comic_info)


def parse_comic_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug("Parse Comic Results")
    # region Publisher
    if "League of Comic Geeks" not in comic_info.series.publisher.identifiers.keys():
        comic_info.series.publisher.identifiers["League of Comic Geeks"] = IdentifierInfo(
            site="League of Comic Geeks", _id=int(result["details"]["publisher_id"])
        )
    comic_info.series.publisher.title = comic_info.series.publisher.title or result["series"]["publisher_name"]
    # endregion
    # region Series
    if "League of Comic Geeks" not in comic_info.series.identifiers.keys():
        comic_info.series.identifiers["League of Comic Geeks"] = IdentifierInfo(
            site="League of Comic Geeks", _id=int(result["details"]["series_id"])
        )
    comic_info.series.title = comic_info.series.title or result["series"]["title"]
    comic_info.series.volume = comic_info.series.volume or int(result["series"]["volume"])
    comic_info.series.start_year = comic_info.series.start_year or int(result["series"]["year_begin"])
    # endregion
    # region Comic
    if "League of Comic Geeks" not in comic_info.identifiers.keys():
        comic_info.identifiers["League of Comic Geeks"] = IdentifierInfo(
            site="League of Comic Geeks", _id=int(result["details"]["id"])
        )
    # TODO: Number
    # TODO: Title
    comic_info.cover_date = (
        comic_info.cover_date or datetime.strptime(result["details"]["date_release"], "%Y-%m-%d").date()
    )
    for creator in result["creators"]:
        for role in creator["role"].split(","):
            if role.strip() not in comic_info.creators:
                comic_info.creators[role.strip()] = []
            comic_info.creators[role.strip()].append(creator["name"])
    comic_info.comic_format = (
        comic_info.comic_format or ComicFormat.from_string(result["details"]["format"]).get_title()
    )
    # TODO: Genres
    # TODO: Language ISO
    comic_info.page_count = comic_info.page_count or int(result["details"]["pages"])
    comic_info.summary = comic_info.summary or remove_extra(result["details"]["description"])
    # TODO: Variant
    # endregion
    return comic_info


def __calculate_search_terms(series_title: str, comic_format: str, number: Optional[str] = None) -> Tuple[str, str]:
    if number and number != "1":
        item_1 = f"{series_title} #{number}"
    else:
        item_1 = series_title
    if number and number != "1":
        if comic_format == ComicFormat.TRADE_PAPERBACK.get_title():
            item_2 = f"{series_title} Vol. {number} TP"
        elif comic_format == ComicFormat.HARDCOVER.get_title():
            item_2 = f"{series_title} Vol. {number} HC"
        elif comic_format == ComicFormat.ANNUAL.get_title():
            item_2 = f"{series_title} Annual #{number}"
        elif comic_format == ComicFormat.DIGITAL_CHAPTER.get_title():
            item_2 = f"{series_title} Chapter #{number}"
        else:
            item_2 = f"{series_title} #{number}"
    else:
        item_2 = series_title
    return item_1, item_2
