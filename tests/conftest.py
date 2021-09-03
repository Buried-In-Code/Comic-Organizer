import pytest
from Simyan import SqliteCache

from Organizer.comicvine_api import Talker as Comicvine
from Organizer.league_of_comic_geeks_api import Talker as League
from Organizer.metron_api import Talker as Metron
from Organizer.utils import COMICVINE_API_KEY, LEAGUE_API_KEY, LEAGUE_CLIENT_ID, METRON_PASSWORD, METRON_USERNAME


@pytest.fixture(scope="session")
def metron():
    return Metron(METRON_USERNAME, METRON_PASSWORD, cache=SqliteCache("tests/Comic-Organizer.sqlite"))


@pytest.fixture(scope="session")
def comicvine():
    return Comicvine(COMICVINE_API_KEY, cache=SqliteCache("tests/Comic-Organizer.sqlite"))


@pytest.fixture(scope="session")
def league():
    return League(LEAGUE_API_KEY, LEAGUE_CLIENT_ID, cache=SqliteCache("tests/Comic-Organizer.sqlite"))
