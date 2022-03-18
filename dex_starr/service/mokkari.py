from typing import Any, Dict, Optional

from mokkari.exceptions import ApiError
from mokkari.session import Session as Mokkari
from rich.prompt import Prompt
from simyan.sqlite_cache import SQLiteCache

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata import Identifier, Metadata


def pull_info(username: str, password: str, cache: SQLiteCache, metadata: Metadata):
    CONSOLE.print("Pulling info from Metron", style="logging.level.info")
    session = Mokkari(username=username, passwd=password, cache=cache)

    publisher = {}
    if metadata.publisher.has_service(service="Metron"):
        publisher = get_publisher(
            session=session, id_=metadata.publisher.get_service_id(service="Metron")
        )
    if not publisher:
        publisher = search_publisher(
            session=session, metadata=metadata, title=metadata.publisher.title
        )

    series = {}
    if metadata.publisher.has_service(service="Metron"):
        if metadata.series.has_service(service="Metron"):
            series = get_series(
                session=session, id_=metadata.series.get_service_id(service="Metron")
            )
        if not series:
            series = search_series(
                session=session,
                metadata=metadata,
                publisher_id=metadata.publisher.get_service_id(service="Metron"),
                title=metadata.series.title,
                volume=metadata.series.volume,
                start_year=metadata.series.start_year,
            )

    comic = {}
    if metadata.series.has_service(service="Metron"):
        if metadata.comic.has_service(service="Metron"):
            comic = get_issue(session=session, id_=metadata.comic.get_service_id(service="Metron"))
        if not comic:
            comic = search_issue(
                session=session,
                metadata=metadata,
                series_id=metadata.series.get_service_id(service="Metron"),
                number=metadata.comic.number,
            )

    return {"publisher": publisher, "series": series, "comic": comic}


def get_publisher(session: Mokkari, id_: int) -> Dict[str, Any]:
    try:
        if publisher := session.publisher(_id=id_):
            return {"title": {"Metron": publisher.name}}
    except ApiError:
        pass
    return {}


def search_publisher(session: Mokkari, metadata: Metadata, title: str) -> Dict[str, Any]:
    results = sorted(session.publishers_list(params={"name": title}), key=lambda x: x.name)
    index = create_menu(
        options=[f"{x.id} | {x.name}" for x in results],
        prompt="Select Publisher",
        default="None of the Above",
    )
    if index:
        selected = results[index - 1]
        metadata.publisher.identifiers.append(Identifier(service="Metron", id_=selected.id))
        return get_publisher(session=session, id_=selected.id)
    title = Prompt.ask("Publisher Title", default=None, show_default=True, console=CONSOLE)
    return search_publisher(session=session, metadata=metadata, title=title) if title else {}


def get_series(session: Mokkari, id_: int) -> Dict[str, Any]:
    try:
        if series := session.series(_id=id_):
            return {
                "title": {"Metron": series.name},
                "volume": {"Metron": series.volume},
                "start_year": {"Metron": series.year_began},
            }
    except ApiError:
        pass
    return {}


def search_series(
    session: Mokkari,
    metadata: Metadata,
    publisher_id: int,
    title: str,
    volume: Optional[int] = None,
    start_year: Optional[int] = None,
) -> Dict[str, Any]:
    params = {"publisher_id": publisher_id, "name": title}
    if volume:
        params["volume"] = volume
    if start_year:
        params["start_year"] = start_year
    results = sorted(session.series_list(params=params), key=lambda x: x.display_name)
    index = create_menu(
        options=[f"{x.id} | {x.display_name}" for x in results],
        prompt="Select Series",
        default="None of the Above",
    )
    if index:
        selected = results[index - 1]
        metadata.series.identifiers.append(Identifier(service="Metron", id_=selected.id))
        return get_series(session=session, id_=selected.id)
    if volume:
        return search_series(
            session=session,
            metadata=metadata,
            publisher_id=publisher_id,
            title=title,
            start_year=start_year,
        )
    if start_year:
        return search_series(
            session=session, metadata=metadata, publisher_id=publisher_id, title=title
        )
    title = Prompt.ask("Series Title", default=None, show_default=True, console=CONSOLE)
    return (
        search_series(session=session, metadata=metadata, publisher_id=publisher_id, title=title)
        if title
        else {}
    )


def get_issue(session: Mokkari, id_: int) -> Dict[str, Any]:
    try:
        if issue := session.issue(_id=id_):
            return {
                "number": {"Metron": issue.number},
                "cover_date": {"Metron": issue.cover_date},
                "page_count": {"Metron": issue.page_count},
                "store_date": {"Metron": issue.store_date},
                "summary": {"Metron": issue.desc},
                "title": {"Metron": "; ".join(issue.story_titles)},
            }
    except ApiError:
        pass
    return {}


def search_issue(
    session: Mokkari, metadata: Metadata, series_id: int, number: str
) -> Dict[str, Any]:
    results = sorted(
        session.issues_list(params={"series_id": series_id, "number": number}),
        key=lambda x: x.issue_name,
    )
    index = create_menu(
        options=[f"{x.id} | {x.issue_name}" for x in results],
        prompt="Select Issue",
        default="None of the Above",
    )
    if index:
        selected = results[index - 1]
        metadata.comic.identifiers.append(Identifier(service="Metron", id_=selected.id))
        return get_issue(session=session, id_=selected.id)
    number = Prompt.ask("Comic Number", default=None, show_default=True, console=CONSOLE)
    return (
        search_issue(session=session, metadata=metadata, series_id=series_id, number=number)
        if number
        else {}
    )
