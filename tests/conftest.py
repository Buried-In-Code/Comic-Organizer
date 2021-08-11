import os

import pytest
from Organizer.metron_api import Talker
from mokkari import api, sqlite_cache

from Organizer.utils import METRON_PASSWORD, METRON_USERNAME


@pytest.fixture(scope="session")
def talker():
    return Talker(
        METRON_USERNAME,
        METRON_PASSWORD,
        cache="tests/testing_mock.sqlite",
    )
