from typing import Any, Dict, Optional

from rich.prompt import Prompt
from simyan.session import Session as Simyan
from simyan.sqlite_cache import SQLiteCache

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata import Identifier, Metadata


def pull_info(api_key: str, cache: SQLiteCache, metadata: Metadata):
    CONSOLE.print("Pulling info from Comicvine", style="logging.level.info")
    session = Simyan(api_key=api_key, cache=cache)

    publisher = {}
    if metadata.publisher.has_service(service="Comicvine"):
        publisher = get_publisher(
            session=session, id_=metadata.publisher.get_service_id(service="Comicvine")
        )
    if not publisher:
        publisher = search_publisher(
            session=session, metadata=metadata, title=metadata.publisher.title
        )

    series = {}
    if metadata.publisher.has_service(service="Comicvine"):
        if metadata.series.has_service(service="Comicvine"):
            series = get_volume(
                session=session, id_=metadata.series.get_service_id(service="Comicvine")
            )
        if not series:
            series = search_volume(
                session=session,
                metadata=metadata,
                publisher_id=metadata.publisher.get_service_id(service="Comicvine"),
                title=metadata.series.title,
                start_year=metadata.series.start_year,
            )

    comic = {}
    if metadata.series.has_service(service="Comicvine"):
        if metadata.comic.has_service(service="Comicvine"):
            comic = get_issue(
                session=session, id_=metadata.comic.get_service_id(service="Comicvine")
            )
        if not comic:
            comic = search_issue(
                session=session,
                metadata=metadata,
                series_id=metadata.series.get_service_id(service="Comicvine"),
                number=metadata.comic.number,
            )

    return {"publisher": publisher, "series": series, "comic": comic}


def get_publisher(session: Simyan, id_: int) -> Dict[str, Any]:
    if publisher := session.publisher(_id=id_):
        return {"title": {"Comicvine": publisher.name}}
    return {}


def search_publisher(session: Simyan, metadata: Metadata, title: str) -> Dict[str, Any]:
    results = sorted(
        session.publisher_list(params={"filter": f"name:{title}"}), key=lambda x: x.name
    )
    index = create_menu(
        options=[f"{x.id} | {x.name}" for x in results],
        prompt="Select Publisher",
        default="None of the Above",
    )
    if index:
        selected = results[index - 1]
        metadata.publisher.identifiers.append(Identifier(service="Comicvine", id_=selected.id))
        return get_publisher(session=session, id_=selected.id)
    title = Prompt.ask("Publisher Title", default=None, show_default=True, console=CONSOLE)
    return search_publisher(session=session, metadata=metadata, title=title) if title else {}


def get_volume(session: Simyan, id_: int) -> Dict[str, Any]:
    if volume := session.volume(_id=id_):
        return {
            "title": {"Comicvine": volume.name},
            "start_year": {"Comicvine": volume.start_year},
        }
    return {}


def search_volume(
    session: Simyan,
    metadata: Metadata,
    publisher_id: int,
    title: str,
    start_year: Optional[int] = None,
) -> Dict[str, Any]:
    results = filter(
        lambda x: x.publisher and x.publisher.id == publisher_id,
        session.volume_list(params={"filter": f"name:{title}"}),
    )
    if start_year:
        results = filter(lambda x: x.start_year == start_year, results)
    results = sorted(results, key=lambda x: (x.name, x.start_year or 0))
    index = create_menu(
        options=[f"{x.id} | {x.name} ({x.start_year})" for x in results],
        prompt="Select Volume",
        default="None of the Above",
    )
    if index:
        selected = results[index - 1]
        metadata.series.identifiers.append(Identifier(service="Comicvine", id_=selected.id))
        return get_volume(session=session, id_=selected.id)
    if start_year:
        return search_volume(
            session=session, metadata=metadata, publisher_id=publisher_id, title=title
        )
    title = Prompt.ask("Volume Title", default=None, show_default=True, console=CONSOLE)
    return (
        search_volume(session=session, metadata=metadata, publisher_id=publisher_id, title=title)
        if title
        else {}
    )


def get_issue(session: Simyan, id_: int) -> Dict[str, Any]:
    if issue := session.issue(_id=id_):
        return {
            "number": {"Comicvine": issue.number},
            "cover_date": {"Comicvine": issue.cover_date},
            "store_date": {"Comicvine": issue.store_date},
            "summary": {"Comicvine": issue.summary or issue.description},
            "title": {"Comicvine": issue.name},
        }
    return {}


def search_issue(
    session: Simyan, metadata: Metadata, series_id: int, number: str
) -> Dict[str, Any]:
    results = sorted(
        session.issue_list(params={"filter": f"volume:{series_id},number:{number}"}),
        key=lambda x: x.number,
    )
    index = create_menu(
        options=[f"{x.id} | {x.volume.name} #{x.number}" for x in results],
        prompt="Select Issue",
        default="None of the Above",
    )
    if index:
        selected = results[index - 1]
        metadata.comic.identifiers.append(Identifier(service="Comicvine", id_=selected.id))
        return get_issue(session=session, id_=selected.id)
    number = Prompt.ask("Issue Number", default=None, show_default=True, console=CONSOLE)
    return (
        search_issue(session=session, metadata=metadata, series_id=series_id, number=number)
        if number
        else {}
    )
