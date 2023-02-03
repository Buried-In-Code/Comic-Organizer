__all__ = ["SimyanTalker"]

from typing import Optional

from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import IntPrompt, Prompt
from simyan.comicvine import Comicvine
from simyan.exceptions import ServiceError
from simyan.schemas.issue import Issue as SimyanIssue
from simyan.schemas.publisher import Publisher as SimyanPublisher
from simyan.schemas.volume import Volume

from dex_starr.console import CONSOLE, create_menu
from dex_starr.models.metadata.enums import Role, Source
from dex_starr.models.metadata.schema import (
    Creator,
    Issue,
    Metadata,
    Publisher,
    Resource,
    Series,
    StoryArc,
)
from dex_starr.services.sqlite_cache import SQLiteCache
from dex_starr.settings import ComicvineSettings


class SimyanTalker:
    def __init__(self, settings: ComicvineSettings):
        self.session = Comicvine(api_key=settings.api_key, cache=SQLiteCache(expiry=14))

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
        issue.resources = sorted(
            {Resource(source=Source.COMICVINE, value=result.issue_id), *issue.resources},
            alg=ns.NA | ns.G,
        )
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

    def _select_issue(self, issue_id: int) -> Optional[SimyanIssue]:
        CONSOLE.print(f"Getting Issue: {issue_id=}", style="logging.level.debug")
        try:
            return self.session.issue(issue_id)
        except ServiceError:
            CONSOLE.print(f"Unable to get Issue: {issue_id=}", style="logging.level.warning")
        return None

    def _search_issue(self, series_id: int, number: str) -> Optional[SimyanIssue]:
        CONSOLE.print(f"Searching for Issue: {series_id=}, {number=}", style="logging.level.debug")
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
                output = self._select_issue(issue_list[issue_index - 1].issue_id)
        return output

    def lookup_issue(self, issue: Issue, series_id: int) -> Optional[SimyanIssue]:
        output = None
        source_list = [x.source for x in issue.resources]
        if Source.COMICVINE in source_list:
            index = source_list.index(Source.COMICVINE)
            output = self._select_issue(issue.resources[index].value)
        if not output:
            output = self._search_issue(series_id, issue.number)
        while not output:
            index = create_menu(
                options=["Enter Issue id", "Enter Issue number"], prompt="Select", default="Exit"
            )
            if index == 0:
                return
            elif index == 1:
                issue_id = IntPrompt.ask("Issue id", console=CONSOLE)
                output = self._select_issue(issue_id)
            else:
                issue_number = Prompt.ask("Issue number", console=CONSOLE)
                output = self._search_issue(series_id, issue_number)
        return output

    def update_series(self, result: Volume, series: Series):
        series.resources = sorted(
            {Resource(source=Source.COMICVINE, value=result.volume_id), *series.resources},
            alg=ns.NA | ns.G,
        )
        if result.start_year:
            series.start_year = result.start_year
        if result.name:
            series.title = result.name

    def _select_volume(self, volume_id: int) -> Optional[Volume]:
        CONSOLE.print(f"Getting Volume: {volume_id=}", style="logging.level.debug")
        try:
            return self.session.volume(volume_id)
        except ServiceError:
            CONSOLE.print(f"Unable to get Volume: {volume_id=}", style="logging.level.warning")
        return None

    def _search_volume(
        self, publisher_id: int, title: str, start_year: Optional[int] = None
    ) -> Optional[Volume]:
        CONSOLE.print(
            f"Searching for Volume: {publisher_id=}, {title=}, {start_year=}",
            style="logging.level.debug",
        )
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
                output = self._select_volume(volume_list[volume_index - 1].volume_id)
        if not output and start_year:
            return self._search_volume(publisher_id, title)
        return output

    def lookup_volume(self, series: Series, publisher_id: int) -> Optional[Volume]:
        output = None
        source_list = [x.source for x in series.resources]
        if Source.COMICVINE in source_list:
            index = source_list.index(Source.COMICVINE)
            output = self._select_volume(series.resources[index].value)
        if not output:
            output = self._search_volume(publisher_id, series.title, series.start_year)
        while not output:
            index = create_menu(
                options=["Enter Volume id", "Enter Volume title"], prompt="Select", default="Exit"
            )
            if index == 0:
                return
            elif index == 1:
                volume_id = IntPrompt.ask("Volume id", console=CONSOLE)
                output = self._select_volume(volume_id)
            else:
                volume_title = Prompt.ask("Volume title", console=CONSOLE)
                output = self._search_volume(publisher_id, volume_title)
        return output

    def update_publisher(self, result: SimyanPublisher, publisher: Publisher):
        publisher.resources = sorted(
            {Resource(source=Source.COMICVINE, value=result.publisher_id), *publisher.resources},
            alg=ns.NA | ns.G,
        )
        if result.name:
            publisher.title = result.name or publisher.title

    def _select_publisher(self, publisher_id: int) -> Optional[Publisher]:
        CONSOLE.print(f"Getting Publisher: {publisher_id=}", style="logging.level.debug")
        try:
            return self.session.publisher(publisher_id)
        except ServiceError:
            CONSOLE.print(
                f"Unable to get Publisher: {publisher_id=}", style="logging.level.warning"
            )
        return None

    def _search_publisher(self, title: str) -> Optional[SimyanPublisher]:
        CONSOLE.print(f"Searching for Publisher: {title=}", style="logging.level.debug")
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
                output = self._select_publisher(publisher_list[publisher_index - 1].publisher_id)
        return output

    def lookup_publisher(self, publisher: Publisher) -> Optional[SimyanPublisher]:
        output = None
        source_list = [x.source for x in publisher.resources]
        if Source.COMICVINE in source_list:
            index = source_list.index(Source.COMICVINE)
            output = self._select_publisher(publisher.resources[index].value)
        if not output:
            output = self._search_publisher(publisher.title)
        if not output and publisher.title.startswith("Marvel"):
            output = self._search_publisher("Marvel")
        while not output:
            index = create_menu(
                options=["Enter Publisher id", "Enter Publisher title"],
                prompt="Select",
                default="Exit",
            )
            if index == 0:
                return
            elif index == 1:
                publisher_id = IntPrompt.ask("Publisher id", console=CONSOLE)
                output = self._select_publisher(publisher_id)
            else:
                publisher_title = Prompt.ask("Publisher title", console=CONSOLE)
                output = self._search_publisher(publisher_title)
        return output

    def update_metadata(self, metadata: Metadata):
        if publisher := self.lookup_publisher(metadata.publisher):
            self.update_publisher(publisher, metadata.publisher)
            if volume := self.lookup_volume(metadata.series, publisher.publisher_id):
                self.update_series(volume, metadata.series)
                if issue := self.lookup_issue(metadata.issue, volume.volume_id):
                    self.update_issue(issue, metadata.issue)
