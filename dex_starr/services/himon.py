from __future__ import annotations

import html

from himon.exceptions import ServiceError
from himon.league_of_comic_geeks import LeagueofComicGeeks
from himon.schemas.comic import Comic
from himon.sqlite_cache import SQLiteCache
from rich.prompt import Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata.metadata import Metadata


class HimonTalker:
    def __init__(self, api_key: str, client_id: str):
        self.session = LeagueofComicGeeks(api_key, client_id, cache=SQLiteCache(expiry=14))

    def _generate_search_terms(self, series_title: str, format: str, number: str | None = None):
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

    def _search_metadata(
        self,
        title: str,
        format: str = "Comic",
        number: str | None = None,
        publisher_name: str | None = None,
        series_name: str | None = None,
    ) -> Comic | None:
        comic = None
        if number:
            search_terms = self._generate_search_terms(title, format, number)
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
            return self._search_metadata(
                title=title, format=format, number=number, publisher_name=publisher_name
            )
        if not comic and publisher_name:
            return self._search_metadata(title=title, format=format, number=number)
        if not comic:
            CONSOLE.print("Unable to find a matching comic", style="logging.level.warning")
        return comic

    def update_metadata(self, metadata: Metadata):
        comic = None
        if "League of Comic Geeks" in metadata.issue.sources:
            comic = self.session.comic(metadata.issue.sources["League of Comic Geeks"])
        if not comic:
            comic = self._search_metadata(
                metadata.series.title,
                metadata.issue.format,
                metadata.issue.number,
                publisher_name=metadata.publisher.title,
                series_name=metadata.series.title,
            )
        while not comic:
            search = Prompt.ask("Search Term", default="Exit", console=CONSOLE)
            if search.lower() == "exit":
                return
            comic = self._search_metadata(search)
        metadata.publisher.sources["League of Comic Geeks"] = comic.series.publisher_id
        metadata.publisher.title = comic.series.publisher_name or metadata.publisher.title
        metadata.series.sources["League of Comic Geeks"] = comic.series.series_id
        metadata.series.start_year = comic.series.year_begin or metadata.series.start_year
        metadata.series.title = comic.series.title or metadata.series.title
        metadata.series.volume = comic.series.volume or metadata.series.volume
        if comic.characters:
            metadata.issue.characters = {c.name for c in comic.characters}
        metadata.issue.cover_date = comic.release_date or metadata.issue.cover_date
        if comic.creators:
            metadata.issue.creators = {
                html.unescape(c.name): list(c.roles.values()) for c in comic.creators
            }
        metadata.issue.format = comic.format or metadata.issue.format
        # TODO: Add Genres
        # TODO: Add Language
        # TODO: Add Locations
        # TODO: Add Number
        metadata.issue.page_count = comic.page_count or metadata.issue.page_count
        metadata.issue.sources["League of Comic Geeks"] = comic.comic_id
        # TODO: Add Store Date
        # TODO: Add Story Arcs
        metadata.issue.summary = comic.description
        # TODO: Add Teams
        if not metadata.issue.title:
            metadata.issue.title = comic.title
