__all__ = ["MokkariTalker"]

import html
from typing import Optional

from mokkari.exceptions import ApiError
from mokkari.issue import Issue as MokkariIssue
from mokkari.publisher import Publisher as MokkariPublisher
from mokkari.series import Series as MokkariSeries
from mokkari.session import Session as Mokkari
from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.models.metadata.enums import Format, Genre, Role, Source
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
from dex_starr.settings import MetronSettings


class MokkariTalker:
    def __init__(self, settings: MetronSettings):
        self.session = Mokkari(
            username=settings.username, passwd=settings.password, cache=SQLiteCache(expiry=14)
        )

    def update_issue(self, result: MokkariIssue, issue: Issue):
        if result.characters:
            issue.characters = sorted({x.name for x in result.characters}, alg=ns.NA | ns.G)
        if result.cover_date:
            issue.cover_date = result.cover_date
        if result.credits:
            issue.creators = sorted(
                {
                    Creator(
                        name=html.unescape(x.creator),
                        roles=sorted({Role.load(r.name) for r in x.role}, alg=ns.NA | ns.G),
                    )
                    for x in result.credits
                },
                alg=ns.NA | ns.G,
            )
        if result.series.series_type:
            issue.format = Format.load(result.series.series_type.name)
        if result.series.genres:
            issue.genres = sorted(
                {Genre.load(x.name) for x in result.series.genres}, alg=ns.NA | ns.G
            )
        # TODO: Add Language
        # TODO: Locations
        if result.number:
            issue.number = result.number
        issue.resources = sorted(
            {Resource(source=Source.METRON, value=result.id), *issue.resources}, alg=ns.NA | ns.G
        )
        if result.store_date:
            issue.store_date = result.store_date
        if result.arcs:
            issue.story_arcs = sorted(
                {StoryArc(title=x.name) for x in result.arcs}, alg=ns.NA | ns.G
            )
        if result.desc:
            issue.summary = result.desc
        if result.teams:
            issue.teams = sorted({x.name for x in result.teams}, alg=ns.NA | ns.G)
        if result.collection_title:
            issue.title = result.collection_title

    def _select_issue(self, issue_id: int) -> Optional[MokkariIssue]:
        CONSOLE.print(f"Getting Issue: {issue_id=}", style="logging.level.debug")
        try:
            return self.session.issue(issue_id)
        except ApiError:
            CONSOLE.print(f"Unable to get Issue: {issue_id=}", style="logging.level.warning")
        return None

    def _search_issue(self, series_id: int, number: str) -> Optional[MokkariIssue]:
        CONSOLE.print(f"Searching for Issue: {series_id=}, {number=}", style="logging.level.debug")
        output = None
        try:
            issue_list = self.session.issues_list({"series_id": series_id, "number": number})
        except ApiError:
            issue_list = []
        if issue_list := sorted(issue_list, key=lambda i: i.issue_name, alg=ns.NA | ns.G):
            issue_index = create_menu(
                options=[f"{i.id} | {i.issue_name or i.collection_title}" for i in issue_list],
                prompt="Select Issue",
                default="None of the Above",
            )
            if issue_index != 0:
                output = self._select_issue(issue_list[issue_index - 1].id)
        return output

    def lookup_issue(self, issue: Issue, series_id: int) -> Optional[MokkariIssue]:
        output = None
        source_list = [x.source for x in issue.resources]
        if Source.METRON in source_list:
            index = source_list.index(Source.METRON)
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

    def update_series(self, result: MokkariSeries, series: Series):
        series.resources = sorted(
            {Resource(source=Source.METRON, value=result.id), *series.resources}, alg=ns.NA | ns.G
        )
        if result.year_began:
            series.start_year = result.year_began
        if result.name:
            series.title = result.name
        if result.volume:
            series.volume = result.volume

    def _select_series(self, series_id: int) -> Optional[MokkariSeries]:
        CONSOLE.print(f"Getting Series: {series_id=}", style="logging.level.debug")
        try:
            return self.session.series(series_id)
        except ApiError:
            CONSOLE.print(f"Unable to get Series: {series_id=}", style="logging.level.warning")
        return None

    def _search_series(
        self,
        publisher_id: int,
        title: str,
        volume: Optional[int] = None,
        start_year: Optional[int] = None,
    ) -> Optional[MokkariSeries]:
        CONSOLE.print(
            f"Searching for Series: {publisher_id=}, {title=}, {volume=}, {start_year=}",
            style="logging.level.debug",
        )
        output = None
        params = {"publisher_id": publisher_id, "name": title}
        if volume:
            params["volume"] = volume
        if start_year:
            params["start_year"] = start_year
        try:
            series_list = self.session.series_list(params)
        except ApiError:
            series_list = []
        if series_list := sorted(series_list, key=lambda s: s.display_name, alg=ns.NA | ns.G):
            series_index = create_menu(
                options=[f"{s.id} | {s.display_name}" for s in series_list],
                prompt="Select Series",
                default="None of the Above",
            )
            if series_index != 0:
                output = self._select_series(series_list[series_index - 1].id)
        if not output and start_year:
            return self._search_series(publisher_id, title, volume=volume)
        if not output and volume:
            return self._search_series(publisher_id, title, start_year=start_year)
        return output

    def lookup_series(self, series: Series, publisher_id: int) -> Optional[MokkariSeries]:
        output = None
        source_list = [x.source for x in series.resources]
        if Source.METRON in source_list:
            index = source_list.index(Source.METRON)
            output = self._select_series(series.resources[index].value)
        if not output:
            output = self._search_series(
                publisher_id, series.title, series.volume, series.start_year
            )
        while not output:
            index = create_menu(
                options=["Enter Series id", "Enter Series title"], prompt="Select", default="Exit"
            )
            if index == 0:
                return
            elif index == 1:
                series_id = IntPrompt.ask("Series id", console=CONSOLE)
                output = self._select_series(series_id)
            else:
                series_title = Prompt.ask("Series title", console=CONSOLE)
                output = self._search_series(publisher_id, series_title)
        return output

    def update_publisher(self, result: MokkariPublisher, publisher: Publisher):
        publisher.resources = sorted(
            {Resource(source=Source.METRON, value=result.id), *publisher.resources},
            alg=ns.NA | ns.G,
        )
        if result.name:
            publisher.title = result.name

    def _select_publisher(self, publisher_id: int) -> Optional[MokkariPublisher]:
        CONSOLE.print(f"Getting Publisher: {publisher_id=}", style="logging.level.debug")
        try:
            return self.session.publisher(publisher_id)
        except ApiError:
            CONSOLE.print(
                f"Unable to get Publisher: {publisher_id=}", style="logging.level.warning"
            )
        return None

    def _search_publisher(self, title: str) -> Optional[MokkariPublisher]:
        CONSOLE.print(f"Searching for Publisher: {title=}", style="logging.level.debug")
        output = None
        try:
            publisher_list = self.session.publishers_list({"name": title})
        except ApiError:
            publisher_list = []
        if publisher_list := sorted(publisher_list, key=lambda p: p.name, alg=ns.NA | ns.G):
            publisher_index = create_menu(
                options=[f"{p.id} | {p.name}" for p in publisher_list],
                prompt="Select Publisher",
                default="None of the Above",
            )
            if publisher_index != 0:
                output = self._select_publisher(publisher_list[publisher_index - 1].id)
        return output

    def lookup_publisher(self, publisher: Publisher) -> Optional[MokkariPublisher]:
        output = None
        source_list = [x.source for x in publisher.resources]
        if Source.METRON in source_list:
            index = source_list.index(Source.METRON)
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
            if series := self.lookup_series(metadata.series, publisher.id):
                self.update_series(series, metadata.series)
                if issue := self.lookup_issue(metadata.issue, series.id):
                    self.update_issue(issue, metadata.issue)
