import logging
import platform
from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Union

from ratelimit import limits, sleep_and_retry
from requests import get
from requests.exceptions import ConnectionError, HTTPError
from simyan.sqlite_cache import SQLiteCache

from dex_starr import __version__

LOGGER = logging.getLogger(__name__)
MINUTE = 60


class Service:
    def __init__(self, cache: Optional[SQLiteCache] = None):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": f"Dex-Starr/{__version__}/{platform.system()}: {platform.release()}",
        }
        self.cache = cache

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def _get(
        self, url: str, params: Dict[str, Union[str, int]] = None
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        if params is None:
            params = {}

        try:
            response = get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except ConnectionError as ce:
            LOGGER.error(f"Unable to connect to `{url}`: {ce}")
        except HTTPError as he:
            LOGGER.error(he.response.text)
        except JSONDecodeError as de:
            LOGGER.error(f"Invalid response from `{url}`: {de}")

        return None
