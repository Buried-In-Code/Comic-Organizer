__all__ = ["HimonTalker"]

import html
import logging
from typing import Optional

from himon.exceptions import ServiceError
from himon.league_of_comic_geeks import LeagueofComicGeeks
from himon.schemas.comic import Comic
from himon.schemas.series import Series as HimonSeries
from rich.prompt import Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.schemas.metadata.enums import Format, Role
from dex_starr.schemas.metadata.schema import Creator, Issue, Metadata, Publisher, Series
from dex_starr.services.sqlite_cache import SQLiteCache

LOGGER = logging.getLogger(__name__)


def generate_search_terms(series_title: str, format: str, number: Optional[str] = None):
    search_1 = series_title
    if number and number != "1":
        search_1 += f" #{number}"
    search_2 = series_title
    if number and number != "1":
        if format == "Annual":
            search_2 += f" Annual #{number}"
        elif format == "Digital Chapter":
            search_2 += f" Chapter #{number}"
        elif format == "Hardcover":
            search_2 += f" Vol. {number} HC"
        elif format == "Trade Paperback":
            search_2 += f" Vol. {number} TP"
        else:
            search_2 += f" #{number}"
    return search_1, search_2


class HimonTalker:
    def __init__(self, api_key: str, client_id: str):
        self.session = LeagueofComicGeeks(api_key, client_id, cache=SQLiteCache(expiry=14))

    def update_issue(self, result: Comic, issue: Issue):
        if result.characters:
            issue.characters = sorted({x.name for x in result.characters})
        if result.release_date:
            issue.cover_date = result.release_date
        if result.creators:
            issue.creators = sorted(
                {
                    Creator(
                        name=html.unescape(x.name),
                        roles=sorted({Role.load(r) for r in x.roles.values()}),
                    )
                    for x in result.creators
                }
            )
        if result.format:
            issue.format = Format.load(result.format)
        # TODO: Genres
        # TODO: Language
        # TODO: Locations
        # TODO: Number
        if result.page_count:
            issue.page_count = result.page_count
        issue.sources.league_of_comic_geeks = result.comic_id
        # TODO: Store Date
        # TODO: Story Arcs
        if result.description:
            issue.summary = result.description
        # TODO: Teams
        if result.title:
            issue.title = result.title

    def update_series(self, result: HimonSeries, series: Series):
        series.sources.league_of_comic_geeks = result.series_id
        if result.year_begin:
            series.start_year = result.year_begin
        if result.title:
            series.title = result.title
        if result.volume:
            series.volume = result.volume

    def update_publisher(self, result: HimonSeries, publisher: Publisher):
        publisher.sources.league_of_comic_geeks = result.publisher_id
        if result.publisher_name:
            publisher.title = result.publisher_name

    def _search_comic(
        self,
        title: str,
        format: str = "Comic",
        number: Optional[str] = None,
        publisher_name: Optional[str] = None,
        series_name: Optional[str] = None,
    ) -> Optional[Comic]:
        output = None
        if number:
            search_terms = generate_search_terms(title, format, number)
        else:
            search_terms = (title, title)
        try:
            results_1 = [x for x in self.session.search(search_terms[0]) if not x.is_variant]
        except ServiceError:
            results_1 = []
        try:
            results_2 = [x for x in self.session.search(search_terms[1]) if not x.is_variant]
        except ServiceError:
            results_2 = []
        comic_list = list({x.comic_id: x for x in results_1 + results_2}.values())
        if publisher_name is not None:
            comic_list = [x for x in comic_list if x.publisher_name == publisher_name]
        if series_name is not None:
            comic_list = [x for x in comic_list if x.series_name == series_name]
        if comic_list := sorted(
            comic_list,
            key=lambda x: (x.publisher_name, x.series_name, x.series_volume or 1, x.title),
        ):
            comic_index = create_menu(
                options=[
                    f"{x.comic_id} | {x.publisher_name} | {x.series_name} v{x.series_volume or 1} "
                    f"| {x.title}"
                    for x in comic_list
                ],
                prompt="Select Comic",
                default="None of the Above",
            )
            if comic_index != 0:
                return self.session.comic(comic_list[comic_index - 1].comic_id)
        if not output and series_name:
            return self._search_comic(
                title=title, format=format, number=number, publisher_name=publisher_name
            )
        if not output and publisher_name:
            return self._search_comic(title=title, format=format, number=number)
        if not output:
            LOGGER.warning("Unable to find a matching comic")
        return output

    def lookup_comic(self, metadata: Metadata) -> Optional[Comic]:
        output = None
        if metadata.issue.sources.league_of_comic_geeks:
            try:
                output = self.session.comic(metadata.issue.sources.league_of_comic_geeks)
            except ServiceError:
                output = None
        if not output:
            output = self._search_comic(
                metadata.series.title,
                str(metadata.issue.format),
                metadata.issue.number,
                publisher_name=metadata.publisher.title,
                series_name=metadata.series.title,
            )
        while not output:
            search = Prompt.ask("Search Term", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            output = self._search_comic(search)
        return output

    def update_metadata(self, metadata: Metadata):
        if comic := self.lookup_comic(metadata):
            self.update_publisher(comic.series, metadata.publisher)
            self.update_series(comic.series, metadata.series)
            self.update_issue(comic, metadata.issue)
