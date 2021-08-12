import logging
from typing import List, Optional

from mokkari import api, sqlite_cache
from mokkari.arc import Arc
from mokkari.issue import Issue
from mokkari.publisher import Publisher
from mokkari.series import Series

from .comic_info import ComicInfo, IdentifierInfo
from .console import Console
from .utils import METRON_USERNAME, METRON_PASSWORD, remove_extra

LOGGER = logging.getLogger(__name__)


class Talker:
    def __init__(self, username: str, password: str, cache=None) -> None:
        if not cache:
            cache = "mokkari.sqlite"
        self.api = api(username, password, sqlite_cache.SqliteCache(cache))

    def search_publishers(self, name: str) -> Optional[int]:
        LOGGER.debug('Search Publishers')
        results = self.api.publishers_list(params={"name": name})
        if results:
            index = Console.display_menu(items=[f"{item.id} - {item.name}" for item in results], exit_text='None of the Above', prompt='Select Publisher')
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_publisher(self, publisher_id: int) -> Publisher:
        LOGGER.debug('Getting Publisher')
        return self.api.publisher(publisher_id)

    def search_series(self, publisher_id: int, name: str, volume: Optional[int] = None) -> Optional[int]:
        LOGGER.debug('Search Series')
        params = {'publisher_id': publisher_id, 'name': name}
        if volume:
            params['volume'] = volume
        results = self.api.series_list(params=params)
        if results:
            index = Console.display_menu(items=[f"{item.id} - {item.display_name}" for item in results], exit_text='None of the Above', prompt='Select Series')
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_series(self, series_id: int) -> Series:
        LOGGER.debug('Getting Series')
        return self.api.series(series_id)

    def search_issues(self, series_id: int, number: str) -> Optional[int]:
        LOGGER.debug('Search Issues')
        params = {'series_id': series_id, 'number': number}
        results = self.api.issues_list(params=params)
        if results:
            index = Console.display_menu(items=[f"{item.id} - {item.issue_name} [{item.cover_date}]" for item in results], exit_text='None of the Above', prompt='Select Issue')
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_issue(self, issue_id: int) -> Issue:
        LOGGER.debug('Getting Issue')
        return self.api.issue(issue_id)

    def search_arcs(self, name: str) -> Optional[int]:
        LOGGER.debug('Search Arcs')
        pass

    def get_arc(self, arc_id: int) -> Arc:
        LOGGER.debug('Getting Arc')
        return self.api.arc(arc_id)


def add_info(comic_info: ComicInfo) -> ComicInfo:
    talker = Talker(METRON_USERNAME, METRON_PASSWORD)

    if 'metron' in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        publisher_id = [x.identifier for x in comic_info.series.publisher.identifiers if x.website.lower() == 'metron'][0]
    else:
        publisher_id = talker.search_publishers(name=comic_info.series.publisher.title)
    if not publisher_id:
        return comic_info

    comic_info = parse_publisher_result(result=talker.get_publisher(publisher_id), comic_info=comic_info)
    if 'metron' in [x.website.lower() for x in comic_info.series.identifiers]:
        series_id = [x.identifier for x in comic_info.series.identifiers if x.website.lower() == 'metron'][0]
    else:
        series_id = talker.search_series(publisher_id=[x.identifier for x in comic_info.series.publisher.identifiers if x.website.lower() == 'metron'][0],
                                         name=comic_info.series.title,
                                         volume=comic_info.series.volume)
    if not series_id:
        return comic_info

    comic_info = parse_series_result(result=talker.get_series(series_id), comic_info=comic_info)
    if 'metron' in [x.website.lower() for x in comic_info.identifiers]:
        issue_id = [x.identifier for x in comic_info.identifiers if x.website.lower() == 'metron'][0]
    else:
        issue_id = talker.search_issues(series_id=[x.identifier for x in comic_info.series.identifiers if x.website.lower() == 'metron'][0], number=comic_info.number)
    if not issue_id:
        return comic_info

    return parse_issue_result(result=talker.get_issue(issue_id), comic_info=comic_info)


def parse_publisher_result(result: Publisher, comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Publisher Results')
    if 'metron' not in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        comic_info.series.publisher.identifiers.append(IdentifierInfo(website='Metron', identifier=result.id))
    comic_info.series.publisher.title = comic_info.series.publisher.title or result.name

    return comic_info


def parse_series_result(result: Series, comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Series Results')
    if 'metron' not in [x.website.lower() for x in comic_info.series.identifiers]:
        comic_info.series.identifiers.append(IdentifierInfo(website='Metron', identifier=result.id))
    comic_info.series.title = comic_info.series.title or result.name
    comic_info.series.volume = comic_info.series.volume or result.volume
    comic_info.series.start_year = comic_info.series.start_year or result.year_began

    return comic_info


def titles_to_string(titles: List[str]) -> str:
    return "; ".join(map(str, titles))


def parse_issue_result(result: Issue, comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Comic Results')
    if 'metron' not in [x.website.lower() for x in comic_info.identifiers]:
        comic_info.identifiers.append(IdentifierInfo(website='Metron', identifier=result.id))
    comic_info.number = comic_info.number or result.number
    comic_info.title = comic_info.title or (
        titles_to_string(result.story_titles) if result.story_titles else None
    )

    comic_info.cover_date = comic_info.cover_date or result.cover_date

    for credit in result.credits:
        for role in credit.role:
            if role.name not in comic_info.creators:
                comic_info.creators[role.name] = []
            comic_info.creators[role.name].append(credit.creator)
    # TODO: Comic Format
    # TODO: Genres
    # TODO: Language ISO
    # TODO: Page Count
    comic_info.summary = comic_info.summary or remove_extra(result.desc)
    # TODO: Variant
    return comic_info
