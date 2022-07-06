from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE
from dex_starr.metadata.comic_info import ComicInfo
from dex_starr.metadata.metadata import FormatEnum, Issue, Metadata, Publisher, Series
from dex_starr.metadata.metron_info import MetronInfo


def create_metadata() -> Metadata:
    publisher = Publisher(title=Prompt.ask("Publisher title", console=CONSOLE))
    series = Series(
        title=Prompt.ask("Series title", console=CONSOLE),
        volume=IntPrompt.ask("Series volume", default=1, console=CONSOLE),
    )
    issue = Issue(
        format=FormatEnum(
            Prompt.ask(
                "Issue format",
                default=FormatEnum.COMIC.value,
                choices=[x.value for x in list(FormatEnum) if x != FormatEnum.UNSET],
                console=CONSOLE,
            )
        ),
        number=Prompt.ask("Issue number", console=CONSOLE),
    )
    return Metadata(publisher=publisher, series=series, issue=issue)


def to_comic_info(metadata: Metadata) -> ComicInfo:
    return ComicInfo(
        publisher=metadata.publisher.title,
        imprint=metadata.publisher.imprint,
        series=metadata.series.title,
        volume=metadata.series.start_year,
        number=metadata.issue.number,
        characters=", ".join(metadata.issue.characters),
        year=metadata.issue.cover_date.year if metadata.issue.cover_date else None,
        month=metadata.issue.cover_date.month if metadata.issue.cover_date else None,
        day=metadata.issue.cover_date.day if metadata.issue.cover_date else None,
        writer=", ".join([k for k, v in metadata.issue.creators.items() if "Writer" in v]),
        penciller=", ".join([k for k, v in metadata.issue.creators.items() if "Penciller" in v]),
        inker=", ".join([k for k, v in metadata.issue.creators.items() if "Inker" in v]),
        colorist=", ".join([k for k, v in metadata.issue.creators.items() if "Colourist" in v]),
        letterer=", ".join([k for k, v in metadata.issue.creators.items() if "Letterer" in v]),
        cover_artist=", ".join(
            [k for k, v in metadata.issue.creators.items() if "Cover Artist" in v]
        ),
        editor=", ".join([k for k, v in metadata.issue.creators.items() if "Editor" in v]),
        genre=", ".join(metadata.issue.genres),
        language_iso=metadata.issue.language_iso,
        locations=", ".join(metadata.issue.locations),
        page_count=metadata.issue.page_count,
        story_arc=", ".join(metadata.issue.story_arcs),
        summary=metadata.issue.summary,
        teams=", ".join(metadata.issue.teams),
        title=metadata.issue.title,
        notes=metadata.notes,
    )


def to_metron_info(metadata: Metadata) -> MetronInfo:
    pass
