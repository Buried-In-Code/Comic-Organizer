import logging

from Simyan import SqliteCache
from Simyan.issue import Issue
from Simyan.publisher import Publisher
from Simyan.volume import Volume

from Organizer import ComicInfo, PublisherInfo, SeriesInfo, Settings
from Organizer.comic_info import IdentifierInfo
from Organizer.comicvine_api import Talker
from Organizer.utils import remove_extra

LOGGER = logging.getLogger(__name__)


def add_info(settings: Settings, comic_info: ComicInfo) -> ComicInfo:
    talker = Talker(settings.comicvine_api_key, SqliteCache("Comic-Organizer.sqlite"))

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
    try:
        series_info.start_year = series_info.start_year or int(result.start_year)
    except ValueError:
        series_info.start_year = None
    # TODO: Volume
    return series_info


def parse_issue_result(result: Issue, comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug("Parse Issue Results")
    if "Comicvine" not in comic_info.identifiers.keys():
        comic_info.identifiers["Comicvine"] = IdentifierInfo(site="Comicvine", _id=result.id, url=result.site_url)
    comic_info.number = comic_info.number or result.number
    comic_info.title = comic_info.title or result.name
    comic_info.cover_date = comic_info.cover_date or result.cover_date
    # TODO: Comic Format
    # TODO: Language ISO
    # TODO: Page Count
    comic_info.store_date = comic_info.store_date or result.store_date
    comic_info.summary = comic_info.summary or remove_extra(result.summary)
    # TODO: Variant
    return comic_info
