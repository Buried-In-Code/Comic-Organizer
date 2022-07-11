import html
import re
from typing import Optional

from rich.prompt import Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata.metadata import Metadata
from dex_starr.services.league_of_comic_geeks.schemas import Comic
from dex_starr.services.league_of_comic_geeks.service import Service
from dex_starr.services.sqlite_cache import SQLiteCache


class Talker:
    def __init__(self, api_key: str, client_id: str):
        self.session = Service(api_key, client_id, cache=SQLiteCache(expiry=14))

    def _generate_search_terms(self, series_title: str, format: str, number: Optional[str] = None):
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

    def _remove_extra(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        tag_re = re.compile(r"(<!--.*?-->|<[^>]*>)")
        return " ".join(html.unescape(tag_re.sub("", value.strip())).split())

    def _search_metadata(
        self,
        title: str,
        format: str = "Comic",
        number: Optional[str] = None,
    ) -> Optional[Comic]:
        comic = None
        if number:
            search_terms = self._generate_search_terms(title, format, number)
        else:
            search_terms = (title, title)
        results_1 = [x for x in self.session.comic_list(search_terms[0]) if x.variant == 0]
        results_2 = [x for x in self.session.comic_list(search_terms[1]) if x.variant == 0]
        comic_list = sorted(
            list({x.comic_id: x for x in results_1 + results_2}.values()), key=lambda x: x.title
        )
        comic_index = create_menu(
            options=[f"{x.comic_id} | {x.title}" for x in comic_list],
            prompt="Select Comic",
            default="None of the Above",
        )
        if comic_index != 0:
            comic = self.session.comic(comic_list[comic_index - 1].comic_id)
        return comic

    def update_metadata(self, metadata: Metadata):
        comic = None
        if "League of Comic Geeks" in metadata.issue.sources:
            comic = self.session.comic(metadata.issue.sources["League of Comic Geeks"])
        if not comic:
            comic = self._search_metadata(
                metadata.series.title, metadata.issue.format, metadata.issue.number
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
        metadata.issue.characters = list(
            {
                *metadata.issue.characters,
                *[c.name for c in comic.characters],
            }
        )
        metadata.issue.cover_date = comic.details.release_date or metadata.issue.cover_date
        # TODO: Add Creators
        metadata.issue.format = comic.details.format or metadata.issue.format
        # TODO: Add Genres
        # TODO: Add Language
        # TODO: Add Locations
        # TODO: Add Number
        metadata.issue.page_count = comic.details.pages or metadata.issue.page_count
        metadata.issue.sources["League of Comic Geeks"] = comic.details.comic_id
        # TODO: Add Store Date
        # TODO: Add Story Arcs
        metadata.issue.summary = self._remove_extra(comic.details.description)
        # TODO: Add Teams
        # TODO: Add Title
