__all__ = ["create_metadata", "to_comic_info", "to_metron_info"]

from typing import List, Optional

from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.models.comic_info.schema import ComicInfo, Page
from dex_starr.models.metadata.enums import Format
from dex_starr.models.metadata.schema import Issue, Metadata, Publisher, Series
from dex_starr.models.metron_info.enums import Format as MetronFormat
from dex_starr.models.metron_info.enums import InformationSource, Role
from dex_starr.models.metron_info.schema import (
    Arc,
    Credit,
    GenreResource,
    MetronInfo,
    Resource,
    RoleResource,
)
from dex_starr.models.metron_info.schema import Series as MetronSeries
from dex_starr.models.metron_info.schema import Source as MetronSource


def create_metadata() -> Metadata:
    publisher = Publisher(title=Prompt.ask("Publisher title", console=CONSOLE))
    series = Series(
        title=Prompt.ask("Series title", console=CONSOLE),
        volume=IntPrompt.ask("Series volume", default=1, console=CONSOLE),
    )
    formats = list(Format)
    index = create_menu(options=formats, prompt="Issue format", default=Format.COMIC)
    issue = Issue(
        format=formats[index - 1] if index else Format.COMIC,
        number=Prompt.ask("Issue number", console=CONSOLE),
    )
    return Metadata(publisher=publisher, series=series, issue=issue)


def to_comic_info(metadata: Metadata) -> ComicInfo:
    roles = ["Writer", "Penciller", "Inker", "Colorist", "Letterer", "Cover Artist", "Editor"]
    creators = {}
    for role in roles:
        creators[role] = sorted(
            [
                x.name
                for x in metadata.issue.creators
                if role in sorted([str(r) for r in x.roles], alg=ns.NA | ns.G)
            ],
            alg=ns.NA | ns.G,
        )
    return ComicInfo(
        title=metadata.issue.title,
        series=metadata.series.title,
        number=metadata.issue.number,
        # TODO: Count
        volume=metadata.series.volume,
        # TODO: Alternate Series
        # TODO: Alternate Number
        # TODO: Alternate Count
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
        genre=", ".join(str(x) for x in metadata.issue.genres) if metadata.issue.genres else None,
        # TODO: Web
        page_count=metadata.issue.page_count,
        language_iso=metadata.issue.language,
        format=str(metadata.issue.format),
        characters=", ".join(metadata.issue.characters) if metadata.issue.characters else None,
        teams=", ".join(metadata.issue.teams) if metadata.issue.teams else None,
        locations=", ".join(metadata.issue.locations) if metadata.issue.locations else None,
        story_arc=", ".join([x.title for x in metadata.issue.story_arcs])
        if metadata.issue.story_arcs
        else None,
        # TODO: Series Group
        pages=sorted(
            {
                Page(
                    image=x.image,
                    page_type=x.page_type,
                    double_page=x.double_page,
                    image_size=x.image_size,
                    key=x.key,
                    bookmark=x.bookmark,
                    image_width=x.image_width,
                    image_height=x.image_height,
                )
                for x in metadata.pages
            },
            alg=ns.NA | ns.G,
        ),
    )


def select_primary_source(sources, resolution_order: List[str]) -> Optional[InformationSource]:
    source_list = [key for key, value in sources.__dict__.items() if value]
    for entry in resolution_order:
        if entry.lower().replace(" ", "_") in source_list:
            return InformationSource.load(entry)
    return None


def get_source(sources, information_source: InformationSource) -> Optional[int]:
    if information_source == InformationSource.COMIC_VINE:
        return sources.comicvine
    if information_source == InformationSource.GRAND_COMICS_DATABASE:
        return sources.grand_comics_database
    if information_source == InformationSource.LEAGUE_OF_COMIC_GEEKS:
        return sources.league_of_comic_geeks
    if information_source == InformationSource.MARVEL:
        return sources.marvel
    if information_source == InformationSource.METRON:
        return sources.metron
    return None


def to_metron_info(metadata: Metadata, resolution_order: List[str]) -> MetronInfo:
    information_source = select_primary_source(metadata.issue.sources, resolution_order)
    return MetronInfo(
        id=MetronSource(
            source=information_source, value=get_source(metadata.issue.sources, information_source)
        )
        if information_source
        else None,
        publisher=Resource(
            id=get_source(metadata.publisher.sources, information_source)
            if information_source
            else None,
            value=metadata.publisher.title,
        ),
        series=MetronSeries(
            lang=metadata.issue.language,
            id=get_source(metadata.series.sources, information_source)
            if information_source
            else None,
            name=metadata.series.title,
            sort_name=metadata.series.title,
            volume=metadata.series.volume,
            format=MetronFormat.load(str(metadata.issue.format)),
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
        genres=sorted({GenreResource(value=x) for x in metadata.issue.genres}, alg=ns.NA | ns.G),
        # TODO: Add tags
        story_arcs=sorted(
            {Arc(name=x.title, number=x.number) for x in metadata.issue.story_arcs},
            alg=ns.NA | ns.G,
        ),
        characters=sorted({Resource(value=x) for x in metadata.issue.characters}, alg=ns.NA | ns.G),
        teams=sorted({Resource(value=x) for x in metadata.issue.teams}, alg=ns.NA | ns.G),
        locations=sorted({Resource(value=x) for x in metadata.issue.locations}, alg=ns.NA | ns.G),
        # TODO: Add reprints
        # TODO: Add GTIN - ISBN & UPC
        credits=sorted(
            {
                Credit(
                    creator=Resource(value=x.name),
                    roles=sorted(
                        {RoleResource(value=Role.load(str(r))) for r in x.roles}, alg=ns.NA | ns.G
                    ),
                )
                for x in metadata.issue.creators
            },
            alg=ns.NA | ns.G,
        ),
        pages=sorted(
            {
                Page(
                    image=x.image,
                    page_type=x.page_type,
                    double_page=x.double_page,
                    image_size=x.image_size,
                    key=x.key,
                    bookmark=x.bookmark,
                    image_width=x.image_width,
                    image_height=x.image_height,
                )
                for x in metadata.pages
            },
            alg=ns.NA | ns.G,
        ),
    )
