import os

import pytest
from Simyan import SqliteCache

from Organizer.external.comicvine_api import Talker as Comicvine
from Organizer.external.league_of_comic_geeks_api import Talker as League
from Organizer.external.metron_api import Talker as Metron


@pytest.fixture(scope="session")
def comicvine_api_key():
    return os.getenv("COMICVINE_API_KEY", "INVALID")


@pytest.fixture(scope="session")
def comicvine(comicvine_api_key):
    return Comicvine(comicvine_api_key, cache=SqliteCache("tests/Comic-Organizer.sqlite"))


@pytest.fixture(scope="session")
def league_api_key():
    return os.getenv("LEAGUE_API_KEY", "INVALID")


@pytest.fixture(scope="session")
def league_client_id():
    return os.getenv("LEAGUE_CLIENT_ID", "INVALID")


@pytest.fixture(scope="session")
def league(league_api_key, league_client_id):
    return League(league_api_key, league_client_id, cache=SqliteCache("tests/Comic-Organizer.sqlite"))


@pytest.fixture(scope="session")
def metron_username():
    return os.getenv("METRON_USERNAME", "INVALID")


@pytest.fixture(scope="session")
def metron_password():
    return os.getenv("METRON_PASSWORD", "INVALID")


@pytest.fixture(scope="session")
def metron(metron_username, metron_password):
    return Metron(metron_username, metron_password, cache=SqliteCache("tests/Comic-Organizer.sqlite"))
