from datetime import date

from DexStarr import ComicInfo, PublisherInfo, SeriesInfo
from DexStarr.metron_api import parse_issue_result, parse_publisher_result, parse_series_result

PUBLISHER_ID = 2
PUBLISHER_TITLE = "DC Comics"
SERIES_ID = 1119
SERIES_TITLE = "Green Lantern"
SERIES_START_YEAR = 2005
SERIES_VOLUME = 4
ISSUE_ID = 9778
ISSUE_NUMBER = "1"


def test_parse_publisher(metron):
    test_publisher = metron.get_publisher(PUBLISHER_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    result = parse_publisher_result(test_publisher, publisher_info)
    # Publisher
    assert "Metron" in result.identifiers.keys()
    assert result.identifiers["Metron"]._id == PUBLISHER_ID
    assert result.title == PUBLISHER_TITLE


def test_parse_series(metron):
    test_series = metron.get_series(SERIES_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    series_info = SeriesInfo(publisher_info, SERIES_TITLE)
    result = parse_series_result(test_series, series_info)
    # Series
    assert "Metron" in result.identifiers.keys()
    assert result.identifiers["Metron"]._id == SERIES_ID
    assert result.title == SERIES_TITLE
    assert result.start_year == SERIES_START_YEAR
    assert result.volume == SERIES_VOLUME


def test_parse_issue(metron):
    test_issue = metron.get_issue(ISSUE_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    series_info = SeriesInfo(publisher_info, SERIES_TITLE)
    issue_info = ComicInfo(series_info, ISSUE_NUMBER)
    result = parse_issue_result(test_issue, issue_info)
    # Issue
    assert "Metron" in result.identifiers.keys()
    assert result.identifiers["Metron"]._id == ISSUE_ID
    assert result.number == ISSUE_NUMBER
    assert result.title == "Airborne"
    assert result.cover_date == date(year=2005, month=7, day=1)
    assert result.store_date == date(year=2005, month=5, day=25)
