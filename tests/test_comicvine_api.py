from datetime import date

from Organizer import ComicInfo, PublisherInfo, SeriesInfo
from Organizer.external.comicvine_api import parse_issue_result, parse_publisher_result, parse_volume_result

PUBLISHER_ID = 10
PUBLISHER_TITLE = "DC Comics"
VOLUME_ID = 18216
VOLUME_TITLE = "Green Lantern"
ISSUE_ID = 111265
ISSUE_NUMBER = "1"


def test_parse_publisher(comicvine):
    test_publisher = comicvine.get_publisher(PUBLISHER_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    result = parse_publisher_result(test_publisher, publisher_info)
    assert "Comicvine" in result.identifiers.keys()
    assert result.identifiers["Comicvine"]._id == PUBLISHER_ID
    assert result.title == PUBLISHER_TITLE


def test_parse_series(comicvine):
    test_volume = comicvine.get_volume(VOLUME_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    volume_info = SeriesInfo(publisher_info, VOLUME_TITLE)
    result = parse_volume_result(test_volume, volume_info)
    assert "Comicvine" in result.identifiers.keys()
    assert result.identifiers["Comicvine"]._id == VOLUME_ID
    assert result.title == VOLUME_TITLE
    assert result.start_year == 2005


def test_parse_issue(comicvine):
    test_issue = comicvine.get_issue(ISSUE_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    volume_info = SeriesInfo(publisher_info, VOLUME_TITLE)
    issue_info = ComicInfo(volume_info, ISSUE_NUMBER)
    result = parse_issue_result(test_issue, issue_info)
    assert "Comicvine" in result.identifiers.keys()
    assert result.identifiers["Comicvine"]._id == ISSUE_ID
    assert result.number == ISSUE_NUMBER
    assert result.title == "Airborne"
    assert result.cover_date == date(year=2005, month=7, day=1)
