__all__ = ["MokkariTalker"]

import html
from typing import Optional

from mokkari.issue import Issue as MokkariIssue
from mokkari.publisher import Publisher as MokkariPublisher
from mokkari.series import Series as MokkariSeries
from mokkari.session import Session as Mokkari
from rich.prompt import Prompt

from ..console import CONSOLE, create_menu
from ..metadata.metadata import Creator, Issue, Metadata, Publisher, Series, StoryArc
from .sqlite_cache import SQLiteCache


class MokkariTalker:
    def __init__(self, username: str, password: str):
        self.session = Mokkari(username=username, passwd=password, cache=SQLiteCache(expiry=14))

    def update_issue(self, mokkari_issue: MokkariIssue, issue: Issue):
        issue.characters = sorted({*issue.characters, *[x.name for x in mokkari_issue.characters]})
        issue.cover_date = mokkari_issue.cover_date or issue.cover_date
        # region Set Creators
        for credit in mokkari_issue.credits:
            name = html.unescape(credit.creator)
            found = False
            for creator in issue.creators:
                if name == creator.name:
                    found = True
                    creator.roles = sorted({*creator.roles, *[x.name for x in credit.role]})
            if not found:
                issue.creators.append(
                    Creator(
                        name=name,
                        roles=sorted(x.name for x in credit.role),
                    )
                )
        # endregion
        format_name = mokkari_issue.series.series_type or issue.format
        if format_name in ["Annual", "Trade Paperback"]:
            issue.format = format_name
        else:
            issue.format = "Comic"
        issue.genres = sorted({*issue.genres, *[x.name for x in mokkari_issue.series.genres]})
        # TODO: Add Language
        # Locations
        issue.number = mokkari_issue.number or issue.number
        issue.sources["Metron"] = mokkari_issue.id
        issue.store_date = mokkari_issue.store_date or issue.store_date
        # region Set Story Arcs
        for arc in mokkari_issue.arcs:
            found = False
            for story_arc in issue.story_arcs:
                if arc.name == story_arc.title:
                    found = True
            if not found:
                issue.story_arcs.append(StoryArc(title=arc.name))
        issue.story_arcs.sort()
        # endregion
        issue.summary = mokkari_issue.desc or issue.summary
        issue.teams = sorted({*issue.teams, *[x.name for x in mokkari_issue.teams]})
        issue.title = mokkari_issue.collection_title or issue.title

    def _search_issue(self, series_id: int, number: str) -> Optional[MokkariIssue]:
        mokkari_issue = None
        issue_list = self.session.issues_list({"series_id": series_id, "number": number})
        if not issue_list:
            CONSOLE.print("Unable to find a matching issue", style="logging.level.warning")
            return None
        issue_list = sorted(issue_list, key=lambda i: i.issue_name)
        issue_index = create_menu(
            options=[f"{i.id} | {i.issue_name or i.collection_title}" for i in issue_list],
            prompt="Select Issue",
            default="None of the Above",
        )
        if issue_index != 0:
            mokkari_issue = self.session.issue(issue_list[issue_index - 1].id)
        return mokkari_issue

    def lookup_issue(self, issue: Issue, series_id: int) -> Optional[MokkariIssue]:
        mokkari_issue = None
        if "Metron" in issue.sources:
            mokkari_issue = self.session.issue(issue.sources["Metron"])
        if not mokkari_issue:
            mokkari_issue = self._search_issue(series_id, issue.number)
        while not mokkari_issue:
            search = Prompt.ask("Issue number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            mokkari_issue = self._search_issue(series_id, search)
        return mokkari_issue

    def update_series(self, mokkari_series: MokkariSeries, series: Series):
        series.sources["Metron"] = mokkari_series.id
        series.start_year = mokkari_series.year_began or series.start_year
        series.title = mokkari_series.name or series.title
        series.volume = mokkari_series.volume or series.volume

    def _search_series(
        self,
        publisher_id: int,
        title: str,
        volume: Optional[int] = None,
        start_year: Optional[int] = None,
    ) -> Optional[MokkariSeries]:
        mokkari_series = None
        params = {"publisher_id": publisher_id, "name": title}
        if volume:
            params["volume"] = volume
        if start_year:
            params["start_year"] = start_year
        series_list = self.session.series_list(params)
        if series_list:
            series_list = sorted(series_list, key=lambda s: s.display_name)
            series_index = create_menu(
                options=[f"{s.id} | {s.display_name}" for s in series_list],
                prompt="Select Series",
                default="None of the Above",
            )
            if series_index != 0:
                mokkari_series = self.session.series(series_list[series_index - 1].id)
        if not mokkari_series and start_year:
            return self._search_series(publisher_id, title, volume=volume)
        if not mokkari_series and volume:
            return self._search_series(publisher_id, title, start_year=start_year)
        if not mokkari_series:
            CONSOLE.print("Unable to find a matching series", style="logging.level.warning")
        return mokkari_series

    def lookup_series(self, series: Series, publisher_id: int) -> Optional[MokkariSeries]:
        mokkari_series = None
        if "Metron" in series.sources:
            mokkari_series = self.session.series(series.sources["Metron"])
        if not mokkari_series:
            mokkari_series = self._search_series(
                publisher_id, series.title, series.volume, series.start_year
            )
        while not mokkari_series:
            search = Prompt.ask("Series title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            mokkari_series = self._search_series(publisher_id, search)
        return mokkari_series

    def update_publisher(self, mokkari_publisher: MokkariPublisher, publisher: Publisher):
        publisher.sources["Metron"] = mokkari_publisher.id
        publisher.title = mokkari_publisher.name or publisher.title

    def _search_publisher(self, title: str) -> Optional[MokkariPublisher]:
        mokkari_publisher = None
        publisher_list = self.session.publishers_list({"name": title})
        if not publisher_list:
            CONSOLE.print("Unable to find a matching publisher", style="logging.level.warning")
            return None
        publisher_list = sorted(publisher_list, key=lambda p: p.name)
        publisher_index = create_menu(
            options=[f"{p.id} | {p.name}" for p in publisher_list],
            prompt="Select Publisher",
            default="None of the Above",
        )
        if publisher_index != 0:
            mokkari_publisher = self.session.publisher(publisher_list[publisher_index - 1].id)
        return mokkari_publisher

    def lookup_publisher(self, publisher: Publisher) -> Optional[MokkariPublisher]:
        mokkari_publisher = None
        if "Metron" in publisher.sources:
            mokkari_publisher = self.session.publisher(publisher.sources["Metron"])
        if not mokkari_publisher:
            mokkari_publisher = self._search_publisher(publisher.title)
        while not mokkari_publisher:
            search = Prompt.ask("Publisher title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            mokkari_publisher = self._search_publisher(search)
        return mokkari_publisher

    def update_metadata(self, metadata: Metadata):
        if mokkari_publisher := self.lookup_publisher(metadata.publisher):
            self.update_publisher(mokkari_publisher, metadata.publisher)
            if mokkari_series := self.lookup_series(
                metadata.series, metadata.publisher.sources["Metron"]
            ):
                self.update_series(mokkari_series, metadata.series)
                if mokkari_issue := self.lookup_issue(
                    metadata.issue, metadata.series.sources["Metron"]
                ):
                    self.update_issue(mokkari_issue, metadata.issue)
