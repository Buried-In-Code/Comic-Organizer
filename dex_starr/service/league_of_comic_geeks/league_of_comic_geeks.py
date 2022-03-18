import html
import re
from typing import Any, Dict, Optional, Tuple

from rich.prompt import Prompt
from simyan.sqlite_cache import SQLiteCache

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata import FormatEnum, Identifier, Metadata
from dex_starr.service.league_of_comic_geeks.session import Session as LeagueOfComicGeeks


def __generate_search_terms(
    series_title: str, format_: FormatEnum, number: Optional[str] = None
) -> Tuple[str, str]:
    search_1 = series_title
    if number and number != "1":
        search_1 += f" #{number}"
    search_2 = series_title
    if number and number != "1":
        if format_ == FormatEnum.ANNUAL:
            search_2 += f" Annual #{number}"
        elif format_ == FormatEnum.DIGITAL_CHAPTER:
            search_2 += f" Chapter #{number}"
        elif format_ == FormatEnum.HARDCOVER:
            search_2 += f" Vol. {number} HC"
        elif format_ == FormatEnum.TRADE_PAPERBACK:
            search_2 += f" Vol. {number} TP"
        else:
            search_2 += f" #{number}"
    return search_1, search_2


def __remove_extra(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    tag_re = re.compile(r"(<!--.*?-->|<[^>]*>)")
    return " ".join(html.unescape(tag_re.sub("", value.strip())).split())


def pull_info(api_key: str, client_id: str, cache: SQLiteCache, metadata: Metadata):
    CONSOLE.print("Pulling info from League of Comic Geeks", style="logging.level.info")
    session = LeagueOfComicGeeks(api_key=api_key, client_id=client_id, cache=cache)

    pulled_info = {}
    if metadata.comic.has_service(service="League of Comic Geeks"):
        pulled_info = get(
            session=session, id_=metadata.comic.get_service_id(service="League of Comic Geeks")
        )
    if not pulled_info:
        search_terms = __generate_search_terms(
            metadata.series.title, metadata.comic.format_, metadata.comic.number
        )
        pulled_info = select(session=session, metadata=metadata, search_terms=search_terms)
    return pulled_info


def get(session: LeagueOfComicGeeks, id_: int) -> Dict[str, Any]:
    if comic := session.comic(id_=id_):
        return {
            "publisher": {"title": {"League of Comic Geeks": comic.series.publisher_name}},
            "series": {
                "title": {"League of Comic Geeks": comic.series.title},
                "volume": {"League of Comic Geeks": comic.series.volume},
                "start_year": {"League of Comic Geeks": comic.series.year_begin},
            },
            "comic": {
                "format": {"League of Comic Geeks": comic.details.comic_format},
                "cover_date": {"League of Comic Geeks": comic.details.release_date},
                "page_count": {"League of Comic Geeks": comic.details.pages},
                "summary": {"League of Comic Geeks": __remove_extra(comic.details.description)},
            },
        }
    return {}


def select(
    session: LeagueOfComicGeeks, metadata: Metadata, search_terms: Tuple[str, str]
) -> Dict[str, Any]:
    results_1 = [x for x in session.comic_list(search_terms[0]) if x.variant == 0]
    results_2 = [x for x in session.comic_list(search_terms[1]) if x.variant == 0]
    results = sorted(
        list({x.id_: x for x in results_1 + results_2}.values()), key=lambda x: x.title
    )
    index = create_menu(
        options=[f"{x.id_} | {x.title}" for x in results],
        prompt="Select Comic",
        default="None of the Above",
    )
    if index:
        selected = results[index - 1]
        metadata.publisher.identifiers.append(
            Identifier(service="League of Comic Geeks", id_=selected.publisher_id)
        )
        metadata.series.identifiers.append(
            Identifier(service="League of Comic Geeks", id_=selected.series_id)
        )
        metadata.comic.identifiers.append(
            Identifier(service="League of Comic Geeks", id_=selected.id_)
        )
        session.series(id_=selected.series_id)
        return get(session=session, id_=selected.id_)
    search_term = Prompt.ask("Search Term", default=None, show_default=True, console=CONSOLE)
    return (
        select(session=session, metadata=metadata, search_terms=(search_term, search_term))
        if search_term
        else {}
    )
