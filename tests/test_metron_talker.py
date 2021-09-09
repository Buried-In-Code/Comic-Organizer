from datetime import date

PUBLISHER_ID = 2
PUBLISHER_TITLE = "DC Comics"
SERIES_ID = 1119
SERIES_TITLE = "Green Lantern"
ISSUE_ID = 9778


def test_get_publisher(metron):
    result = metron.get_publisher(publisher_id=PUBLISHER_ID)
    # Publisher
    assert result.id == PUBLISHER_ID
    assert result.name == PUBLISHER_TITLE


def test_get_series(metron):
    result = metron.get_series(series_id=SERIES_ID)
    # Series
    assert result.id == SERIES_ID
    assert result.name == SERIES_TITLE
    assert result.year_began == 2005
    assert result.volume == 4
    # Publisher
    assert result.publisher_id == PUBLISHER_ID


def test_get_issue(metron):
    result = metron.get_issue(issue_id=ISSUE_ID)
    # Issue
    assert result.id == ISSUE_ID
    assert result.number == "1"
    assert result.story_titles == ["Airborne"]
    assert result.cover_date == date(year=2005, month=7, day=1)
    assert result.store_date == date(year=2005, month=5, day=25)
    # Series
    assert result.series.id == SERIES_ID
    assert result.series.name == SERIES_TITLE
    # Publisher
    assert result.publisher.id == PUBLISHER_ID
    assert result.publisher.name == PUBLISHER_TITLE
