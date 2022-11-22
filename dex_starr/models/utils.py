__all__ = ["create_metadata", "to_comic_info", "to_metron_info"]

from typing import List, Optional, Tuple

from natsort import humansorted as sorted
from natsort import ns
from rich.prompt import IntPrompt, Prompt

from dex_starr.console import CONSOLE, create_menu
from dex_starr.models.comic_info.schema import ComicInfo
from dex_starr.models.metadata.enums import Format
from dex_starr.models.metadata.schema import Issue, Metadata, Publisher, Series, SourceResource
from dex_starr.models.metron_info.schema import MetronInfo


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
    from dex_starr.models.comic_info.enums import PageType
    from dex_starr.models.comic_info.schema import Page

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
                    page_type=PageType.load(str(x.page_type)),
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


def to_metron_info(metadata: Metadata, resolution_order: List[str]) -> MetronInfo:
    from dex_starr.models.metron_info.enums import Format, InformationSource, PageType, Role
    from dex_starr.models.metron_info.schema import (
        Arc,
        Credit,
        GenreResource,
        MetronInfo,
        Page,
        Resource,
        RoleResource,
        Series,
        Source,
    )

    def get_information_source(
        sources: List[str], resolution_order: List[str]
    ) -> Tuple[Optional[InformationSource], Optional[str]]:
        for entry in resolution_order:
            if entry in sources:
                return InformationSource.load(entry), entry
        return None, None

    def get_source_id(primary_source: str, source_list: List[SourceResource]) -> Optional[int]:
        for entry in source_list:
            if str(entry.source) == primary_source:
                return entry.value
        return None

    information_source, primary_source = get_information_source(
        sources=[str(x.source) for x in metadata.issue.sources], resolution_order=resolution_order
    )
    return MetronInfo(
        id=Source(
            source=information_source, value=get_source_id(primary_source, metadata.issue.sources)
        )
        if information_source
        else None,
        publisher=Resource(
            id=get_source_id(primary_source, metadata.publisher.sources)
            if primary_source
            else None,
            value=metadata.publisher.title,
        ),
        series=Series(
            lang=metadata.issue.language,
            id=get_source_id(primary_source, metadata.series.sources) if primary_source else None,
            name=metadata.series.title,
            sort_name=metadata.series.title,
            volume=metadata.series.volume,
            format=Format.load(str(metadata.issue.format)),
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
                    page_type=PageType.load(str(x.page_type)),
                    double_page=x.double_page,
                    key=x.key,
                    bookmark=x.bookmark,
                    image_size=x.image_size,
                    image_width=x.image_width,
                    image_height=x.image_height,
                )
                for x in metadata.pages
            },
            alg=ns.NA | ns.G,
        ),
    )
