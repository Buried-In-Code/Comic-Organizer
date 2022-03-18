from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from simyan.sqlite_cache import SQLiteCache

from dex_starr.service.league_of_comic_geeks.response import Comic, ComicResult, Series
from dex_starr.service.service import Service

MINUTE = 60


class Session(Service):
    API_URL = "https://leagueofcomicgeeks.com/api/"

    def __init__(self, api_key: str, client_id: str, cache: Optional[SQLiteCache] = None):
        super().__init__(cache=cache)

        self.headers["X-API-KEY"] = api_key
        self.headers["X-API-CLIENT"] = client_id

    def _get_request(
        self, endpoint: List[str], params: Dict[str, str] = None, skip_cache: bool = False
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        cache_params = f"?{urlencode(params)}" if params else ""

        url = self.API_URL + "/".join(endpoint)
        cache_key = f"{url}{cache_params}"

        if self.cache and not skip_cache:
            if cached_response := self.cache.select(cache_key):
                return cached_response

        response = self._get(url=url, params=params)
        if not response:
            return None

        if self.cache and not skip_cache:
            self.cache.insert(cache_key, response)

        return response

    def comic_list(self, search_term: str) -> List[ComicResult]:
        results = (
            self._get_request(["search", "format", "json"], params={"query": search_term}) or []
        )
        if results:
            results = ComicResult.schema().load(results, many=True)
        return results

    def series(self, id_: int) -> Optional[Series]:
        response = self._get_request(["series", "format", "json"], params={"series_id": str(id_)})
        if response and "details" in response:
            response = Series.from_dict(response["details"])
        return response

    def comic(self, id_: int) -> Optional[Comic]:
        response = self._get_request(["comic", "format", "json"], params={"comic_id": str(id_)})
        if response:
            response = Comic.from_dict(response)
        return response
