from datetime import date

PUBLISHER_ID = 10
PUBLISHER_TITLE = "DC Comics"
VOLUME_ID = 18216
VOLUME_TITLE = "Green Lantern"
VOLUME_START_YEAR = 2005
ISSUE_ID = 111265


def test_get_publisher(comicvine):
    result = comicvine.get_publisher(publisher_id=PUBLISHER_ID)
    # Publisher
    assert result.id == PUBLISHER_ID
    assert result.name == PUBLISHER_TITLE


def test_get_volume(comicvine):
    result = comicvine.get_volume(volume_id=VOLUME_ID)
    # Volume
    assert result.id == VOLUME_ID
    assert result.name == VOLUME_TITLE
    assert int(result.start_year) == VOLUME_START_YEAR
    # Publisher
    assert result.publisher.id == PUBLISHER_ID
    assert result.publisher.name == PUBLISHER_TITLE


def test_get_issue(comicvine):
    result = comicvine.get_issue(issue_id=ISSUE_ID)
    # Issue
    assert result.id == ISSUE_ID
    assert result.number == "1"
    assert result.name == "Airborne"
    assert result.cover_date == date(year=2005, month=7, day=1)
    assert result.store_date == date(year=2005, month=5, day=18)
    # Volume
    assert result.volume.id == VOLUME_ID
    assert result.volume.name == VOLUME_TITLE
