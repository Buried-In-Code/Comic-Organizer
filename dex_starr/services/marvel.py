__all__ = ["EsakTalker"]

import re
from typing import Optional

from esak.comic import Comic
from esak.exceptions import ApiError
from esak.series import Series as EsakSeries
from esak.session import Session as Esak
from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.models.metadata.enums import Format, Role, Source
from dex_starr.models.metadata.schema import Creator, Issue, Metadata, Resource, Series, StoryArc
from dex_starr.services.sqlite_cache import SQLiteCache
from dex_starr.settings import MarvelSettings


def clean_title(title: str) -> str:
    return re.sub(r"(.*)(\(.*?\))", r"\1", title).strip()


class EsakTalker:
    def __init__(self, settings: MarvelSettings):
        self.session = Esak(
            public_key=settings.public_key,
            private_key=settings.private_key,
            cache=SQLiteCache(expiry=14),
        )

    def update_issue(self, result: Comic, issue: Issue):
        if result.characters:
            issue.characters = sorted({x.name for x in result.characters}, alg=ns.NA | ns.G)
        # TODO: Cover date
        if result.creators:
            issue.creators = sorted(
                {
                    Creator(name=x.name, roles=[Role.load(clean_title(x.role.title()))])
                    for x in result.creators
                },
                alg=ns.NA | ns.G,
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
        issue.resources = sorted(
            {Resource(source=Source.MARVEL, value=result.id), *issue.resources}, alg=ns.NA | ns.G
        )
        if result.dates.on_sale:
            issue.store_date = result.dates.on_sale
        if result.events:
            issue.story_arcs = sorted(
                {StoryArc(title=x.name) for x in result.events}, alg=ns.NA | ns.G
            )
        if result.description:
            issue.summary = result.description
        # TODO: Teams
        if result.title:
            issue.title = result.title

    def _select_comic(self, comic_id: int) -> Optional[Comic]:
        CONSOLE.print(f"Getting Comic: {comic_id=}", style="logging.level.debug")
        try:
            return self.session.comic(comic_id)
        except ApiError:
            CONSOLE.print(f"Unable to get Comic: {comic_id=}", style="logging.level.warning")
        return None

    def _search_comic(self, series_id: int, number: str) -> Optional[Comic]:
        CONSOLE.print(f"Searching for Comic: {series_id=}, {number=}", style="logging.level.debug")
        output = None
        params = {"noVariants": True, "series": series_id, "issueNumber": number}
        try:
            comic_list = self.session.comics_list(params=params)
        except ApiError:
            comic_list = []
        if comic_list := sorted(comic_list, key=lambda c: c.issue_number, alg=ns.NA | ns.G):
            comic_index = create_menu(
                options=[
                    f"{c.id} | {clean_title(c.series.name)} #{c.issue_number} - {c.format}"
                    for c in comic_list
                ],
                prompt="Select Comic",
                default="None of the Above",
            )
            if comic_index != 0:
                output = self._select_comic(comic_list[comic_index - 1].id)
        return output

    def lookup_comic(self, issue: Issue, series_id: int) -> Optional[Comic]:
        output = None
        source_list = [x.source for x in issue.resources]
        if Source.MARVEL in source_list:
            index = source_list.index(Source.MARVEL)
            output = self._select_comic(issue.resources[index].value)
        if not output:
            output = self._search_comic(series_id, issue.number)
        while not output:
            index = create_menu(
                options=["Enter Comic id", "Enter Comic number"], prompt="Select", default="Exit"
            )
            if index == 0:
                return
            elif index == 1:
                comic_id = IntPrompt.ask("Comic id", console=CONSOLE)
                output = self._select_comic(comic_id)
            else:
                comic_number = Prompt.ask("Comic number", console=CONSOLE)
                output = self._search_comic(series_id, comic_number)
        return output

    def update_series(self, result: EsakSeries, series: Series):
        series.resources = sorted(
            {Resource(source=Source.MARVEL, value=result.id), *series.resources}, alg=ns.NA | ns.G
        )
        if result.start_year:
            series.start_year = result.start_year
        if result.title:
            series.title = clean_title(result.title)

    def _select_series(self, series_id: int) -> Optional[EsakSeries]:
        CONSOLE.print(f"Getting Series: {series_id=}", style="logging.level.debug")
        try:
            return self.session.series(series_id)
        except ApiError:
            CONSOLE.print(f"Unable to get Series: {series_id=}", style="logging.level.warning")
        return None

    def _search_series(self, title: str, start_year: Optional[int] = None) -> Optional[EsakSeries]:
        CONSOLE.print(f"Searching for Series: {title=}, {start_year=}", style="logging.level.debug")
        output = None
        params = {"title": title}
        if start_year:
            params["startYear"] = start_year
        try:
            series_list = self.session.series_list(params)
        except ApiError:
            series_list = []
        if series_list := sorted(
            series_list, key=lambda s: (s.title, s.start_year), alg=ns.NA | ns.G
        ):
            series_index = create_menu(
                options=[f"{s.id} | {clean_title(s.title)} ({s.start_year})" for s in series_list],
                prompt="Select Series",
                default="None of the Above",
            )
            if series_index != 0:
                output = self._select_series(series_list[series_index - 1].id)
        if not output and start_year:
            return self._search_series(title)
        return output

    def lookup_series(self, series: Series) -> Optional[EsakSeries]:
        output = None
        source_list = [x.source for x in series.resources]
        if Source.MARVEL in source_list:
            index = source_list.index(Source.MARVEL)
            output = self._select_series(series.resources[index].value)
        if not output:
            output = self._search_series(series.title, series.start_year)
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
                output = self._search_series(series_title)
        return output

    def update_metadata(self, metadata: Metadata):
        if not metadata.publisher.title.startswith("Marvel"):
            return
        if series := self.lookup_series(metadata.series):
            self.update_series(series, metadata.series)
            if comic := self.lookup_comic(metadata.issue, series.id):
                self.update_issue(comic, metadata.issue)
