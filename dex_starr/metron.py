from typing import Any, Dict, Optional

from mokkari.issue import Issue
from mokkari.publisher import Publisher
from mokkari.series import Series
from mokkari.session import Session
from simyan.sqlite_cache import SQLiteCache

from dex_starr.console import ConsoleLog
from dex_starr.metadata import Identifier, Metadata

CONSOLE = ConsoleLog(__name__)


class Metron:
    def __init__(self, username: str, password: str, cache: Optional[SQLiteCache] = None):
        if not cache:
            cache = SQLiteCache()
        self.session = Session(username=username, passwd=password, cache=cache)

    def lookup_publisher(self, metadata: Metadata) -> Dict[str, Any]:
        if "metron" in [x.service.lower() for x in metadata.publisher.identifiers]:
            publisher = self.select_publisher(
                int([x for x in metadata.publisher.identifiers if x.service.lower() == "metron"][0].id)
            )
            if publisher:
                return {"title": {"Metron": publisher.name}}
        else:
            result = self.search_publisher(title=metadata.publisher.title)
            if result:
                metadata.publisher.identifiers.append(Identifier(service="Metron", id=result.id))
                return self.lookup_publisher(metadata)
        return {}

    def search_publisher(self, title: str, attempts: int = 0) -> Optional[Publisher]:
        results = [x for x in self.session.publishers_list({"name": title})]
        if results:
            selected_index = CONSOLE.menu(options=[f"{x.id} | {x.name}" for x in results], prompt="Select Publisher")
            if selected_index != 0:
                return results[selected_index - 1]
        if attempts:
            CONSOLE.info("No results found in Metron")
        title = CONSOLE.prompt("Publisher Title", require_response=False)
        if title:
            return self.search_publisher(title=title, attempts=attempts + 1)
        return None

    def select_publisher(self, _id: int) -> Publisher:
        return self.session.publisher(_id=_id)

    def lookup_series(self, metadata: Metadata) -> Dict[str, Any]:
        if "metron" in [x.service.lower() for x in metadata.series.identifiers]:
            series = self.select_series(
                int([x for x in metadata.series.identifiers if x.service.lower() == "metron"][0].id)
            )
            if series:
                return {
                    "title": {"Metron": series.name},
                    "volume": {"Metron": series.volume},
                    "start_year": {"Metron": series.year_began},
                }
        else:
            publisher_id = int([x for x in metadata.publisher.identifiers if x.service.lower() == "metron"][0].id)
            result = self.search_series(
                publisher_id=publisher_id,
                title=metadata.series.title,
                volume=metadata.series.volume,
                start_year=metadata.series.start_year,
            )
            if result:
                metadata.series.identifiers.append(Identifier(service="Metron", id=result.id))
                return self.lookup_series(metadata)
        return {}

    def search_series(
        self,
        publisher_id: int,
        title: str,
        volume: Optional[int] = None,
        start_year: Optional[int] = None,
        attempts: int = 0,
    ) -> Optional[Series]:
        filters = {"publisher_id": publisher_id, "name": title}
        if volume:
            filters["volume"] = volume
        if start_year:
            filters["start_year"] = start_year
        results = [x for x in self.session.series_list(filters)]
        if results:
            selected_index = CONSOLE.menu(
                options=[f"{x.id} | {x.display_name}" for x in results], prompt="Select Series"
            )
            if selected_index != 0:
                return results[selected_index - 1]
        if start_year:
            return self.search_series(publisher_id, title, volume=volume)
        if volume:
            return self.search_series(publisher_id, title, start_year=start_year)
        if attempts:
            CONSOLE.info("No results found in Metron")
        title = CONSOLE.prompt("Series Title", require_response=False)
        if title:
            return self.search_series(publisher_id, title, attempts=attempts + 1)
        return None

    def select_series(self, _id: int) -> Series:
        return self.session.series(_id=_id)

    def lookup_comic(self, metadata: Metadata) -> Dict[str, Any]:
        if "metron" in [x.service.lower() for x in metadata.comic.identifiers]:
            comic = self.select_comic(
                int([x for x in metadata.comic.identifiers if x.service.lower() == "metron"][0].id)
            )
            if comic:
                return {
                    "number": {"Metron": comic.number},
                    "cover_date": {"Metron": comic.cover_date},
                    "page_count": {"Metron": comic.page_count},
                    "store_date": {"Metron": comic.store_date},
                    "summary": {"Metron": comic.desc},
                    "title": {"Metron": "; ".join(comic.story_titles)},
                }
        else:
            series_id = int([x for x in metadata.series.identifiers if x.service.lower() == "metron"][0].id)
            result = self.search_comic(series_id=series_id, number=metadata.comic.number)
            if result:
                metadata.comic.identifiers.append(Identifier(service="Metron", id=result.id))
                return self.lookup_comic(metadata)
        return {}

    def search_comic(self, series_id: int, number: str, attempts: int = 1) -> Optional[Issue]:
        results = [x for x in self.session.issues_list({"series_id": series_id, "number": number})]
        if results:
            selected_index = CONSOLE.menu(options=[f"{x.id} | {x.issue_name}" for x in results], prompt="Select Comic")
            if selected_index != 0:
                return results[selected_index - 1]
        if attempts:
            CONSOLE.info("No results found in Metron")
        number = CONSOLE.prompt("Comic Number", require_response=False)
        if number:
            return self.search_comic(series_id, number, attempts=attempts + 1)
        return None

    def select_comic(self, _id: int) -> Issue:
        return self.session.issue(_id=_id)


def pull_info(username: str, password: str, cache: SQLiteCache, metadata: Metadata):
    metron = Metron(username, password, cache=cache)
    CONSOLE.rule("Pulling Info from Metron")
    publisher = metron.lookup_publisher(metadata)
    series = metron.lookup_series(metadata) if publisher else {}
    comic = metron.lookup_comic(metadata) if series else {}
    return {
        "publisher": publisher,
        "series": series,
        "comic": comic,
    }
