__all__ = ["create_metadata", "to_comic_info", "to_metron_info"]

from typing import Dict, List, Tuple

from rich.prompt import IntPrompt, Prompt

from ..console import CONSOLE, create_menu
from .comic_info import ComicInfo
from .metadata import Issue, Metadata, Publisher, Series
from .metron_info import Arc, Credit, MetronInfo, Resource
from .metron_info import Series as MetronSeries
from .metron_info import Source


def create_metadata() -> Metadata:
    publisher = Publisher(title=Prompt.ask("Publisher title", console=CONSOLE))
    series = Series(
        title=Prompt.ask("Series title", console=CONSOLE),
        volume=IntPrompt.ask("Series volume", default=1, console=CONSOLE),
    )
    formats = ["Annual", "Comic", "Digital Chapter", "Hardcover", "Trade Paperback"]
    format_index = create_menu(options=formats, prompt="Issue format", default="Comic")
    format = "Comic"
    if format_index != 0:
        format = formats[format_index - 1]
    issue = Issue(
        format=format,
        number=Prompt.ask("Issue number", console=CONSOLE),
    )
    return Metadata(publisher=publisher, series=series, issue=issue)


def to_comic_info(metadata: Metadata) -> ComicInfo:
    roles = ["Writer", "Penciller", "Inker", "Colorist", "Letterer", "Cover Artist", "Editor"]
    creators = {}
    for role in roles:
        creators[role] = [x.name for x in metadata.issue.creators if role in x.roles]
    return ComicInfo(
        title=metadata.issue.title,
        series=metadata.series.title,
        number=metadata.issue.number,
        # Count
        volume=metadata.series.volume,
        # Alternate Series
        # Alternate Number
        # Alternate Count
        summary=metadata.issue.summary,
        notes=metadata.notes,
        year=metadata.issue.cover_date.year if metadata.issue.cover_date else None,
        month=metadata.issue.cover_date.month if metadata.issue.cover_date else None,
        day=metadata.issue.cover_date.day if metadata.issue.cover_date else None,
        writer=", ".join(creators["Writer"]) if creators["Writer"] else None,
        penciller=", ".join(creators["Penciller"]) if creators["Penciller"] else None,
        inker=", ".join(creators["Inker"]) if creators["Inker"] else None,
        colorist=", ".join(creators["Colorist"]) if creators["Colorist"] else None,
        letterer=", ".join(creators["Letterer"]) if creators["Letterer"] else None,
        cover_artist=", ".join(creators["Cover Artist"]) if creators["Cover Artist"] else None,
        editor=", ".join(creators["Editor"]) if creators["Editor"] else None,
        publisher=metadata.publisher.title,
        imprint=metadata.publisher.imprint,
        genre=", ".join(metadata.issue.genres) if metadata.issue.genres else None,
        # Web
        page_count=metadata.issue.page_count,
        language_iso=metadata.issue.language,
        format=metadata.issue.format,
        characters=", ".join(metadata.issue.characters) if metadata.issue.characters else None,
        teams=", ".join(metadata.issue.teams) if metadata.issue.teams else None,
        locations=", ".join(metadata.issue.locations) if metadata.issue.locations else None,
        story_arc=", ".join([x.title for x in metadata.issue.story_arcs])
        if metadata.issue.story_arcs
        else None,
        # Series Group
        # TODO: Add pages
    )


def get_source(sources: Dict[str, int], resolution_order: List[str]) -> Tuple[int, str]:
    result = None
    for source in reversed(resolution_order):
        if source in sources:
            result = (sources[source], source)
    return result


def to_metron_info(metadata: Metadata, resolution_order: List[str]) -> MetronInfo:
    source = get_source(metadata.issue.sources, resolution_order)
    return MetronInfo(
        id=Source(source=source[1], value=source[0]) if source else None,
        publisher=Resource(
            id=metadata.publisher.sources.get(source[1]) if source else None,
            value=metadata.publisher.title,
        ),
        series=MetronSeries(
            name=Resource(
                id=metadata.series.sources.get(source[1]) if source else None,
                value=metadata.series.title,
            ),
            sort_name=metadata.series.title,
            volume=metadata.series.volume,
            format=metadata.issue.format,
            lang=metadata.issue.language,
        ),
        collection_title=metadata.issue.title,
        number=metadata.issue.number,
        # TODO: Add stories
        summary=metadata.issue.summary,
        # TODO: Add prices
        cover_date=metadata.issue.cover_date,
        store_date=metadata.issue.store_date,
        page_count=metadata.issue.page_count,
        notes=metadata.notes,
        genres=[Resource(value=x) for x in metadata.issue.genres],
        # TODO: Add tags
        story_arcs=[
            Arc(name=Resource(value=x.title), number=x.number) for x in metadata.issue.story_arcs
        ],
        characters=[Resource(value=x) for x in metadata.issue.characters],
        teams=[Resource(value=x) for x in metadata.issue.teams],
        locations=[Resource(value=x) for x in metadata.issue.locations],
        # TODO: Add reprints
        # TODO: Add GTIN - ISBN & UPC
        credits=[
            Credit(creator=Resource(value=x.name), roles=[Resource(value=r) for r in x.roles])
            for x in metadata.issue.creators
        ],
        # TODO: Add pages
    )
