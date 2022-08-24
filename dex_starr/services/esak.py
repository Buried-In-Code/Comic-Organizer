__all__ = ["EsakTalker"]

import re
from typing import Optional

from esak.comic import Comic
from esak.series import Series as EsakSeries
from esak.session import Session as Esak
from rich.prompt import Prompt

from ..console import CONSOLE, create_menu
from ..metadata.metadata import Creator, Issue, Metadata, Series, StoryArc
from .sqlite_cache import SQLiteCache


def clean_title(title: str) -> str:
    return re.sub(r"(.*)(\(.*?\))", r"\1", title).strip()


class EsakTalker:
    def __init__(self, public_key: str, private_key: str):
        self.session = Esak(
            public_key=public_key, private_key=private_key, cache=SQLiteCache(expiry=14)
        )

    def update_issue(self, esak_comic: Comic, issue: Issue):
        issue.characters = sorted({*issue.characters, *[x.name for x in esak_comic.characters]})
        # Cover date
        # region Set Creators
        for esak_creator in esak_comic.creators:
            found = False
            for creator in issue.creators:
                if esak_creator.name == creator.name:
                    found = True
                    creator.roles = sorted({*creator.roles, clean_title(esak_creator.role.title())})
            if not found:
                issue.creators.append(
                    Creator(
                        name=esak_creator.name,
                        roles=[clean_title(esak_creator.role.title())],
                    )
                )
        # endregion
        issue.format = esak_comic.format or issue.format
        # Genres
        # Language
        # Locations
        issue.number = esak_comic.issue_number or issue.number
        issue.page_count = esak_comic.page_count or issue.page_count
        issue.sources["Marvel"] = esak_comic.id
        issue.store_date = esak_comic.dates.on_sale or issue.store_date
        # region Set Story Arcs
        for esak_event in esak_comic.events:
            found = False
            for story_arc in issue.story_arcs:
                if esak_event.name == story_arc.title:
                    found = True
            if not found:
                issue.story_arcs.append(StoryArc(title=esak_event.name))
        issue.story_arcs.sort()
        # endregion
        issue.summary = esak_comic.description or issue.summary
        # Teams
        issue.title = esak_comic.title = issue.title

    def _search_comic(
        self, series_id: int, number: str, format: Optional[str] = None
    ) -> Optional[Comic]:
        esak_comic = None
        params = {"noVariants": True, "series": series_id, "issueNumber": number}
        if format in ["Trade Paperback", "Hardcover"]:
            params["format"] = format.lower()
        comic_list = self.session.comics_list(params=params)
        comic_list = sorted(comic_list, key=lambda c: c.issue_number)
        if comic_list:
            comic_index = create_menu(
                options=[
                    f"{c.id} | {clean_title(c.series.name)} #{c.issue_number} - {c.format}"
                    for c in comic_list
                ],
                prompt="Select Comic",
                default="None of the Above",
            )
            if comic_index != 0:
                esak_comic = self.session.comic(comic_list[comic_index - 1].id)
        if not esak_comic and format:
            return self._search_comic(series_id, number)
        if not esak_comic:
            CONSOLE.print("Unable to find a matching comic", style="logging.level.warning")
        return esak_comic

    def lookup_comic(self, issue: Issue, series_id: int) -> Optional[Comic]:
        esak_comic = None
        if "Marvel" in issue.sources:
            esak_comic = self.session.comic(issue.sources["Marvel"])
        if not esak_comic:
            esak_comic = self._search_comic(series_id, issue.number, issue.format)
        while not esak_comic:
            search = Prompt.ask("Comic number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            esak_comic = self._search_comic(series_id, search, None)
        return esak_comic

    def update_series(self, esak_series: EsakSeries, series: Series):
        series.sources["Marvel"] = esak_series.id
        series.start_year = esak_series.start_year or series.start_year
        series.title = clean_title(esak_series.title) or series.title

    def _search_series(self, title: str, start_year: Optional[int] = None) -> Optional[EsakSeries]:
        esak_series = None
        params = {"title": title}
        if start_year:
            params["startYear"] = start_year
        series_list = self.session.series_list(params)
        series_list = sorted(series_list, key=lambda s: (s.title, s.start_year))
        if series_list:
            series_index = create_menu(
                options=[f"{s.id} | {clean_title(s.title)} ({s.start_year})" for s in series_list],
                prompt="Select Series",
                default="None of the Above",
            )
            if series_index != 0:
                esak_series = self.session.series(series_list[series_index - 1].id)
        if not esak_series and start_year:
            return self._search_series(title)
        if not series_list:
            CONSOLE.print("Unable to find a matching series", style="logging.level.warning")
        return esak_series

    def lookup_series(self, series: Series) -> Optional[EsakSeries]:
        esak_series = None
        if "Marvel" in series.sources:
            esak_series = self.session.series(series.sources["Marvel`"])
        if not esak_series:
            esak_series = self._search_series(series.title, series.start_year)
        while not esak_series:
            search = Prompt.ask("Series title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            esak_series = self._search_series(search)
        return esak_series

    def update_metadata(self, metadata: Metadata):
        if not metadata.publisher.title.startswith("Marvel"):
            return
        esak_series = self.lookup_series(metadata.series)
        if esak_series:
            self.update_series(esak_series, metadata.series)
            esak_comic = self.lookup_comic(metadata.issue, metadata.series.sources["Marvel"])
            if esak_comic:
                self.update_issue(esak_comic, metadata.issue)
