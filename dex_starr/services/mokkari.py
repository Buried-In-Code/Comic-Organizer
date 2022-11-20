__all__ = ["MokkariTalker"]

import html
import logging
from typing import Optional

from mokkari.exceptions import ApiError
from mokkari.issue import Issue as MokkariIssue
from mokkari.publisher import Publisher as MokkariPublisher
from mokkari.series import Series as MokkariSeries
from mokkari.session import Session as Mokkari
from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import Prompt

from dex_starr.console import CONSOLE, RichLogger, create_menu
from dex_starr.schemas.metadata.enums import Format, Genre, Role
from dex_starr.schemas.metadata.schema import Creator, Issue, Metadata, Publisher, Series, StoryArc
from dex_starr.services.sqlite_cache import SQLiteCache

LOGGER = RichLogger(logging.getLogger(__name__))


class MokkariTalker:
    def __init__(self, username: str, password: str):
        self.session = Mokkari(username=username, passwd=password, cache=SQLiteCache(expiry=14))

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
        issue.sources.metron = result.id
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

    def _search_issue(self, series_id: int, number: str) -> Optional[MokkariIssue]:
        LOGGER.debug(f"Searching for: {series_id=}, {number=}")
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
                try:
                    output = self.session.issue(issue_list[issue_index - 1].id)
                except ApiError:
                    LOGGER.warning(
                        f"Unable to find issue: issue_id={issue_list[issue_index - 1].id}"
                    )
                    output = None
        else:
            LOGGER.info(f"Unable to find issue: {series_id=}, {number=}")
        return output

    def lookup_issue(self, issue: Issue, series_id: int) -> Optional[MokkariIssue]:
        output = None
        if issue.sources.metron:
            try:
                output = self.session.issue(issue.sources.metron)
            except ApiError:
                LOGGER.warning(f"Unable to find issue: issue_id={issue.sources.metron}")
                output = None
        if not output:
            output = self._search_issue(series_id, issue.number)
        while not output:
            search = Prompt.ask("Issue number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            output = self._search_issue(series_id, search)
        return output

    def update_series(self, result: MokkariSeries, series: Series):
        series.sources.metron = result.id
        if result.year_began:
            series.start_year = result.year_began
        if result.name:
            series.title = result.name
        if result.volume:
            series.volume = result.volume

    def _search_series(
        self,
        publisher_id: int,
        title: str,
        volume: Optional[int] = None,
        start_year: Optional[int] = None,
    ) -> Optional[MokkariSeries]:
        LOGGER.debug(f"Searching for: {publisher_id=}, {title=}, {volume=}, {start_year=}")
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
                try:
                    output = self.session.series(series_list[series_index - 1].id)
                except ApiError:
                    LOGGER.warning(
                        f"Unable to find series: series_id={series_list[series_index - 1].id}"
                    )
                    output = None
        else:
            LOGGER.info(
                f"Unable to find series: {publisher_id=}, {title=}, {volume=}, {start_year=}"
            )
        if not output and start_year:
            return self._search_series(publisher_id, title, volume=volume)
        if not output and volume:
            return self._search_series(publisher_id, title, start_year=start_year)
        return output

    def lookup_series(self, series: Series, publisher_id: int) -> Optional[MokkariSeries]:
        output = None
        if series.sources.metron:
            try:
                output = self.session.series(series.sources.metron)
            except ApiError:
                LOGGER.warning(f"Unable to find series: series_id={series.sources.metron}")
                output = None
        if not output:
            output = self._search_series(
                publisher_id, series.title, series.volume, series.start_year
            )
        while not output:
            search = Prompt.ask("Series title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            output = self._search_series(publisher_id, search)
        return output

    def update_publisher(self, result: MokkariPublisher, publisher: Publisher):
        publisher.sources.metron = result.id
        if result.name:
            publisher.title = result.name

    def _search_publisher(self, title: str) -> Optional[MokkariPublisher]:
        LOGGER.debug(f"Searching for: {title=}")
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
                try:
                    output = self.session.publisher(publisher_list[publisher_index - 1].id)
                except ApiError:
                    LOGGER.warning(
                        "Unable to find publisher: "
                        f"publisher_id={publisher_list[publisher_index - 1].id}"
                    )
                    output = None
        else:
            LOGGER.info(f"Unable to find publisher: {title=}")
        return output

    def lookup_publisher(self, publisher: Publisher) -> Optional[MokkariPublisher]:
        output = None
        if publisher.sources.metron:
            try:
                output = self.session.publisher(publisher.sources.metron)
            except ApiError:
                LOGGER.warning(f"Unable to find publisher: publisher_id={publisher.sources.metron}")
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
            if series := self.lookup_series(metadata.series, metadata.publisher.sources.metron):
                self.update_series(series, metadata.series)
                if issue := self.lookup_issue(metadata.issue, metadata.series.sources.metron):
                    self.update_issue(issue, metadata.issue)
