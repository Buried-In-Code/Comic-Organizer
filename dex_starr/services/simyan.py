__all__ = ["SimyanTalker"]

import logging
from typing import Optional

from rich.prompt import Prompt
from simyan.comicvine import Comicvine
from simyan.exceptions import ServiceError
from simyan.schemas.issue import Issue as SimyanIssue
from simyan.schemas.publisher import Publisher as SimyanPublisher
from simyan.schemas.volume import Volume

from ..console import CONSOLE, create_menu
from ..metadata.metadata import Creator, Issue, Metadata, Publisher, Series, StoryArc
from .sqlite_cache import SQLiteCache

LOGGER = logging.getLogger(__name__)


class SimyanTalker:
    def __init__(self, api_key: str):
        self.session = Comicvine(api_key=api_key, cache=SQLiteCache(expiry=14))

    def update_issue(self, simyan_issue: SimyanIssue, issue: Issue):
        issue.characters = sorted(
            {
                *issue.characters,
                *[x.name for x in simyan_issue.characters],
                *[x.name for x in simyan_issue.first_appearance_characters],
                *[x.name for x in simyan_issue.deaths],
            }
        )
        issue.cover_date = simyan_issue.cover_date or issue.cover_date
        # region Set Creators
        for simyan_creator in simyan_issue.creators:
            found = False
            for creator in issue.creators:
                if simyan_creator.name == creator.name:
                    found = True
                    creator.roles = sorted(
                        {
                            *creator.roles,
                            *[
                                x.strip().title()
                                for role in simyan_creator.role_list
                                for x in role.split(",")
                            ],
                        }
                    )
            if not found:
                issue.creators.append(
                    Creator(
                        name=simyan_creator.name,
                        roles=sorted(
                            x.strip().title()
                            for role in simyan_creator.role_list
                            for x in role.split(",")
                        ),
                    )
                )
        # endregion
        # Format
        # Genres
        # Language
        issue.locations = sorted(
            {
                *issue.locations,
                *[x.name for x in simyan_issue.locations],
                *[x.name for x in simyan_issue.first_appearance_locations],
            }
        )
        issue.number = simyan_issue.number or issue.number
        # Page Count
        issue.sources["Comicvine"] = simyan_issue.issue_id
        issue.store_date = simyan_issue.store_date or issue.store_date
        # region Set Story Arcs
        for simyan_story_arc in simyan_issue.story_arcs:
            found = False
            for story_arc in issue.story_arcs:
                if simyan_story_arc.name == story_arc.title:
                    found = True
            if not found:
                issue.story_arcs.append(StoryArc(title=simyan_story_arc.name))
        for simyan_story_arc in simyan_issue.first_appearance_story_arcs:
            found = False
            for story_arc in issue.story_arcs:
                if simyan_story_arc.name == story_arc.title:
                    found = True
            if not found:
                issue.story_arcs.append(StoryArc(title=simyan_story_arc.name))
        issue.story_arcs.sort()
        # endregion
        issue.summary = simyan_issue.summary or issue.summary
        issue.teams = sorted(
            {
                *issue.teams,
                *[x.name for x in simyan_issue.teams],
                *[x.name for x in simyan_issue.first_appearance_teams],
                *[x.name for x in simyan_issue.teams_disbanded],
            }
        )
        issue.title = simyan_issue.name or issue.title

    def _search_issue(self, series_id: int, number: str) -> Optional[SimyanIssue]:
        simyan_issue = None
        try:
            issue_list = self.session.issue_list(
                {"filter": f"volume:{series_id},issue_number:{number}"}
            )
        except ServiceError:
            issue_list = []
        if not issue_list:
            LOGGER.warning("Unable to find a matching issue")
            return None
        issue_list = sorted(issue_list, key=lambda i: i.number)
        issue_index = create_menu(
            options=[f"{i.issue_id} | {i.volume.name} #{i.number}" for i in issue_list],
            prompt="Select Issue",
            default="None of the Above",
        )
        if issue_index != 0:
            try:
                simyan_issue = self.session.issue(issue_list[issue_index - 1].issue_id)
            except ServiceError:
                simyan_issue = None
        return simyan_issue

    def lookup_issue(self, issue: Issue, series_id: int) -> Optional[SimyanIssue]:
        simyan_issue = None
        if "Comicvine" in issue.sources:
            try:
                simyan_issue = self.session.issue(issue.sources["Comicvine"])
            except ServiceError:
                simyan_issue = None
        if not simyan_issue:
            simyan_issue = self._search_issue(series_id, issue.number)
        while not simyan_issue:
            search = Prompt.ask("Issue number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            simyan_issue = self._search_issue(series_id, search)
        return simyan_issue

    def update_series(self, simyan_volume: Volume, series: Series):
        series.sources["Comicvine"] = simyan_volume.volume_id
        series.start_year = simyan_volume.start_year or series.start_year
        series.title = simyan_volume.name or series.title

    def _search_volume(
        self, publisher_id: int, title: str, start_year: Optional[int] = None
    ) -> Optional[Volume]:
        simyan_volume = None
        try:
            volume_list = self.session.volume_list({"filter": f"name:{title}"})
        except ServiceError:
            volume_list = []
        volume_list = filter(lambda v: v.publisher is not None, volume_list)
        volume_list = filter(lambda v: v.publisher.id_ == publisher_id, volume_list)
        if start_year:
            volume_list = filter(lambda v: v.start_year == start_year, volume_list)
        if not volume_list:
            LOGGER.warning("Unable to find a matching volume")
            return None
        volume_list = sorted(volume_list, key=lambda v: (v.name, v.start_year or 0))
        volume_index = create_menu(
            options=[f"{v.volume_id} | {v.name} ({v.start_year})" for v in volume_list],
            prompt="Select Volume",
            default="None of the Above",
        )
        if volume_index != 0:
            try:
                simyan_volume = self.session.volume(volume_list[volume_index - 1].volume_id)
            except ServiceError:
                simyan_volume = None
        if not simyan_volume and start_year:
            return self._search_volume(publisher_id, title)
        return simyan_volume

    def lookup_volume(self, series: Series, publisher_id: int) -> Optional[Volume]:
        simyan_volume = None
        if "Comicvine" in series.sources:
            try:
                simyan_volume = self.session.volume(series.sources["Comicvine"])
            except ServiceError:
                simyan_volume = None
        if not simyan_volume:
            simyan_volume = self._search_volume(publisher_id, series.title, series.start_year)
        while not simyan_volume:
            search = Prompt.ask("Volume title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            simyan_volume = self._search_volume(publisher_id, search)
        return simyan_volume

    def update_publisher(self, simyan_publisher: SimyanPublisher, publisher: Publisher):
        publisher.sources["Comicvine"] = simyan_publisher.publisher_id
        publisher.title = simyan_publisher.name or publisher.title

    def _search_publisher(self, title: str) -> Optional[SimyanPublisher]:
        simyan_publisher = None
        try:
            publisher_list = self.session.publisher_list({"filter": f"name:{title}"})
        except ServiceError:
            publisher_list = []
        if not publisher_list:
            LOGGER.warning("Unable to find a matching publisher")
            return None
        publisher_list = sorted(publisher_list, key=lambda p: p.name)
        publisher_index = create_menu(
            options=[f"{p.publisher_id} | {p.name}" for p in publisher_list],
            prompt="Select Publisher",
            default="None of the Above",
        )
        if publisher_index != 0:
            try:
                simyan_publisher = self.session.publisher(
                    publisher_list[publisher_index - 1].publisher_id
                )
            except ServiceError:
                simyan_publisher = None
        return simyan_publisher

    def lookup_publisher(self, publisher: Publisher) -> Optional[SimyanPublisher]:
        simyan_publisher = None
        if "Comicvine" in publisher.sources:
            try:
                simyan_publisher = self.session.publisher(publisher.sources["Comicvine"])
            except ServiceError:
                simyan_publisher = None
        if not simyan_publisher:
            simyan_publisher = self._search_publisher(publisher.title)
        while not simyan_publisher:
            search = Prompt.ask("Publisher title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            simyan_publisher = self._search_publisher(search)
        return simyan_publisher

    def update_metadata(self, metadata: Metadata):
        if simyan_publisher := self.lookup_publisher(metadata.publisher):
            self.update_publisher(simyan_publisher, metadata.publisher)
            if simyan_volume := self.lookup_volume(
                metadata.series, metadata.publisher.sources["Comicvine"]
            ):
                self.update_series(simyan_volume, metadata.series)
                if simyan_issue := self.lookup_issue(
                    metadata.issue, metadata.series.sources["Comicvine"]
                ):
                    self.update_issue(simyan_issue, metadata.issue)
