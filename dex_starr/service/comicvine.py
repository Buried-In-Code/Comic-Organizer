from typing import Any, Dict, Optional

from rich.prompt import Prompt
from simyan.issue import Issue
from simyan.issue_list import IssueResult
from simyan.publisher import Publisher
from simyan.publisher_list import PublisherResult
from simyan.session import Session
from simyan.sqlite_cache import SQLiteCache
from simyan.volume import Volume
from simyan.volume_list import VolumeResult

from ..console import CONSOLE, create_menu
from ..metadata import Identifier, Metadata


class Comicvine:
    def __init__(self, api_key: str, cache: Optional[SQLiteCache] = None):
        self.session = Session(api_key=api_key, cache=cache)

    def lookup_publisher(self, metadata: Metadata) -> Dict[str, Any]:
        if "comicvine" in [x.service.lower() for x in metadata.publisher.identifiers]:
            publisher = self.select_publisher(
                int(
                    [x for x in metadata.publisher.identifiers if x.service.lower() == "comicvine"][
                        0
                    ].id_
                )
            )
            if publisher:
                return {"title": {"Comicvine": publisher.name}}
        else:
            result = self.search_publisher(title=metadata.publisher.title)
            if result:
                metadata.publisher.identifiers.append(
                    Identifier(service="Comicvine", id_=result.id)
                )
                return self.lookup_publisher(metadata)
        return {}

    def search_publisher(self, title: str, attempts: int = 0) -> Optional[PublisherResult]:
        results = [x for x in self.session.publisher_list({"filter": f"name:{title}"})]
        if results:
            results = sorted(results, key=lambda x: x.name)
            selected_index = create_menu(
                options=[f"{x.id} | {x.name}" for x in results],
                prompt="Select Publisher",
                default="None of the Above",
            )
            if selected_index != 0:
                return results[selected_index - 1]
        if attempts:
            CONSOLE.print("No results found in Comicvine", style="logging.level.info")
        title = Prompt.ask("Publisher Title", console=CONSOLE)
        if title:
            return self.search_publisher(title=title, attempts=attempts + 1)
        return None

    def select_publisher(self, _id: int) -> Publisher:
        return self.session.publisher(_id=_id)

    def lookup_series(self, metadata: Metadata) -> Dict[str, Any]:
        if "comicvine" in [x.service.lower() for x in metadata.series.identifiers]:
            series = self.select_series(
                int(
                    [x for x in metadata.series.identifiers if x.service.lower() == "comicvine"][
                        0
                    ].id_
                )
            )
            if series:
                return {
                    "title": {"Comicvine": series.name},
                    "start_year": {"Comicvine": series.start_year},
                }
        else:
            publisher_id = int(
                [x for x in metadata.publisher.identifiers if x.service.lower() == "comicvine"][
                    0
                ].id_
            )
            result = self.search_series(
                publisher_id=publisher_id,
                title=metadata.series.title,
                start_year=metadata.series.start_year,
            )
            if result:
                metadata.series.identifiers.append(Identifier(service="Comicvine", id_=result.id))
                return self.lookup_series(metadata)
        return {}

    def search_series(
        self, publisher_id: int, title: str, start_year: Optional[int] = None, attempts: int = 0
    ) -> Optional[VolumeResult]:
        results = [
            x
            for x in self.session.volume_list({"filter": f"name:{title}"})
            if x.publisher and x.publisher.id == publisher_id
        ]
        if results:
            if start_year:
                results = [x for x in results if x.start_year == start_year]
            if results:
                results = sorted(results, key=lambda x: x.name)
                selected_index = create_menu(
                    options=[f"{x.id} | {x.name} ({x.start_year})" for x in results],
                    prompt="Select Series",
                    default="None of the Above",
                )
                if selected_index != 0:
                    return results[selected_index - 1]
        if start_year:
            return self.search_series(publisher_id, title)
        if attempts:
            CONSOLE.print("No results found in Comicvine", style="logging.level.info")
        title = Prompt.ask("Series Title", console=CONSOLE)
        if title:
            return self.search_series(publisher_id, title, attempts=attempts + 1)
        return None

    def select_series(self, _id: int) -> Volume:
        return self.session.volume(_id=_id)

    def lookup_comic(self, metadata: Metadata) -> Dict[str, Any]:
        if "comicvine" in [x.service.lower() for x in metadata.comic.identifiers]:
            comic = self.select_comic(
                int(
                    [x for x in metadata.comic.identifiers if x.service.lower() == "comicvine"][
                        0
                    ].id_
                )
            )
            if comic:
                return {
                    "number": {"Comicvine": comic.number},
                    "cover_date": {"Comicvine": comic.cover_date},
                    "store_date": {"Comicvine": comic.store_date},
                    "summary": {"Comicvine": comic.summary or comic.description},
                    "title": {"Comicvine": comic.name},
                }
        else:
            series_id = int(
                [x for x in metadata.series.identifiers if x.service.lower() == "comicvine"][0].id_
            )
            result = self.search_comic(series_id=series_id, number=metadata.comic.number)
            if result:
                metadata.comic.identifiers.append(Identifier(service="Comicvine", id_=result.id))
                return self.lookup_comic(metadata)
        return {}

    def search_comic(self, series_id: int, number: str, attempts: int = 0) -> Optional[IssueResult]:
        results = [
            x
            for x in self.session.issue_list(
                {"filter": f"volume:{series_id},issue_number:{number}"}
            )
        ]
        if results:
            results = sorted(results, key=lambda x: (x.volume.name, x.number))
            selected_index = create_menu(
                options=[f"{x.id} | {x.volume.name} #{x.number}" for x in results],
                prompt="Select Comic",
                default="None of the Above",
            )
            if selected_index != 0:
                return results[selected_index - 1]
        if attempts:
            CONSOLE.print("No results found in Comicvine", style="logging.level.info")
        number = Prompt.ask("Comic Number", console=CONSOLE)
        if number:
            return self.search_comic(series_id, number, attempts=attempts + 1)
        return None

    def select_comic(self, _id: int) -> Issue:
        return self.session.issue(_id=_id)


def pull_info(api_key: str, cache: SQLiteCache, metadata: Metadata):
    comicvine = Comicvine(api_key, cache=cache)
    CONSOLE.print("Pulling Info from Comicvine", style="blue")
    return {
        "publisher": comicvine.lookup_publisher(metadata),
        "series": comicvine.lookup_series(metadata),
        "comic": comicvine.lookup_comic(metadata),
    }
