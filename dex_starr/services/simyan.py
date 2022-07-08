from typing import Optional

from rich.prompt import IntPrompt, Prompt
from simyan.comicvine import Comicvine
from simyan.exceptions import ServiceError
from simyan.schemas.issue import Issue as SimyanIssue
from simyan.schemas.publisher import Publisher as SimyanPublisher
from simyan.schemas.volume import Volume

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata.metadata import Issue, Metadata, Publisher, Series
from dex_starr.services.sqlite_cache import SQLiteCache


class SimyanTalker:
    def __init__(self, api_key: str):
        self.session = Comicvine(api_key=api_key, cache=SQLiteCache(expiry=14))

    def _search_issue(self, series_id: int, number: str) -> Optional[SimyanIssue]:
        _issue = None
        try:
            issue_list = self.session.issue_list({"filter": f"volume:{series_id}, number:{number}"})
        except ServiceError:
            issue_list = []
        if not issue_list:
            CONSOLE.print(f"Unable to find a issue for: {number}", style="logging.level.warning")
            return None
        issue_list = sorted(issue_list, key=lambda i: i.number)
        issue_index = create_menu(
            options=[f"{i.issue_id} | {i.volume.name} #{i.number}" for i in issue_list],
            prompt="Select Issue",
            default="None of the Above",
        )
        if issue_index != 0:
            try:
                _issue = self.session.issue(issue_list[issue_index - 1].issue_id)
            except ServiceError:
                _issue = None
        return _issue

    def _update_issue(self, issue: Issue, series_id: int):
        _issue = None
        if "Comicvine" in issue.sources:
            try:
                _issue = self.session.issue(issue.sources["Comicvine"])
            except ServiceError:
                _issue = None
        if not _issue:
            _issue = self._search_issue(series_id, issue.number)
        while not _issue:
            search = Prompt.ask("Issue number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            _issue = self._search_issue(series_id, search)
        issue.characters = {*issue.characters, *[c.name for c in _issue.characters]}
        issue.cover_date = _issue.cover_date or issue.cover_date
        # TODO: Add Creators
        issue.locations = {*issue.locations, *[x.name for x in _issue.locations]}
        issue.number = _issue.number or issue.number
        issue.sources["Comicvine"] = _issue.issue_id
        issue.store_date = _issue.store_date or issue.store_date
        issue.story_arcs = {*issue.story_arcs, *[s.name for s in _issue.story_arcs]}
        issue.summary = _issue.summary or issue.summary
        issue.teams = {*issue.teams, *[t.name for t in _issue.teams]}
        issue.title = _issue.name or issue.title

    def _search_volume(
        self, publisher_id: int, title: str, start_year: Optional[int] = None
    ) -> Optional[Volume]:
        volume = None
        try:
            volume_list = self.session.volume_list({"filter": f"name:{title}"})
        except ServiceError:
            volume_list = []
        volume_list = filter(lambda v: v.publisher_id == publisher_id, volume_list)
        if start_year:
            volume_list = filter(lambda v: v.start_year == start_year, volume_list)
        if not volume_list:
            CONSOLE.print(
                f"Unable to find a volume for: {title} ({start_year})",
                style="logging.level.warning",
            )
            return None
        volume_list = sorted(volume_list, key=lambda v: (v.name, v.start_year or 0))
        volume_index = create_menu(
            options=[f"{v.volume_id} | {v.name} ({v.start_year})" for v in volume_list],
            prompt="Select Volume",
            default="None of the Above",
        )
        if volume_index != 0:
            try:
                volume = self.session.volume(volume_list[volume_index - 1].volume_id)
            except ServiceError:
                volume = None
        if not volume and start_year:
            return self._search_volume(publisher_id, title)
        return volume

    def _update_series(self, series: Series, publisher_id: int):
        volume = None
        if "Comicvine" in series.sources:
            try:
                volume = self.session.volume(series.sources["Comicvine"])
            except ServiceError:
                volume = None
        if not volume:
            volume = self._search_volume(publisher_id, series.title, series.start_year)
        while not volume:
            search_title = Prompt.ask("Volume title", default="Exit", console=CONSOLE)
            if search_title.lower() == "exit":
                return
            search_start_year = IntPrompt.ask(
                "Volume start year", default=None, show_default=True, console=CONSOLE
            )
            volume = self._search_volume(publisher_id, search_title, search_start_year)
        series.sources["Comicvine"] = volume.volume_id
        series.start_year = volume.start_year or series.start_year
        series.title = volume.name or series.title

    def _search_publisher(self, title: str) -> Optional[SimyanPublisher]:
        _publisher = None
        try:
            publisher_list = self.session.publisher_list({"filter": f"name:{title}"})
        except ServiceError:
            publisher_list = []
        if not publisher_list:
            CONSOLE.print(f"Unable to find a publisher for: {title}", style="logging.level.warning")
            return None
        publisher_list = sorted(publisher_list, key=lambda p: p.name)
        publisher_index = create_menu(
            options=[f"{p.publisher_id} | {p.name}" for p in publisher_list],
            prompt="Select Publisher",
            default="None of the Above",
        )
        if publisher_index != 0:
            try:
                _publisher = self.session.publisher(
                    publisher_list[publisher_index - 1].publisher_id
                )
            except ServiceError:
                _publisher = None
        return _publisher

    def _update_publisher(self, publisher: Publisher):
        _publisher = None
        if "Comicvine" in publisher.sources:
            try:
                _publisher = self.session.publisher(publisher.sources["Comicvine"])
            except ServiceError:
                _publisher = None
        if not _publisher:
            _publisher = self._search_publisher(publisher.title)
        while not _publisher:
            search = Prompt.ask("Publisher title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            _publisher = self._search_publisher(search)
        publisher.sources["Comicvine"] = _publisher.publisher_id
        publisher.title = _publisher.name or publisher.title

    def update_metadata(self, metadata: Metadata):
        self._update_publisher(metadata.publisher)
        if "Comicvine" in metadata.publisher.sources:
            self._update_series(metadata.series, metadata.publisher.sources["Comicvine"])
        if "Comicvine" in metadata.series.sources:
            self._update_issue(metadata.issue, metadata.series.sources["Comicvine"])
