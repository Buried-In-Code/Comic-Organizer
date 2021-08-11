import datetime

from Organizer.comic_info import ComicInfo, PublisherInfo, SeriesInfo
from Organizer.metron_api import parse_issue_result, parse_publisher_result, parse_series_result

# TODO: Make some fixtures for the PublisherInfo, SeriesInfo, and ComicInfo

def test_parse_publisher(talker):
    marvel = talker.get_publisher(1)
    pub_info = PublisherInfo("Marvel")
    ser_info = SeriesInfo(pub_info, "Death of the Inhumans")
    ci = ComicInfo(ser_info, "1")
    results = parse_publisher_result(marvel, ci)
    assert results.series.publisher.title == "Marvel"


def test_parse_series(talker):
    inhumans = talker.get_series(1)
    pub_info = PublisherInfo("Marvel")
    ser_info = SeriesInfo(pub_info, "Death of the Inhumans")
    ci = ComicInfo(ser_info, "1")
    results = parse_series_result(inhumans, ci)
    assert results.series.volume == 1
    assert results.series.start_year == 2018
    assert results.series.title == "Death of the Inhumans"


def test_parse_issue(talker):
    test_issue = talker.get_issue(1)
    pub_info = PublisherInfo("Marvel")
    ser_info = SeriesInfo(pub_info, "Death of the Inhumans")
    ci = ComicInfo(ser_info, "1")
    result = parse_issue_result(test_issue, ci)
    assert result.number == "1"
    assert result.title == "Chapter One: Vox"
    assert result.cover_date == datetime.date(2018, 9, 1)
    assert len(result.creators) == 5
