import logging
from typing import Optional

from Simyan import SqliteCache, api
from Simyan.issue import Issue
from Simyan.publisher import Publisher
from Simyan.story_arc import StoryArc
from Simyan.volume import Volume

from Organizer.comic_info import ComicInfo, IdentifierInfo, PublisherInfo, SeriesInfo
from Organizer.console import Console
from Organizer.utils import COMICVINE_API_KEY, remove_extra

LOGGER = logging.getLogger(__name__)


class Talker:
    def __init__(self, api_key: str, cache=None) -> None:
        if not cache:
            cache = SqliteCache()
        self.session = api(api_key=api_key, cache=cache)

    def search_publishers(self, name: str) -> Optional[int]:
        LOGGER.debug("Search Publishers")
        results = self.session.publisher_list(params={"name": name})
        if results:
            index = Console.display_menu(
                items=[f"{item.id} | {item.name}" for item in results],
                exit_text="None of the Above",
                prompt="Select Publisher",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_publisher(self, publisher_id: int) -> Publisher:
        LOGGER.debug("Getting Publisher")
        return self.session.publisher(publisher_id)

    def search_volumes(
        self, name: str, publisher_id: Optional[int] = None, start_year: Optional[int] = None
    ) -> Optional[int]:
        LOGGER.debug("Search Volumes")
        params = {"name": name}
        results = self.session.volume_list(params=params)
        if results and publisher_id:
            results = [x for x in results if x.publisher.id == publisher_id]
        if results and start_year:
            results = [x for x in results if x.start_year == start_year]
        if results:
            index = Console.display_menu(
                items=[f"{item.id} | {item.publisher.name} | {item.name} [{item.start_year}]" for item in results],
                exit_text="None of the Above",
                prompt="Select Volume",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_volume(self, volume_id: int) -> Volume:
        LOGGER.debug("Getting Volume")
        return self.session.volume(volume_id)

    def search_issues(self, volume_id: int, number: str) -> Optional[int]:
        LOGGER.debug("Search Issues")
        params = {"volume": volume_id, "number": number}
        results = self.session.issue_list(params=params)
        if results:
            index = Console.display_menu(
                items=[
                    f"{item.id} | {item.publisher.name} | {item.name} [{item.start_year}] #{item.issue_number}"
                    for item in results
                ],
                exit_text="None of the Above",
                prompt="Select Issue",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_issue(self, issue_id: int) -> Issue:
        LOGGER.debug("Getting Issue")
        return self.session.issue(issue_id)

    def search_arcs(self, name: str) -> Optional[int]:
        LOGGER.debug("Search Arcs")
        pass

    def get_arc(self, arc_id: int) -> StoryArc:
        LOGGER.debug("Getting Arc")
        return self.session.story_arc(arc_id)


def add_info(comic_info: ComicInfo) -> ComicInfo:
    talker = Talker(COMICVINE_API_KEY, SqliteCache("Comic-Organizer.sqlite"))

    if "Comicvine" in comic_info.series.publisher.identifiers.keys():
        publisher_id = comic_info.series.publisher.identifiers["Comicvine"]._id
    else:
        publisher_id = talker.search_publishers(name=comic_info.series.publisher.title)
    if not publisher_id:
        return comic_info

    comic_info.series.publisher = parse_publisher_result(
        result=talker.get_publisher(publisher_id), publisher_info=comic_info.series.publisher
    )
    if "Comicvine" in comic_info.series.identifiers.keys():
        series_id = comic_info.series.identifiers["Comicvine"]._id
    else:
        series_id = talker.search_volumes(
            publisher_id=comic_info.series.publisher.identifiers["Comicvine"]._id,
            name=comic_info.series.title,
            start_year=comic_info.series.start_year,
        )
    if not series_id:
        return comic_info

    comic_info.series = parse_volume_result(result=talker.get_volume(series_id), series_info=comic_info.series)
    if "Comicvine" in comic_info.identifiers.keys():
        issue_id = comic_info.identifiers["Comicvine"]._id
    else:
        issue_id = talker.search_issues(
            volume_id=comic_info.series.identifiers["Comicvine"]._id,
            number=comic_info.number,
        )
    if not issue_id:
        return comic_info

    return parse_issue_result(result=talker.get_issue(issue_id), comic_info=comic_info)


def parse_publisher_result(result: Publisher, publisher_info: PublisherInfo) -> PublisherInfo:
    LOGGER.debug("Parse Publisher Results")
    if "Comicvine" not in publisher_info.identifiers.keys():
        publisher_info.identifiers["Comicvine"] = IdentifierInfo(site="Comicvine", _id=result.id, url=result.site_url)
    publisher_info.title = publisher_info.title or result.name
    return publisher_info


def parse_volume_result(result: Volume, series_info: SeriesInfo) -> SeriesInfo:
    LOGGER.debug("Parse Volume Results")
    if "Comicvine" not in series_info.identifiers.keys():
        series_info.identifiers["Comicvine"] = IdentifierInfo(site="Comicvine", _id=result.id, url=result.site_url)
    series_info.title = series_info.title or result.name
    # TODO: Volume
    try:
        series_info.start_year = series_info.start_year or int(result.start_year)
    except ValueError:
        series_info.start_year = None
    return series_info


def parse_issue_result(result: Issue, comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug("Parse Issue Results")
    if "Comicvine" not in comic_info.identifiers.keys():
        comic_info.identifiers["Comicvine"] = IdentifierInfo(site="Comicvine", _id=result.id, url=result.site_url)
    comic_info.number = comic_info.number or result.number
    comic_info.title = comic_info.title or result.name
    comic_info.cover_date = comic_info.cover_date or result.cover_date
    for creator in result.creators:
        for role in creator.roles.split(","):
            if role.strip() not in comic_info.creators:
                comic_info.creators[role.strip()] = []
            comic_info.creators[role.strip()].append(creator.name)
    # TODO: Comic Format
    # TODO: Genres
    # TODO: Language ISO
    # TODO: Page Count
    comic_info.summary = comic_info.summary or remove_extra(result.summary)
    # TODO: Variant
    return comic_info
