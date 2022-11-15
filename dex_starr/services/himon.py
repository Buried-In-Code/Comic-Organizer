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
from dex_starr.schemas.metadata import Creator, Issue, Metadata, Publisher, Series
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

    def update_issue(self, himon_comic: Comic, issue: Issue):
        issue.characters = sorted({*issue.characters, *[x.name for x in himon_comic.characters]})
        issue.cover_date = himon_comic.release_date or issue.cover_date
        # region Set Creators
        for himon_creator in himon_comic.creators:
            name = html.unescape(himon_creator.name)
            found = False
            for creator in issue.creators:
                if name == creator.name:
                    found = True
                    creator.roles = sorted({*creator.roles, *himon_creator.roles.values()})
            if not found:
                issue.creators.append(
                    Creator(
                        name=name,
                        roles=sorted(himon_creator.roles.values()),
                    )
                )
        # endregion
        issue.format = himon_comic.format or issue.format
        # Genres
        # Language
        # Locations
        # Number
        issue.page_count = himon_comic.page_count or issue.page_count
        issue.sources["League of Comic Geeks"] = himon_comic.comic_id
        # Store Date
        # Story Arcs
        issue.summary = himon_comic.description
        # Teams
        issue.title = issue.title or himon_comic.title

    def update_series(self, himon_series: HimonSeries, series: Series):
        series.sources["League of Comic Geeks"] = himon_series.series_id
        series.start_year = himon_series.year_begin or series.start_year
        series.title = himon_series.title or series.title
        series.volume = himon_series.volume or series.volume

    def update_publisher(self, himon_series: HimonSeries, publisher: Publisher):
        publisher.sources["League of Comic Geeks"] = himon_series.publisher_id
        publisher.title = himon_series.publisher_name or publisher.title

    def _search_comic(
        self,
        title: str,
        format: str = "Comic",
        number: Optional[str] = None,
        publisher_name: Optional[str] = None,
        series_name: Optional[str] = None,
    ) -> Optional[Comic]:
        comic = None
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
        comic_list = sorted(
            comic_list,
            key=lambda x: (x.publisher_name, x.series_name, x.series_volume or 1, x.title),
        )
        if comic_list:
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
        if not comic and series_name:
            return self._search_comic(
                title=title, format=format, number=number, publisher_name=publisher_name
            )
        if not comic and publisher_name:
            return self._search_comic(title=title, format=format, number=number)
        if not comic:
            LOGGER.warning("Unable to find a matching comic")
        return comic

    def lookup_comic(self, metadata: Metadata) -> Optional[Comic]:
        himon_comic = None
        if "League of Comic Geeks" in metadata.issue.sources:
            himon_comic = self.session.comic(metadata.issue.sources["League of Comic Geeks"])
        if not himon_comic:
            himon_comic = self._search_comic(
                metadata.series.title,
                metadata.issue.format,
                metadata.issue.number,
                publisher_name=metadata.publisher.title,
                series_name=metadata.series.title,
            )
        while not himon_comic:
            search = Prompt.ask("Search Term", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            himon_comic = self._search_comic(search)
        return himon_comic

    def update_metadata(self, metadata: Metadata):
        himon_comic = self.lookup_comic(metadata)
        if himon_comic:
            self.update_publisher(himon_comic.series, metadata.publisher)
            self.update_series(himon_comic.series, metadata.series)
            self.update_issue(himon_comic, metadata.issue)
