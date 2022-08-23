import re
from typing import Optional

from esak.comic import Comic
from esak.series import Series as EsakSeries
from esak.session import Session as Esak
from rich.prompt import Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata.metadata import Issue, Metadata, Series
from dex_starr.services.sqlite_cache import SQLiteCache


class EsakTalker:
    def __init__(self, public_key: str, private_key: str):
        self.session = Esak(
            public_key=public_key, private_key=private_key, cache=SQLiteCache(expiry=14)
        )

    def _clean_title(self, title: str) -> str:
        return re.sub(r"(.*)(\(.*?\))", r"\1", title).strip()

    def _search_comic(
        self, series_id: int, number: str, format: Optional[str] = None
    ) -> Optional[Comic]:
        _comic = None
        params = {"noVariants": True, "series": series_id, "issueNumber": number}
        if format in ["Trade Paperback", "Hardcover"]:
            params["format"] = format.lower()
        comic_list = self.session.comics_list(params=params)
        comic_list = sorted(comic_list, key=lambda c: c.issue_number)
        if comic_list:
            comic_index = create_menu(
                options=[
                    f"{c.id} | {self._clean_title(c.series.name)} #{c.issue_number} - {c.format}"
                    for c in comic_list
                ],
                prompt="Select Comic",
                default="None of the Above",
            )
            if comic_index != 0:
                _comic = self.session.comic(comic_list[comic_index - 1].id)
        if not _comic and format:
            return self._search_comic(series_id, number)
        if not _comic:
            CONSOLE.print("Unable to find a matching comic", style="logging.level.warning")
        return _comic

    def _update_comic(self, issue: Issue, series_id: int):
        _comic = None
        if "Marvel" in issue.sources:
            _comic = self.session.comic(issue.sources["Marvel"])
        if not _comic:
            _comic = self._search_comic(series_id, issue.number, issue.format)
        while not _comic:
            search = Prompt.ask("Comic number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            _comic = self._search_comic(series_id, search, None)
        if _comic.characters:
            issue.characters = {c.name for c in _comic.characters}
        # TODO: Cover date
        if _comic.creators:
            issue.creators = {c.name: [self._clean_title(c.role.title())] for c in _comic.creators}
        issue.format = _comic.format or issue.format
        # TODO: Genres
        # TODO: Language ISO
        # TODO: Locations
        issue.number = _comic.issue_number or issue.number
        issue.page_count = _comic.page_count or issue.page_count
        issue.sources["Marvel"] = _comic.id
        issue.store_date = _comic.dates.on_sale or issue.store_date
        if _comic.events:
            issue.story_arcs = {s.name for s in _comic.events}
        issue.summary = _comic.description or issue.summary
        # TODO: Teams
        issue.title = _comic.title = issue.title

    def _search_series(self, title: str, start_year: Optional[int] = None) -> Optional[EsakSeries]:
        _series = None
        params = {"title": title}
        if start_year:
            params["startYear"] = start_year
        series_list = self.session.series_list(params)
        series_list = sorted(series_list, key=lambda s: (s.title, s.start_year))
        if series_list:
            series_index = create_menu(
                options=[
                    f"{s.id} | {self._clean_title(s.title)} ({s.start_year})" for s in series_list
                ],
                prompt="Select Series",
                default="None of the Above",
            )
            if series_index != 0:
                _series = self.session.series(series_list[series_index - 1].id)
        if not _series and start_year:
            return self._search_series(title)
        if not series_list:
            CONSOLE.print("Unable to find a matching series", style="logging.level.warning")
        return _series

    def _update_series(self, series: Series):
        _series = None
        if "Marvel" in series.sources:
            _series = self.session.series(series.sources["Marvel"])
        if not _series:
            _series = self._search_series(series.title, series.start_year)
        while not _series:
            search = Prompt.ask("Series title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            _series = self._search_series(search)
        series.sources["Marvel"] = _series.id
        series.start_year = _series.start_year or series.start_year
        series.title = self._clean_title(_series.title) or series.title

    def update_metadata(self, metadata: Metadata):
        if not metadata.publisher.title.startswith("Marvel"):
            return
        self._update_series(metadata.series)
        if "Marvel" in metadata.series.sources:
            self._update_comic(metadata.issue, metadata.series.sources["Marvel"])
