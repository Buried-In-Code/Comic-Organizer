import logging
from typing import Any, Dict, Optional, Tuple

from Simyan import SqliteCache

from DexStarr.console import Console
from DexStarr.league_of_comic_geeks_api.session import Session

LOGGER = logging.getLogger(__name__)


class Talker:
    def __init__(self, api_key: str, client_id: str, cache=None) -> None:
        if not cache:
            cache = SqliteCache()
        self.session = Session(api_key=api_key, client_id=client_id, cache=cache)

    def get_series(self, series_id: int) -> Dict[str, Any]:
        LOGGER.debug("Getting Series")
        return self.session.series(series_id)

    def search_comics(
        self, search_terms: Tuple[str, str], comic_format: Optional[str] = None, show_variants: bool = False
    ) -> Optional[int]:
        LOGGER.debug("Search Comics")

        results_1 = self.session.comic_list(search_terms[0])
        results_2 = []
        if search_terms[0] != search_terms[1]:
            results_2 = self.session.comic_list(search_terms[0])

        results = results_1 + results_2
        if not results:
            return None
        if comic_format:
            results = filter(lambda x: x["format"] == comic_format, results)
        results = sorted(
            results if show_variants else filter(lambda x: x["variant"] == "0", results),
            key=lambda x: (x["publisher_name"], x["series_name"], x["series_volume"], x["title"]),
        )
        if len(results) >= 1:
            index = Console.display_menu(
                items=[
                    f"{item['id']} | [{item['publisher_name']}] {item['series_name']} v{item['series_volume']} - "
                    f"{item['title']} - {item['format']}"
                    for item in results
                ],
                exit_text="None of the Above",
                prompt="Select Comic",
            )
            if 1 <= index <= len(results):
                return results[index - 1]["id"]
        search_term = Console.request_str("Comic Search Term or `None`")
        if search_term and search_term.lower() != "none":
            return self.search_comics(search_terms=(search_term, search_term))
        return Console.request_int("Comic ID or `None`")

    def get_comic(self, comic_id: int) -> Dict[str, Any]:
        LOGGER.debug("Getting Comic")
        return self.session.comic(comic_id)
