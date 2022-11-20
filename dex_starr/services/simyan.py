__all__ = ["SimyanTalker"]

import logging
from typing import Optional

from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import Prompt
from simyan.comicvine import Comicvine
from simyan.exceptions import ServiceError
from simyan.schemas.issue import Issue as SimyanIssue
from simyan.schemas.publisher import Publisher as SimyanPublisher
from simyan.schemas.volume import Volume

from dex_starr.console import CONSOLE, RichLogger, create_menu
from dex_starr.schemas.metadata.enums import Role
from dex_starr.schemas.metadata.schema import Creator, Issue, Metadata, Publisher, Series, StoryArc
from dex_starr.services.sqlite_cache import SQLiteCache

LOGGER = RichLogger(logging.getLogger(__name__))


class SimyanTalker:
    def __init__(self, api_key: str):
        self.session = Comicvine(api_key=api_key, cache=SQLiteCache(expiry=14))

    def update_issue(self, result: SimyanIssue, issue: Issue):
        if result.characters or result.first_appearance_characters or result.deaths:
            issue.characters = sorted(
                {
                    *{x.name for x in result.characters},
                    *{x.name for x in result.first_appearance_characters},
                    *{x.name for x in result.deaths},
                },
                alg=ns.NA | ns.G,
            )
        if result.cover_date:
            issue.cover_date = result.cover_date
        if result.creators:
            issue.creators = sorted(
                {
                    Creator(
                        name=x.name,
                        roles=sorted(
                            {Role.load(r.strip()) for role in x.role_list for r in role.split(",")},
                            alg=ns.NA | ns.G,
                        ),
                    )
                    for x in result.creators
                },
                alg=ns.NA | ns.G,
            )
        # TODO: Format
        # TODO: Genres
        # TODO: Language
        if result.locations or result.first_appearance_locations:
            issue.locations = sorted(
                {
                    *{x.name for x in result.locations},
                    *{x.name for x in result.first_appearance_locations},
                },
                alg=ns.NA | ns.G,
            )
        if result.number:
            issue.number = result.number
        # TODO: Page Count
        issue.sources.comicvine = result.issue_id
        if result.store_date:
            issue.store_date = result.store_date
        if result.story_arcs or result.first_appearance_story_arcs:
            issue.story_arcs = sorted(
                {
                    *{StoryArc(title=x.name) for x in result.story_arcs},
                    *{StoryArc(title=x.name) for x in result.first_appearance_story_arcs},
                },
                alg=ns.NA | ns.G,
            )
        if result.summary:
            issue.summary = result.summary
        if result.teams or result.first_appearance_teams or result.teams_disbanded:
            issue.teams = sorted(
                {
                    *{x.name for x in result.teams},
                    *{x.name for x in result.first_appearance_teams},
                    *{x.name for x in result.teams_disbanded},
                },
                alg=ns.NA | ns.G,
            )
        if result.name:
            issue.title = result.name

    def _search_issue(self, series_id: int, number: str) -> Optional[SimyanIssue]:
        LOGGER.debug(f"Searching for: {series_id=}, {number=}")
        output = None
        try:
            issue_list = self.session.issue_list(
                {"filter": f"volume:{series_id},issue_number:{number}"}
            )
        except ServiceError:
            issue_list = []
        if issue_list := sorted(issue_list, key=lambda i: i.number, alg=ns.NA | ns.G):
            issue_index = create_menu(
                options=[f"{i.issue_id} | {i.volume.name} #{i.number}" for i in issue_list],
                prompt="Select Issue",
                default="None of the Above",
            )
            if issue_index != 0:
                try:
                    output = self.session.issue(issue_list[issue_index - 1].issue_id)
                except ServiceError:
                    LOGGER.warning(
                        f"Unable to find issue: issue_id={issue_list[issue_index - 1].issue_id}"
                    )
                    output = None
        else:
            LOGGER.info(f"Unable to find issue: {series_id=}, {number=}")
        return output

    def lookup_issue(self, issue: Issue, series_id: int) -> Optional[SimyanIssue]:
        output = None
        if issue.sources.comicvine:
            try:
                output = self.session.issue(issue.sources.comicvine)
            except ServiceError:
                LOGGER.warning(f"Unable to find issue: issue_id={issue.sources.comicvine}")
                output = None
        if not output:
            output = self._search_issue(series_id, issue.number)
        while not output:
            search = Prompt.ask("Issue number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            output = self._search_issue(series_id, search)
        return output

    def update_series(self, result: Volume, series: Series):
        series.sources.comicvine = result.volume_id
        if result.start_year:
            series.start_year = result.start_year
        if result.name:
            series.title = result.name

    def _search_volume(
        self, publisher_id: int, title: str, start_year: Optional[int] = None
    ) -> Optional[Volume]:
        LOGGER.debug(f"Searching for: {publisher_id=}, {title=}, {start_year=}")
        output = None
        try:
            volume_list = self.session.volume_list({"filter": f"name:{title}"})
        except ServiceError:
            volume_list = []
        volume_list = filter(
            lambda v: v.publisher is not None and v.publisher.id_ == publisher_id, volume_list
        )
        if start_year:
            volume_list = filter(lambda v: v.start_year == start_year, volume_list)
        if volume_list := sorted(
            volume_list, key=lambda v: (v.name, v.start_year or 0), alg=ns.NA | ns.G
        ):
            volume_index = create_menu(
                options=[f"{v.volume_id} | {v.name} ({v.start_year})" for v in volume_list],
                prompt="Select Volume",
                default="None of the Above",
            )
            if volume_index != 0:
                try:
                    output = self.session.volume(volume_list[volume_index - 1].volume_id)
                except ServiceError:
                    LOGGER.warning(
                        "Unable to find volume: "
                        f"volume_id={volume_list[volume_index - 1].volume_id}"
                    )
                    output = None
        else:
            LOGGER.info(f"Unable to find volume: {publisher_id=}, {title=}, {start_year=}")
        if not output and start_year:
            return self._search_volume(publisher_id, title)
        return output

    def lookup_volume(self, series: Series, publisher_id: int) -> Optional[Volume]:
        output = None
        if series.sources.comicvine:
            try:
                output = self.session.volume(series.sources.comicvine)
            except ServiceError:
                LOGGER.warning(f"Unable to find volume: volume_id={series.sources.comicvine}")
                output = None
        if not output:
            output = self._search_volume(publisher_id, series.title, series.start_year)
        while not output:
            search = Prompt.ask("Volume title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            output = self._search_volume(publisher_id, search)
        return output

    def update_publisher(self, result: SimyanPublisher, publisher: Publisher):
        publisher.sources.comicvine = result.publisher_id
        if result.name:
            publisher.title = result.name or publisher.title

    def _search_publisher(self, title: str) -> Optional[SimyanPublisher]:
        LOGGER.debug(f"Searching for: {title=}")
        output = None
        try:
            publisher_list = self.session.publisher_list({"filter": f"name:{title}"})
        except ServiceError:
            publisher_list = []
        if publisher_list := sorted(publisher_list, key=lambda p: p.name, alg=ns.NA | ns.G):
            publisher_index = create_menu(
                options=[f"{p.publisher_id} | {p.name}" for p in publisher_list],
                prompt="Select Publisher",
                default="None of the Above",
            )
            if publisher_index != 0:
                try:
                    output = self.session.publisher(
                        publisher_list[publisher_index - 1].publisher_id
                    )
                except ServiceError:
                    LOGGER.warning(
                        "Unable to find publisher: "
                        f"publisher_id={publisher_list[publisher_index - 1].publisher_id}"
                    )
                    output = None
        else:
            LOGGER.info(f"Unable to find publisher: {title=}")
        return output

    def lookup_publisher(self, publisher: Publisher) -> Optional[SimyanPublisher]:
        output = None
        if publisher.sources.comicvine:
            try:
                output = self.session.publisher(publisher.sources.comicvine)
            except ServiceError:
                LOGGER.warning(
                    f"Unable to find publisher: publisher_id={publisher.sources.comicvine}"
                )
                output = None
        if not output:
            output = self._search_publisher(publisher.title)
        while not output:
            search = Prompt.ask("Publisher title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            output = self._search_publisher(search)
        return output

    def update_metadata(self, metadata: Metadata):
        if publisher := self.lookup_publisher(metadata.publisher):
            self.update_publisher(publisher, metadata.publisher)
            if volume := self.lookup_volume(metadata.series, metadata.publisher.sources.comicvine):
                self.update_series(volume, metadata.series)
                if issue := self.lookup_issue(metadata.issue, metadata.series.sources.comicvine):
                    self.update_issue(issue, metadata.issue)
