import logging
from typing import Optional

from Simyan import SqliteCache, api
from Simyan.issue import Issue
from Simyan.publisher import Publisher
from Simyan.story_arc import StoryArc
from Simyan.volume import Volume

from Organizer import Console

LOGGER = logging.getLogger(__name__)


class Talker:
    def __init__(self, api_key: str, cache=None) -> None:
        if not cache:
            cache = SqliteCache()
        self.session = api(api_key=api_key, cache=cache)

    def search_publishers(self, name: str) -> Optional[int]:
        LOGGER.debug("Search Publishers")
        results = self.session.publisher_list(params={"filter": f"name:{name}"})
        if results:
            index = Console.display_menu(
                items=[f"{item.id} | {item.name}" for item in results],
                exit_text="None of the Above",
                prompt="Select Publisher",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_publisher(self, publisher_id: int) -> Publisher:
        LOGGER.debug("Getting Publisher")
        return self.session.publisher(publisher_id)

    def search_volumes(
        self, name: str, publisher_id: Optional[int] = None, start_year: Optional[int] = None
    ) -> Optional[int]:
        LOGGER.debug("Search Volumes")
        results = self.session.volume_list(params={"filter": f"name:{name}"})
        if results and publisher_id:
            results = [x for x in results if x.publisher.id == publisher_id]
        if results and start_year:
            results = [x for x in results if x.start_year == start_year]
        if results:
            index = Console.display_menu(
                items=[f"{item.id} | {item.publisher.name} | {item.name} [{item.start_year}]" for item in results],
                exit_text="None of the Above",
                prompt="Select Volume",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_volume(self, volume_id: int) -> Volume:
        LOGGER.debug("Getting Volume")
        return self.session.volume(volume_id)

    def search_issues(self, volume_id: int, number: str) -> Optional[int]:
        LOGGER.debug("Search Issues")
        results = self.session.issue_list(params={"filter": f"volume:{volume_id},issue_number:{number}"})
        if results:
            index = Console.display_menu(
                items=[
                    f"{item.id} | {item.publisher.name} | {item.name} [{item.start_year}] #{item.issue_number}"
                    for item in results
                ],
                exit_text="None of the Above",
                prompt="Select Issue",
            )
            if 1 <= index <= len(results):
                return results[index - 1].id
        return None

    def get_issue(self, issue_id: int) -> Issue:
        LOGGER.debug("Getting Issue")
        return self.session.issue(issue_id)

    def search_arcs(self, name: str) -> Optional[int]:
        LOGGER.debug("Search Arcs")
        pass

    def get_arc(self, arc_id: int) -> StoryArc:
        LOGGER.debug("Getting Arc")
        return self.session.story_arc(arc_id)
