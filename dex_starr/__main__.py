from argparse import ArgumentParser, Namespace
from typing import Dict, List, Optional, Union

from pydantic import ValidationError
from rich import box
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax

from dex_starr import (
    SUPPORTED_FILE_EXTENSIONS,
    SUPPORTED_IMAGE_EXTENSIONS,
    __version__,
    del_folder,
    get_cache_root,
    list_files,
    setup_logging,
)
from dex_starr.archive import Archive
from dex_starr.console import CONSOLE
from dex_starr.models.comic_info.schema import ComicInfo
from dex_starr.models.metadata.schema import Metadata
from dex_starr.models.metron_info.schema import MetronInfo
from dex_starr.models.utils import create_metadata, to_comic_info, to_metron_info
from dex_starr.services.comicvine import SimyanTalker
from dex_starr.services.league_of_comic_geeks import HimonTalker
from dex_starr.services.marvel import EsakTalker
from dex_starr.services.metron import MokkariTalker
from dex_starr.settings import Settings


def read_info_file(archive: Archive) -> Optional[Metadata]:
    info_file = archive.extracted_folder / "Metadata.json"
    if info_file.exists():
        try:
            CONSOLE.print("Parsing Metadata.json", style="logging.level.debug")
            return Metadata.from_file(info_file)
        except ValidationError as err:
            CONSOLE.print(f"Unable to parse Metadata.json: {err}", style="logging.level.warning")
    info_file = archive.extracted_folder / "MetronInfo.xml"
    if info_file.exists():
        try:
            CONSOLE.print("Parsing MetronInfo.xml", style="logging.level.debug")
            metron_info = MetronInfo.from_file(info_file)
            try:
                return metron_info.to_metadata()
            except ValidationError as err:
                CONSOLE.print(
                    f"Unable to convert to Metadata: {err}", style="logging.level.warning"
                )
        except ValidationError as err:
            CONSOLE.print(f"Unable to parse MetronInfo.xml: {err}", style="logging.level.warning")
    info_file = archive.extracted_folder / "ComicInfo.xml"
    if info_file.exists():
        try:
            CONSOLE.print("Parsing ComicInfo.xml", style="logging.level.debug")
            comic_info = ComicInfo.from_file(info_file)
            try:
                return comic_info.to_metadata()
            except ValidationError as err:
                CONSOLE.print(
                    f"Unable to convert to Metadata: {err}", style="logging.level.warning"
                )
        except ValidationError as err:
            CONSOLE.print(f"Unable to parse ComicInfo.xml: {err}", style="logging.level.warning")
    return None


def write_info_file(archive: Archive, settings: Settings, metadata: Metadata):
    if settings.general.generate_metadata_file:
        CONSOLE.print("Generating Metadata.json", style="logging.level.debug")
        metadata.to_file(archive.extracted_folder / "Metadata.json")
    if settings.metron.generate_metroninfo_file:
        CONSOLE.print("Generating MetronInfo.xml", style="logging.level.debug")
        metron_info = to_metron_info(metadata, settings.general.resolution_order)
        metron_info.to_file(archive.extracted_folder / "MetronInfo.xml")
    if settings.general.generate_comicinfo_file:
        CONSOLE.print("Generating ComicInfo.xml", style="logging.level.debug")
        comic_info = to_comic_info(metadata)
        comic_info.to_file(archive.extracted_folder / "ComicInfo.xml")


def pull_info(
    metadata: Metadata,
    services: Dict[str, Union[HimonTalker, MokkariTalker, SimyanTalker, EsakTalker]],
    resolution_order: List[str] = None,
    resolve_manually: bool = False,
):
    if not resolution_order:
        resolution_order = []
    for service in reversed(resolution_order):
        if service not in services or not services[service]:
            continue
        if service == "Marvel" and not metadata.publisher.title.startswith("Marvel"):
            continue
        CONSOLE.rule(f"[bold blue]Pulling from {service}[/]", style="dim blue")
        services[service].update_metadata(metadata)


