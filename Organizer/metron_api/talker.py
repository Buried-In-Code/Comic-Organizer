import logging
from typing import Optional

from mokkari import api
from mokkari.issue import Issue
from mokkari.publisher import Publisher
from mokkari.series import Series
from Simyan import SqliteCache

from Organizer.console import Console

LOGGER = logging.getLogger(__name__)


class Talker:
    def __init__(self, username: str, password: str, cache=None) -> None:
        if not cache:
            cache = SqliteCache()
        self.api = api(username, password, cache)

    def search_publishers(self, name: str) -> Optional[int]:
        LOGGER.debug("Search Publishers")
        results = self.api.publishers_list(params={"name": name})
        if results:
            index = Console.display_menu(
                items=[f"{item.id} | {item.name}" for item in results],
                exit_text="None of the Above",
                prompt="Select Publisher",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        name_search = Console.request_str("Publisher Name or `None`")
        if name_search and name_search.lower() != "none":
            return self.search_publishers(name=name_search)
        return Console.request_int("Publisher ID or `None`")

    def get_publisher(self, publisher_id: int) -> Publisher:
        LOGGER.debug("Getting Publisher")
        return self.api.publisher(publisher_id)

    def search_series(self, publisher_id: int, name: str, volume: Optional[int] = None) -> Optional[int]:
        LOGGER.debug("Search Series")
        params = {"publisher_id": publisher_id, "name": name}
        if volume:
            params["volume"] = volume
        results = self.api.series_list(params=params)
        if results:
            index = Console.display_menu(
                items=[f"{item.id} | {item.display_name}" for item in results],
                exit_text="None of the Above",
                prompt="Select Series",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        elif volume:
            return self.search_series(publisher_id=publisher_id, name=name)
        name_search = Console.request_str("Series Name or `None`")
        if name_search and name_search.lower() != "none":
            return self.search_series(publisher_id=publisher_id, name=name_search)
        return Console.request_int("Series ID or `None`")

    def get_series(self, series_id: int) -> Series:
        LOGGER.debug("Getting Series")
        return self.api.series(series_id)

    def search_issues(self, series_id: int, number: str) -> Optional[int]:
        LOGGER.debug("Search Issues")
        params = {"series_id": series_id, "number": number}
        results = self.api.issues_list(params=params)
        if results:
            index = Console.display_menu(
                items=[f"{item.id} | {item.issue_name} [{item.cover_date}]" for item in results],
                exit_text="None of the Above",
                prompt="Select Issue",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        number_search = Console.request_str("Issue Number or `None`")
        if number_search and number_search.lower() != "none":
            return self.search_issues(series_id=series_id, number=number_search)
        return Console.request_int("Issue ID or `None`")

    def get_issue(self, issue_id: int) -> Issue:
        LOGGER.debug("Getting Issue")
        return self.api.issue(issue_id)
