import logging
from configparser import ConfigParser
from json import JSONDecodeError
from typing import Dict, Any, List, Tuple

from requests import get
from requests.exceptions import HTTPError, ConnectionError

LOGGER = logging.getLogger(__name__)
CONFIG = ConfigParser()
CONFIG.read('config.ini')


def add_info():
    pass


def search_publisher(name: str) -> List[int]:
    pass


def select_publisher(id: int) -> Dict[str, Any]:
    pass


def search_series(name: str, year_began: int) -> List[int]:
    pass


def select_series(id: int) -> Dict[str, Any]:
    pass


def search_issues(number: str, publisher: str, series_name: str, series_volume: int) -> List[int]:
    pass


def select_issue(id: int) -> Dict[str, Any]:
    pass


def search_arcs(name: str) -> List[int]:
    pass


def select_arc(id: int) -> Dict[str, Any]:
    pass


def __request(endpoint: str, params: List[Tuple[str, str]] = None) -> Dict[str, Any]:
    if not CONFIG['Metron']['Username'] or not CONFIG['Metron']['Password']:
        LOGGER.warning('Unable to access Metron without a `Username` and `Password`')
        return {}
    if not params:
        params = []
    try:
        response = get(url=f"https://metron.cloud/api{endpoint}", headers={}, params=params)
        if response.status_code == 200:
            LOGGER.info(f"{response.status_code}: GET - {response.url}")
            try:
                return response.json()
            except (JSONDecodeError, KeyError):
                if response.text:
                    LOGGER.critical(f'Unable to parse the response message: {response.text}')
                return {}
    except (HTTPError, ConnectionError) as err:
        LOGGER.error(err)
        return {}