def clean_cache():
    for child in get_cache_root().iterdir():
        if child.is_dir():
            del_folder(child)
        elif child.name != "cache.sqlite":
            child.unlink(missing_ok=True)


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog="Dex-Starr")
    parser.version = __version__
    parser.add_argument("--manual-edit", action="store_true")
    parser.add_argument("--version", action="version")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main():
    args = parse_arguments()
    setup_logging(args.debug)

    CONSOLE.print(
        Panel.fit(
            "Welcome to Dex-Starr",
            subtitle=f"v{__version__}",
            box=box.SQUARE,
            style="title",
            border_style="title.border",
        ),
        justify="center",
    )
    settings = Settings.load()
    settings.save()

    services = {}
    if settings.comicvine.api_key:
        services["Comicvine"] = SimyanTalker(settings=settings.comicvine)
    if settings.metron.username and settings.metron.password:
        services["Metron"] = MokkariTalker(settings=settings.metron)
    if settings.league_of_comic_geeks.client_id and settings.league_of_comic_geeks.client_secret:
        services["League of Comic Geeks"] = HimonTalker(settings=settings.league_of_comic_geeks)
    if settings.marvel.public_key and settings.marvel.private_key:
        services["Marvel"] = EsakTalker(settings=settings.marvel)
    settings.save()

    clean_cache()

    try:
        for archive_file in list_files(
            settings.general.import_folder, filter_=SUPPORTED_FILE_EXTENSIONS
        ):
            CONSOLE.rule(f"[title]Importing {archive_file.name}[/]", style="subtitle.border")
            archive = Archive(archive_file)

            if not archive.extract():
                CONSOLE.print(
                    f"Unable to extract: {archive.source_file.name}", style="logging.level.error"
                )
                continue

            metadata = read_info_file(archive)
            if metadata:
                CONSOLE.print(
                    Panel.fit(
                        Syntax(
                            metadata.json(indent=2, ensure_ascii=False),
                            "json",
                            indent_guides=True,
                            theme="ansi_dark",
                            word_wrap=True,
                        ),
                        box=box.SQUARE,
                        border_style="syntax.border",
                    ),
                )
                if not Confirm.ask("Keep Metadata", console=CONSOLE):
                    metadata = None
            if not metadata:
                metadata = create_metadata()
            # region Delete extras
            for child in list_files(archive.extracted_folder):
                if child.suffix not in SUPPORTED_IMAGE_EXTENSIONS:
                    CONSOLE.print(f"Deleting {child.name}", style="logging.level.debug")
                    child.unlink(missing_ok=True)
            # endregion
            pull_info(metadata, services, settings.general.resolution_order)

            if args.manual_edit:
                write_info_file(archive, settings, metadata)
                CONSOLE.print(
                    Panel.fit(
                        Syntax(
                            metadata.json(indent=2, ensure_ascii=False),
                            "json",
                            indent_guides=True,
                            theme="ansi_dark",
                            word_wrap=True,
                        ),
                        box=box.SQUARE,
                        border_style="syntax.border",
                    ),
                )
                CONSOLE.print(
                    f"Metadata file is at: {archive.extracted_folder / 'Metadata.json'}",
                    style="logging.level.info",
                )
                Prompt.ask("Press <Enter> to continue", console=CONSOLE)
                metadata = read_info_file(archive)
            write_info_file(archive, settings, metadata)

            if archive.archive(metadata, settings.general):
                if not args.debug:
                    archive.source_file.unlink(missing_ok=True)
            else:
                CONSOLE.print(
                    f"Unable to archive: {archive.result_file.name}", style="logging.level.error"
                )
            del_folder(archive.extracted_folder)
    except KeyboardInterrupt:
        CONSOLE.print("Shutting down Dex-Starr", style="logging.level.info")


if __name__ == "__main__":
    main()
