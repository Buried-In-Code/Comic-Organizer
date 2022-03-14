import html
import re
from datetime import date
from typing import Any, Dict, Optional, Tuple

from rich.prompt import Prompt
from simyan.sqlite_cache import SQLiteCache

from ...console import CONSOLE, create_menu
from ...metadata import FormatEnum, Identifier, Metadata
from .session import Session


class League:
    def __init__(self, api_key: str, client_id: str, cache: Optional[SQLiteCache] = None):
        self.session = Session(api_key=api_key, client_id=client_id, cache=cache)

    def select_series(self, _id: int) -> Dict[str, Any]:
        return self.session.series(_id=_id)

    def __generate_search_terms(
        self, series_title: str, format_: FormatEnum, number: Optional[str] = None
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

    def __remove_extra(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        tag_re = re.compile(r"(<!--.*?-->|<[^>]*>)")
        return " ".join(html.unescape(tag_re.sub("", value.strip())).split())

    def lookup_comic(self, metadata: Metadata) -> Dict[str, Any]:
        if "league of comic geeks" in [x.service.lower() for x in metadata.comic.identifiers]:
            comic = self.select_comic(
                int(
                    [
                        x
                        for x in metadata.comic.identifiers
                        if x.service.lower() == "league of comic geeks"
                    ][0].id_
                )
            )
            if comic:
                return {
                    "publisher": {
                        "title": {"League of Comic Geeks": comic["series"]["publisher_name"]}
                    },
                    "series": {
                        "title": {"League of Comic Geeks": comic["series"]["title"]},
                        "volume": {
                            "League of Comic Geeks": int(comic["series"]["volume"])
                            if comic["series"]["volume"]
                            else 1
                        },
                        "start_year": {
                            "League of Comic Geeks": int(comic["series"]["year_begin"])
                            if comic["series"]["year_begin"]
                            else None
                        },
                    },
                    "comic": {
                        "format": {
                            "League of Comic Geeks": FormatEnum.get(comic["details"]["format"])
                        },
                        "cover_date": {
                            "League of Comic Geeks": date.fromisoformat(
                                comic["details"]["date_release"]
                            )
                        },
                        "page_count": {"League of Comic Geeks": int(comic["details"]["pages"])},
                        "summary": {
                            "League of Comic Geeks": self.__remove_extra(
                                comic["details"]["description"]
                            )
                        },
                    },
                }
        else:
            search_terms = self.__generate_search_terms(
                metadata.series.title, metadata.comic.format_, metadata.comic.number
            )
            result = self.search_comic(search_terms)
            if result:
                metadata.publisher.identifiers.append(
                    Identifier(service="League of Comic Geeks", id_=int(result["publisher_id"]))
                )
                metadata.series.identifiers.append(
                    Identifier(service="League of Comic Geeks", id_=int(result["series_id"]))
                )
                metadata.comic.identifiers.append(
                    Identifier(service="League of Comic Geeks", id_=int(result["id"]))
                )
                return self.lookup_comic(metadata)
        return {}

    def search_comic(
        self, search_terms: Tuple[str, str], format_: Optional[FormatEnum] = None, attempts: int = 0
    ) -> Optional[Dict[str, Any]]:
        results_1 = [x for x in self.session.comic_list(search_terms[0]) if x["variant"] == "0"]
        results_2 = []
        if search_terms[0] != search_terms[1]:
            results_2 = [x for x in self.session.comic_list(search_terms[1]) if x["variant"] == "0"]
        results = results_1 + results_2
        if results:
            if format_:
                results = [x for x in results if x["format"] == format_.get_title()]
            if results:
                results = sorted(results, key=lambda x: x["title"])
                selected_index = create_menu(
                    options=[f"{x['id']} | {x['title']}" for x in results],
                    prompt="Select Comic",
                    default="None of the Above",
                )
                if selected_index != 0:
                    return results[selected_index - 1]
        if format_:
            return self.search_comic(search_terms)
        if attempts:
            CONSOLE.print("No results found in League of Comic Geeks", style="logging.level.info")
        search = Prompt.ask("Search Term", console=CONSOLE)
        if search:
            return self.search_comic((search, search), attempts=attempts + 1)
        return None

    def select_comic(self, _id: int) -> Dict[str, Any]:
        return self.session.comic(_id=_id)


def pull_info(api_key: str, client_id: str, cache: SQLiteCache, metadata: Metadata):
    league = League(api_key, client_id, cache=cache)
    CONSOLE.print("Pulling Info from League of Comic Geeks", style="blue")
    return league.lookup_comic(metadata)
