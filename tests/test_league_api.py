from datetime import date

from Organizer import ComicInfo, PublisherInfo, SeriesInfo
from Organizer.external.league_of_comic_geeks_api import parse_comic_result

PUBLISHER_ID = 1
PUBLISHER_TITLE = "DC Comics"
SERIES_ID = 110787
SERIES_TITLE = "Green Lantern"
COMIC_ID = 4579722
COMIC_NUMBER = "1"


def test_parse_series(league):
    result = league.get_series(SERIES_ID)
    assert int(result["details"]["id"]) == SERIES_ID
    assert result["details"]["title"] == SERIES_TITLE
    assert int(result["details"]["volume"]) == 4


def test_parse_comic(league):
    test_comic = league.get_comic(COMIC_ID)
    publisher_info = PublisherInfo(PUBLISHER_TITLE)
    series_info = SeriesInfo(publisher_info, SERIES_TITLE)
    comic_info = ComicInfo(series_info, COMIC_NUMBER)
    result = parse_comic_result(test_comic, comic_info)
    assert "League of Comic Geeks" in result.series.publisher.identifiers.keys()
    assert result.series.publisher.identifiers["League of Comic Geeks"]._id == PUBLISHER_ID
    assert result.series.publisher.title == PUBLISHER_TITLE

    assert "League of Comic Geeks" in result.series.identifiers.keys()
    assert result.series.identifiers["League of Comic Geeks"]._id == SERIES_ID
    assert result.series.title == SERIES_TITLE
    assert result.series.start_year == 2005

    assert "League of Comic Geeks" in result.identifiers.keys()
    assert result.identifiers["League of Comic Geeks"]._id == COMIC_ID
    assert result.cover_date == date(year=2005, month=5, day=18)
