from datetime import date, datetime

from Organizer.comic_format import ComicFormat

PUBLISHER_ID = 1
PUBLISHER_TITLE = "DC Comics"
SERIES_ID = 110787
SERIES_TITLE = "Green Lantern"
SERIES_START_YEAR = 2005
SERIES_VOLUME = 4
COMIC_ID = 4579722


def test_get_series(league):
    result = league.get_series(series_id=SERIES_ID)
    # Series
    assert int(result["details"]["id"]) == SERIES_ID
    assert result["details"]["title"] == SERIES_TITLE
    assert int(result["details"]["year_begin"]) == SERIES_START_YEAR
    assert int(result["details"]["volume"]) == SERIES_VOLUME
    # Publisher
    assert int(result["details"]["publisher_id"]) == PUBLISHER_ID
    assert result["details"]["publisher_name"] == PUBLISHER_TITLE


def test_get_comic(league):
    result = league.get_comic(comic_id=COMIC_ID)
    # Comic
    assert int(result["details"]["id"]) == COMIC_ID
    assert result["details"]["title"] == "Green Lantern #1"
    assert result["details"]["format"] == ComicFormat.COMIC.get_title()
    assert int(result["details"]["pages"]) == 40
    assert datetime.strptime(result["details"]["date_release"], "%Y-%m-%d").date() == date(year=2005, month=5, day=18)
    assert bool(result["details"]["variant"] != "0") is False
    # Series
    assert int(result["series"]["id"]) == SERIES_ID
    assert result["series"]["title"] == SERIES_TITLE
    assert int(result["series"]["year_begin"]) == SERIES_START_YEAR
    assert int(result["series"]["volume"]) == SERIES_VOLUME
    # Publisher
    assert int(result["series"]["publisher_id"]) == PUBLISHER_ID
    assert result["series"]["publisher_name"] == PUBLISHER_TITLE
