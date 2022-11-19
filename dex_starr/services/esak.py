__all__ = ["EsakTalker"]

import re
from typing import Optional

from esak.comic import Comic
from esak.exceptions import ApiError
from esak.series import Series as EsakSeries
from esak.session import Session as Esak
from rich.prompt import Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.schemas.metadata.enums import Format, Role
from dex_starr.schemas.metadata.schema import Creator, Issue, Metadata, Series, StoryArc
from dex_starr.services.sqlite_cache import SQLiteCache


def clean_title(title: str) -> str:
    return re.sub(r"(.*)(\(.*?\))", r"\1", title).strip()


class EsakTalker:
    def __init__(self, public_key: str, private_key: str):
        self.session = Esak(
            public_key=public_key, private_key=private_key, cache=SQLiteCache(expiry=14)
        )

    def update_issue(self, result: Comic, issue: Issue):
        if result.characters:
            issue.characters = sorted({x.name for x in result.characters})
        # TODO: Cover date
        if result.creators:
            issue.creators = sorted(
                {
                    Creator(name=x.name, roles=[Role.load(clean_title(x.role.title()))])
                    for x in result.creators
                }
            )
        if result.format:
            issue.format = Format.load(result.format)
        # TODO: Genres
        # TODO: Language
        # TODO: Locations
        if result.issue_number:
            issue.number = result.issue_number
        if result.page_count:
            issue.page_count = result.page_count
        issue.sources.marvel = result.id
        if result.dates.on_sale:
            issue.store_date = result.dates.on_sale
        if result.events:
            issue.story_arcs = sorted({StoryArc(title=x.name) for x in result.events})
        if result.description:
            issue.summary = result.description
        # TODO: Teams
        if result.title:
            issue.title = result.title

    def _search_comic(
        self, series_id: int, number: str, format: Optional[str] = None
    ) -> Optional[Comic]:
        CONSOLE.print(
            f"Searching for: {series_id=}, {number=}, {format=}", style="logging.level.debug"
        )
        output = None
        params = {"noVariants": True, "series": series_id, "issueNumber": number}
        if format in ["Trade Paperback", "Hardcover"]:
            params["format"] = format.lower()
        try:
            comic_list = self.session.comics_list(params=params)
        except ApiError:
            comic_list = []
        if comic_list := sorted(comic_list, key=lambda c: c.issue_number):
            comic_index = create_menu(
                options=[
                    f"{c.id} | {clean_title(c.series.name)} #{c.issue_number} - {c.format}"
                    for c in comic_list
                ],
                prompt="Select Comic",
                default="None of the Above",
            )
            if comic_index != 0:
                try:
                    output = self.session.comic(comic_list[comic_index - 1].id)
                except ApiError:
                    CONSOLE.print(
                        f"Unable to find comic: comic_id={comic_list[comic_index - 1].id}",
                        style="logging.level.warning",
                    )
                    output = None
        else:
            CONSOLE.print(
                f"Unable to find comic: {series_id=}, {number=}, {format=}",
                style="logging.level.info",
            )
        if not output and format:
            return self._search_comic(series_id, number)
        return output

    def lookup_comic(self, issue: Issue, series_id: int) -> Optional[Comic]:
        output = None
        if issue.sources.marvel:
            try:
                output = self.session.comic(issue.sources.marvel)
            except ApiError:
                CONSOLE.print(
                    f"Unable to find comic: comic_id={issue.sources.marvel}",
                    style="logging.level.warning",
                )
                output = None
        if not output:
            output = self._search_comic(series_id, issue.number, str(issue.format))
        while not output:
            search = Prompt.ask("Comic number", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            output = self._search_comic(series_id, search, None)
        return output

    def update_series(self, result: EsakSeries, series: Series):
        series.sources.marvel = result.id
        if result.start_year:
            series.start_year = result.start_year
        if result.title:
            series.title = clean_title(result.title)

    def _search_series(self, title: str, start_year: Optional[int] = None) -> Optional[EsakSeries]:
        CONSOLE.print(f"Searching for: {title=}, {start_year=}", style="logging.level.debug")
        output = None
        params = {"title": title}
        if start_year:
            params["startYear"] = start_year
        try:
            series_list = self.session.series_list(params)
        except ApiError:
            series_list = []
        if series_list := sorted(series_list, key=lambda s: (s.title, s.start_year)):
            series_index = create_menu(
                options=[f"{s.id} | {clean_title(s.title)} ({s.start_year})" for s in series_list],
                prompt="Select Series",
                default="None of the Above",
            )
            if series_index != 0:
                try:
                    output = self.session.series(series_list[series_index - 1].id)
                except ApiError:
                    CONSOLE.print(
                        f"Unable to find series: series_id={series_list[series_index - 1].id}",
                        style="logging.level.warning",
                    )
                    output = None
        else:
            CONSOLE.print(
                f"Unable to find series: {title=}, {start_year=}",
                style="logging.level.info",
            )
        if not output and start_year:
            return self._search_series(title)
        return output

    def lookup_series(self, series: Series) -> Optional[EsakSeries]:
        output = None
        if series.sources.marvel:
            try:
                output = self.session.series(series.sources.marvel)
            except ApiError:
                CONSOLE.print(
                    f"Unable to find series: series_id={series.sources.marvel}",
                    style="logging.level.warning",
                )
                output = None
        if not output:
            output = self._search_series(series.title, series.start_year)
        while not output:
            search = Prompt.ask("Series title", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return None
            output = self._search_series(search)
        return output

    def update_metadata(self, metadata: Metadata):
        if not metadata.publisher.title.startswith("Marvel"):
            return
        if series := self.lookup_series(metadata.series):
            self.update_series(series, metadata.series)
            if comic := self.lookup_comic(metadata.issue, metadata.series.sources.marvel):
                self.update_issue(comic, metadata.issue)
