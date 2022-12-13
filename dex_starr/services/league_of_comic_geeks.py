__all__ = ["HimonTalker"]

import html
from typing import List, Optional, Tuple

from himon.exceptions import ServiceError
from himon.league_of_comic_geeks import LeagueofComicGeeks
from himon.schemas.comic import Comic
from himon.schemas.series import Series as HimonSeries
from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.models.metadata.enums import Format, Role, Source
from dex_starr.models.metadata.schema import Creator, Issue, Metadata, Publisher, Resource, Series
from dex_starr.services.sqlite_cache import SQLiteCache
from dex_starr.settings import LeagueOfComicGeeksSettings


def generate_search_terms(
    series_title: str, number: Optional[str] = None
) -> Tuple[str, Optional[str], Optional[str], Optional[str], Optional[str]]:
    if not number or number == "1":
        return series_title, None, None, None, None
    comic_search = f"{series_title} #{number}"
    annual_search = f"{series_title} Annual #{number}"
    digital_search = f"{series_title} Chapter #{number}"
    hardcover_search = f"{series_title} Vol. {number} HC"
    trade_search = f"{series_title} Vol. {number} TP"
    return comic_search, annual_search, digital_search, hardcover_search, trade_search


class HimonTalker:
    def __init__(self, settings: LeagueOfComicGeeksSettings):
        self.session = LeagueofComicGeeks(
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            access_token=settings.access_token,
            cache=SQLiteCache(expiry=14),
        )
        if not settings.access_token:
            CONSOLE.print("Generating new access token", style="logging.level.info")
            self.session.access_token = settings.access_token = self.session.generate_access_token()

    def update_issue(self, result: Comic, issue: Issue):
        if result.characters:
            issue.characters = sorted({x.name for x in result.characters}, alg=ns.NA | ns.G)
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
                },
                alg=ns.NA | ns.G,
            )
        if result.format:
            issue.format = Format.load(result.format)
        # TODO: Genres
        # TODO: Language
        # TODO: Locations
        # TODO: Number
        if result.page_count:
            issue.page_count = result.page_count
        issue.resources = sorted(
            {
                Resource(source=Source.LEAGUE_OF_COMIC_GEEKS, value=result.comic_id),
                *issue.resources,
            },
            alg=ns.NA | ns.G,
        )
        # TODO: Store Date
        # TODO: Story Arcs
        if result.description:
            issue.summary = result.description
        # TODO: Teams
        if result.title:
            issue.title = result.title  # TODO: Parse out duplicate data

    def update_series(self, result: HimonSeries, series: Series):
        series.resources = sorted(
            {
                Resource(source=Source.LEAGUE_OF_COMIC_GEEKS, value=result.series_id),
                *series.resources,
            },
            alg=ns.NA | ns.G,
        )
        if result.year_begin:
            series.start_year = result.year_begin
        if result.title:
            series.title = result.title
        if result.volume:
            series.volume = result.volume

    def update_publisher(self, result: HimonSeries, publisher: Publisher):
        publisher.resources = sorted(
            {
                Resource(source=Source.LEAGUE_OF_COMIC_GEEKS, value=result.publisher_id),
                *publisher.resources,
            },
            alg=ns.NA | ns.G,
        )
        if result.publisher_name:
            publisher.title = result.publisher_name

    def _filter_format(self, results: List[Comic]) -> List[Comic]:
        format_list = sorted({x.format for x in results}, alg=ns.NA | ns.G)
        if len(format_list) == 1:
            return results
        index = create_menu(
            options=format_list, prompt="Filter by format", default="None of the Above"
        )
        if index == 0:
            return results
        return [x for x in results if x.format == format_list[index - 1]]

    def _filter_series(self, results: List[Comic]) -> List[Comic]:
        series_list = sorted({x.series_name for x in results}, alg=ns.NA | ns.G)
        if len(series_list) == 1:
            return results
        index = create_menu(
            options=series_list, prompt="Filter by series", default="None of the Above"
        )
        if index == 0:
            return results
        return [x for x in results if x.series_name == series_list[index - 1]]

    def _filter_publisher(self, results: List[Comic]) -> List[Comic]:
        publisher_list = sorted({x.publisher_name for x in results}, alg=ns.NA | ns.G)
        if len(publisher_list) == 1:
            return results
        index = create_menu(
            options=publisher_list, prompt="Filter by publisher", default="None of the above"
        )
        if index == 0:
            return results
        return [x for x in results if x.publisher_name == publisher_list[index - 1]]

    def _select_comic(self, comic_id: int) -> Optional[Comic]:
        CONSOLE.print(f"Getting Comic: {comic_id=}", style="logging.level.debug")
        try:
            return self.session.comic(comic_id)
        except ServiceError:
            CONSOLE.print(f"Unable to get Comic: {comic_id=}", style="logging.level.warning")
        return None

    def _search_comic(
        self,
        title: str,
        number: Optional[str] = None,
    ) -> Optional[Comic]:
        CONSOLE.print(f"Searching for Comic: {title=}, {number=}", style="logging.level.debug")
        output = None
        results = []
        for search_term in generate_search_terms(title, number):
            if not search_term:
                continue
            try:
                results.extend(x for x in self.session.search(search_term) if not x.is_variant)
            except ServiceError:
                pass
        comic_list = list({x.comic_id: x for x in results}.values())
        comic_list = self._filter_publisher(results=comic_list)
        comic_list = self._filter_series(results=comic_list)
        comic_list = self._filter_format(results=comic_list)
        if comic_list := sorted(
            comic_list,
            key=lambda x: (x.publisher_name, x.series_name, x.series_volume or 1, x.title),
            alg=ns.NA | ns.G,
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
                output = self._select_comic(comic_list[comic_index - 1].comic_id)
        return output

    def lookup_comic(self, metadata: Metadata) -> Optional[Comic]:
        output = None
        source_list = [x.source for x in metadata.issue.resources]
        if Source.LEAGUE_OF_COMIC_GEEKS in source_list:
            index = source_list.index(Source.LEAGUE_OF_COMIC_GEEKS)
            output = self._select_comic(metadata.issue.resources[index].value)
        if not output:
            output = self._search_comic(metadata.series.title, metadata.issue.number)
        while not output:
            index = create_menu(
                options=["Enter Comic id", "Enter Search term"], prompt="Select", default="Exit"
            )
            if index == 0:
                return
            elif index == 1:
                comic_id = IntPrompt.ask("Comic id", console=CONSOLE)
                output = self._select_comic(comic_id)
            else:
                search = Prompt.ask("Search Term", console=CONSOLE)
                output = self._search_comic(search)
        return output

    def update_metadata(self, metadata: Metadata):
        if comic := self.lookup_comic(metadata):
            self.update_publisher(comic.series, metadata.publisher)
            self.update_series(comic.series, metadata.series)
            self.update_issue(comic, metadata.issue)
