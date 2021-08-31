import datetime

from Organizer.comic_info import ComicInfo, PublisherInfo, SeriesInfo
from Organizer.metron_api import parse_issue_result, parse_publisher_result, parse_series_result

# TODO: Make some fixtures for the PublisherInfo, SeriesInfo, and ComicInfo


def test_parse_publisher(talker):
    test_publisher = talker.get_publisher(1)
    publisher_info = PublisherInfo("Marvel")
    results = parse_publisher_result(test_publisher, publisher_info)
    assert results.title == "Marvel"


def test_parse_series(talker):
    test_series = talker.get_series(1)
    publisher_info = PublisherInfo("Marvel")
    series_info = SeriesInfo(publisher_info, "Death of the Inhumans")
    results = parse_series_result(test_series, series_info)
    assert results.volume == 1
    assert results.start_year == 2018
    assert results.title == "Death of the Inhumans"


def test_parse_issue(talker):
    test_issue = talker.get_issue(1)
    publisher_info = PublisherInfo("Marvel")
    series_info = SeriesInfo(publisher_info, "Death of the Inhumans")
    issue_info = ComicInfo(series_info, "1")
    result = parse_issue_result(test_issue, issue_info)
    assert result.number == "1"
    assert result.title == "Chapter One: Vox"
    assert result.cover_date == datetime.date(2018, 9, 1)
    assert len(result.creators) == 5
