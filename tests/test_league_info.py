from datetime import date

from DexStarr import ComicInfo, PublisherInfo, SeriesInfo
from DexStarr.comic_format import ComicFormat
from DexStarr.league_of_comic_geeks_api import parse_comic_result, parse_series_result

PUBLISHER_ID = 1
PUBLISHER_TITLE = "DC Comics"
SERIES_ID = 110787
SERIES_TITLE = "Green Lantern"
SERIES_START_YEAR = 2005
SERIES_VOLUME = 4
COMIC_ID = 4579722
COMIC_NUMBER = "1"


def test_parse_series(league):
    test_series = league.get_series(SERIES_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    series_info = SeriesInfo(publisher_info, SERIES_TITLE)
    result = parse_series_result(test_series, series_info)
    # Series
    assert "League of Comic Geeks" in result.identifiers.keys()
    assert result.identifiers["League of Comic Geeks"]._id == SERIES_ID
    assert result.title == SERIES_TITLE
    assert result.start_year == SERIES_START_YEAR
    assert result.volume == SERIES_VOLUME
    # Publisher
    assert "League of Comic Geeks" in result.publisher.identifiers.keys()
    assert result.publisher.identifiers["League of Comic Geeks"]._id == PUBLISHER_ID
    assert result.publisher.title == PUBLISHER_TITLE


def test_parse_comic(league):
    test_comic = league.get_comic(COMIC_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    series_info = SeriesInfo(publisher_info, SERIES_TITLE)
    comic_info = ComicInfo(series_info, COMIC_NUMBER)
    result = parse_comic_result(test_comic, comic_info)
    # Comic
    assert "League of Comic Geeks" in result.identifiers.keys()
    assert result.identifiers["League of Comic Geeks"]._id == COMIC_ID
    assert result.title == "Green Lantern #1"
    assert result.comic_format == ComicFormat.COMIC
    assert result.page_count == 40
    assert result.store_date == date(year=2005, month=5, day=18)
    assert result.variant is False
    # Series
    assert "League of Comic Geeks" in result.series.identifiers.keys()
    assert result.series.identifiers["League of Comic Geeks"]._id == SERIES_ID
    assert result.series.title == SERIES_TITLE
    assert result.series.start_year == SERIES_START_YEAR
    assert result.series.volume == SERIES_VOLUME
    # Publisher
    assert "League of Comic Geeks" in result.series.publisher.identifiers.keys()
    assert result.series.publisher.identifiers["League of Comic Geeks"]._id == PUBLISHER_ID
    assert result.series.publisher.title == PUBLISHER_TITLE
