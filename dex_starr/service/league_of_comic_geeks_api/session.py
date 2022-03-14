import platform
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from ratelimit import limits, sleep_and_retry
from requests import get
from requests.exceptions import ConnectionError, JSONDecodeError
from simyan.exceptions import APIError, CacheError
from simyan.sqlite_cache import SQLiteCache

MINUTE = 60


class Session:
    def __init__(self, api_key: str, client_id: str, cache: Optional[SQLiteCache] = None):
        self.api_key = api_key
        self.api_client = client_id
        self.header = {
            "User-Agent": f"Dex-Starr/{platform.system()}: {platform.release()}",
            "X-API-KEY": self.api_key,
            "X-API-CLIENT": self.api_client,
        }
        self.api_url = "https://leagueofcomicgeeks.com/api/{}/"
        self.cache = cache

    def _get_request(
        self, endpoint: List[Union[str, int]], params: Dict[str, Union[str, int]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if params is None:
            params = {}

        cache_params = ""
        if params:
            ordered_params = OrderedDict(sorted(params.items(), key=lambda x: x[0]))
            cache_params = f"?{urlencode(ordered_params)}"

        url = self.api_url.format("/".join(str(e) for e in endpoint))
        cache_key = f"{url}{cache_params}"

        if self.cache:
            try:
                cached_response = self.cache.get(cache_key)
                if cached_response is not None:
                    return cached_response
            except AttributeError as err:
                raise CacheError(f"Cache object passed in is missing attribute: {err}")

        data = self.__perform_get_request(url, params=params)

        if self.cache:
            try:
                self.cache.insert(cache_key, data)
            except AttributeError as err:
                raise CacheError(f"Cache object passed in is missing attribute: {err}")

        return data

    def series(self, _id: int) -> Dict[str, Any]:
        try:
            return self._get_request(["series", "format", "json"], params={"series_id": str(_id)})
        except APIError:
            return {}

    def comic(self, _id: int) -> Dict[str, Any]:
        try:
            return self._get_request(["comic", "format", "json"], params={"comic_id": str(_id)})
        except APIError:
            return {}

    def comic_list(self, search_term: str) -> List[Dict[str, Any]]:
        try:
            return self._get_request(["search", "format", "json"], params={"query": search_term})
        except APIError:
            return []

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def __perform_get_request(
        self, url: str, params: Dict[str, Union[str, int]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if params is None:
            params = {}

        try:
            response = get(url, params=params, headers=self.header)
            data = response.json()
        except ConnectionError as err:
            raise APIError(f"Unable to connect to `{url}`: {err}")
        except JSONDecodeError as err:
            raise APIError(f"Invalid response from `{url}`: {err}")

        return data
