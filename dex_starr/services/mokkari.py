from typing import Optional

from mokkari.issue import Issue as MokkariIssue
from mokkari.publisher import Publisher as MokkariPublisher
from mokkari.series import Series as MokkariSeries
from mokkari.session import Session as Mokkari
from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata.metadata import Issue, Metadata, Publisher, Series
from dex_starr.services.sqlite_cache import SQLiteCache


class MokkariTalker:
    def __init__(self, username: str, password: str):
        self.session = Mokkari(username=username, passwd=password, cache=SQLiteCache(expiry=14))

    def _search_issue(self, series_id: int, number: str) -> Optional[MokkariIssue]:
        _issue = None
        issue_list = self.session.issues_list({"series_id": series_id, "number": number})
        if not issue_list:
            CONSOLE.print(f"Unable to find a issue for: {number}", style="logging.level.warning")
            return None
        issue_list = sorted(issue_list, key=lambda i: i.issue_name)
        issue_index = create_menu(
            options=[f"{i.id} | {i.name}" for i in issue_list],
            prompt="Select Issue",
            default="None of the Above",
        )
        if issue_index != 0:
            _issue = self.session.issue(issue_list[issue_index - 1].id)
        return _issue

    def _update_issue(self, issue: Issue, series_id: int):
        _issue = None
        if "Metron" in issue.sources:
            _issue = self.session.issue(issue.sources["Metron"])
        if not _issue:
            _issue = self._search_issue(series_id, issue.number)
        while not _issue:
            search = Prompt.ask("Issue number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            _issue = self._search_issue(series_id, search)
        issue.characters = list({*issue.characters, *[c.alias for c in _issue.characters]})
        issue.cover_date = _issue.cover_date or issue.cover_date
        # TODO: Add Creators
        issue.format = _issue.series.series_type
        if _issue.series.series_type.name == "Annual":
            issue.format = "Annual"
        elif _issue.series.series_type.name == "Trade Paperback":
            issue.format = "Trade Paperback"
        issue.format = "Comic"
        # TODO: Add Genres
        # TODO: Add Language ISO
        # TODO: Add Locations
        issue.number = _issue.number or issue.number
        issue.sources["Metron"] = _issue.id
        issue.store_date = _issue.store_date or issue.store_date
        issue.story_arcs = list({*issue.story_arcs, *[s.name for s in _issue.arcs]})
        issue.summary = _issue.desc or issue.summary
        issue.teams = list({*issue.teams, *[t.name for t in _issue.teams]})
        issue.title = _issue.issue_name or _issue.collection_title or issue.title

    def _search_series(
        self,
        publisher_id: int,
        title: str,
        volume: Optional[int] = None,
        start_year: Optional[int] = None,
    ) -> Optional[MokkariSeries]:
        _series = None
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
                _series = self.session.series(series_list[series_index - 1].id)
        if not _series and start_year:
            _series = self._search_series(publisher_id, title, volume=volume)
        if not _series and volume:
            _series = self._search_series(publisher_id, title, start_year=start_year)
        if not _series:
            CONSOLE.print(
                f"Unable to find a series for: {title} v{volume} ({start_year})",
                style="logging.level.warning",
            )
        return _series

    def _update_series(self, series: Series, publisher_id: int):
        _series = None
        if "Metron" in series.sources:
            _series = self.session.series(series.sources["Metron"])
        if not _series:
            _series = self._search_series(
                publisher_id, series.title, series.volume, series.start_year
            )
        while not _series:
            search_title = Prompt.ask("Series title", default="Exit", console=CONSOLE)
            if search_title.lower() == "exit":
                return
            search_volume = IntPrompt.ask(
                "Series volume", default=None, show_default=True, console=CONSOLE
            )
            search_start_year = IntPrompt.ask(
                "Series start year", default=None, show_default=True, console=CONSOLE
            )
            _series = self._search_series(
                publisher_id, search_title, search_volume, search_start_year
            )
        series.sources["Metron"] = _series.id
        series.start_year = _series.year_began or series.start_year
        series.title = _series.name or series.title
        series.volume = _series.volume or series.volume

    def _search_publisher(self, title: str) -> Optional[MokkariPublisher]:
        _publisher = None
        publisher_list = self.session.publishers_list({"name": title})
        if not publisher_list:
            CONSOLE.print(f"Unable to find a publisher for: {title}", style="logging.level.warning")
            return None
        publisher_list = sorted(publisher_list, key=lambda p: p.name)
        publisher_index = create_menu(
            options=[f"{p.id} | {p.name}" for p in publisher_list],
            prompt="Select Publisher",
            default="None of the Above",
        )
        if publisher_index != 0:
            _publisher = self.session.publisher(publisher_list[publisher_index - 1].id)
        return _publisher

    def _update_publisher(self, publisher: Publisher):
        _publisher = None
        if "Metron" in publisher.sources:
            _publisher = self.session.publisher(publisher.sources["Metron"])
        if not _publisher:
            _publisher = self._search_publisher(publisher.title)
        while not _publisher:
            search = Prompt.ask("Publisher title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            _publisher = self._search_publisher(search)
        publisher.sources["Metron"] = _publisher.id
        publisher.title = _publisher.name or publisher.title

    def update_metadata(self, metadata: Metadata):
        self._update_publisher(metadata.publisher)
        if "Metron" in metadata.publisher.sources:
            self._update_series(metadata.series, metadata.publisher.sources["Metron"])
        if "Metron" in metadata.series.sources:
            self._update_issue(metadata.issue, metadata.series.sources["Metron"])
