import logging
from typing import List

from mokkari.issue import Issue
from mokkari.publisher import Publisher
from mokkari.series import Series
from Simyan import SqliteCache

from Organizer import ComicInfo, PublisherInfo, SeriesInfo, Settings
from Organizer.comic_info import IdentifierInfo
from Organizer.metron_api import Talker
from Organizer.utils import remove_extra

LOGGER = logging.getLogger(__name__)


def add_info(settings: Settings, comic_info: ComicInfo) -> ComicInfo:
    talker = Talker(settings.metron_username, settings.metron_password, SqliteCache("Comic-Organizer.sqlite"))

    if "Metron" in comic_info.series.publisher.identifiers.keys():
        publisher_id = comic_info.series.publisher.identifiers["Metron"]._id
    else:
        publisher_id = talker.search_publishers(name=comic_info.series.publisher.title)
    if not publisher_id:
        return comic_info

    comic_info.series.publisher = parse_publisher_result(
        result=talker.get_publisher(publisher_id), publisher_info=comic_info.series.publisher
    )
    if "Metron" in comic_info.series.identifiers.keys():
        series_id = comic_info.series.identifiers["Metron"]._id
    else:
        series_id = talker.search_series(
            publisher_id=comic_info.series.publisher.identifiers["Metron"]._id,
            name=comic_info.series.title,
            volume=comic_info.series.volume,
        )
    if not series_id:
        return comic_info

    comic_info.series = parse_series_result(result=talker.get_series(series_id), series_info=comic_info.series)
    if "Metron" in comic_info.identifiers.keys():
        issue_id = comic_info.identifiers["Metron"]._id
    else:
        issue_id = talker.search_issues(
            series_id=comic_info.series.identifiers["Metron"]._id,
            number=comic_info.number,
        )
    if not issue_id:
        return comic_info

    return parse_issue_result(result=talker.get_issue(issue_id), comic_info=comic_info)


def parse_publisher_result(result: Publisher, publisher_info: PublisherInfo) -> PublisherInfo:
    LOGGER.debug("Parse Publisher Results")
    if "Metron" not in publisher_info.identifiers.keys():
        publisher_info.identifiers["Metron"] = IdentifierInfo(site="Metron", _id=result.id)
    publisher_info.title = publisher_info.title or result.name

    return publisher_info


def parse_series_result(result: Series, series_info: SeriesInfo) -> SeriesInfo:
    LOGGER.debug("Parse Series Results")
    if "Metron" not in series_info.identifiers.keys():
        series_info.identifiers["Metron"] = IdentifierInfo(site="Metron", _id=result.id)
    series_info.title = series_info.title or result.name
    series_info.start_year = series_info.start_year or result.year_began
    series_info.volume = series_info.volume or result.volume

    return series_info


def titles_to_string(titles: List[str]) -> str:
    return "; ".join(map(str, titles))


def parse_issue_result(result: Issue, comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug("Parse Comic Results")
    if "Metron" not in comic_info.identifiers.keys():
        comic_info.identifiers["Metron"] = IdentifierInfo(site="Metron", _id=result.id)
    comic_info.number = comic_info.number or result.number
    comic_info.title = comic_info.title or (titles_to_string(result.story_titles) if result.story_titles else None)
    comic_info.cover_date = comic_info.cover_date or result.cover_date
    # TODO: Comic Format
    # TODO: Language ISO
    # TODO: Page Count
    comic_info.store_date = comic_info.store_date or result.store_date
    comic_info.summary = comic_info.summary or remove_extra(result.desc)
    # TODO: Variant

    return comic_info
