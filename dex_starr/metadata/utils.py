from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.metadata.comic_info import ComicInfo
from dex_starr.metadata.metadata import Issue, Metadata, Publisher, Series
from dex_starr.metadata.metron_info import MetronInfo
from dex_starr.metadata.metron_info import Series as MetronSeries


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
    writers = [k for k, v in metadata.issue.creators.items() if "Writer" in v]
    pencillers = [k for k, v in metadata.issue.creators.items() if "Penciller" in v]
    inkers = [k for k, v in metadata.issue.creators.items() if "Inker" in v]
    colorists = [k for k, v in metadata.issue.creators.items() if "Colorist" in v]
    letterers = [k for k, v in metadata.issue.creators.items() if "Letterer" in v]
    cover_artists = [k for k, v in metadata.issue.creators.items() if "Cover Artist" in v]
    editors = [k for k, v in metadata.issue.creators.items() if "Editor" in v]
    return ComicInfo(
        publisher=metadata.publisher.title,
        imprint=metadata.publisher.imprint,
        series=metadata.series.title,
        volume=metadata.series.start_year,
        number=metadata.issue.number,
        characters=", ".join(metadata.issue.characters) if metadata.issue.characters else None,
        year=metadata.issue.cover_date.year if metadata.issue.cover_date else None,
        month=metadata.issue.cover_date.month if metadata.issue.cover_date else None,
        day=metadata.issue.cover_date.day if metadata.issue.cover_date else None,
        writer=", ".join(writers) if writers else None,
        penciller=", ".join(pencillers) if pencillers else None,
        inker=", ".join(inkers) if inkers else None,
        colorist=", ".join(colorists) if colorists else None,
        letterer=", ".join(letterers) if letterers else None,
        cover_artist=", ".join(cover_artists) if cover_artists else None,
        editor=", ".join(editors) if editors else None,
        genre=", ".join(metadata.issue.genres) if metadata.issue.genres else None,
        language_iso=metadata.issue.language_iso,
        locations=", ".join(metadata.issue.locations) if metadata.issue.locations else None,
        page_count=metadata.issue.page_count,
        story_arc=", ".join(metadata.issue.story_arcs) if metadata.issue.story_arcs else None,
        summary=metadata.issue.summary,
        teams=", ".join(metadata.issue.teams) if metadata.issue.teams else None,
        title=metadata.issue.title,
        notes=metadata.notes,
    )


def to_metron_info(metadata: Metadata) -> MetronInfo:
    return MetronInfo(
        publisher=metadata.publisher.title,
        series=MetronSeries(
            name=metadata.series.title, sort_name=metadata.series.title, type=metadata.issue.format
        ),
        volume=metadata.series.volume,
        collection_title=metadata.issue.title,
        number=metadata.issue.number,
        summary=metadata.issue.summary,
        cover_date=metadata.issue.cover_date,
        store_date=metadata.issue.store_date,
        page_count=metadata.issue.page_count,
        characters=metadata.issue.characters,
        locations=metadata.issue.locations,
    )
