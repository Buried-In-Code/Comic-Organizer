import os

import pytest
from simyan.sqlite_cache import SQLiteCache

from dex_starr.services.league_of_comic_geeks.service import LeagueOfComicGeeks


@pytest.fixture(scope="session")
def league_of_comic_geeks_api_key():
    return os.getenv("LEAGUE_OF_COMIC_GEEKS_API_KEY", default="INVALID")


@pytest.fixture(scope="session")
def league_of_comic_geeks_client_id():
    return os.getenv("LEAGUE_OF_COMIC_GEEKS_CLIENT_ID", default="INVALID")


@pytest.fixture(scope="session")
def league_of_comic_geeks(
    league_of_comic_geeks_api_key, league_of_comic_geeks_client_id
) -> LeagueOfComicGeeks:
    return LeagueOfComicGeeks(
        api_key=league_of_comic_geeks_api_key,
        client_id=league_of_comic_geeks_client_id,
        cache=SQLiteCache("tests/cache.sqlite", expiry=None),
    )
