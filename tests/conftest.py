import pytest
from Simyan import SqliteCache

from Organizer.metron_api import Talker
from Organizer.utils import METRON_PASSWORD, METRON_USERNAME


@pytest.fixture(scope="session")
def talker():
    return Talker(METRON_USERNAME, METRON_PASSWORD, cache=SqliteCache("tests/Comic-Organizer.sqlite"))
