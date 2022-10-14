import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, List, Union

from pathvalidate.argparse import sanitize_filepath_arg
from pydantic import ValidationError
from rich import box
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Prompt

from . import (
    IMAGE_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    __version__,
    del_folder,
    filter_files,
    get_cache_root,
    list_files,
)
from .archive import Archive
from .console import CONSOLE
from .metadata.comic_info import ComicInfo
from .metadata.metadata import Metadata
from .metadata.metron_info import MetronInfo
from .metadata.utils import create_metadata, to_comic_info, to_metron_info
from .services.esak import EsakTalker
from .services.himon import HimonTalker
from .services.mokkari import MokkariTalker
from .services.simyan import SimyanTalker
from .settings import Settings


def read_info_file(archive: Archive) -> Metadata:
    info_file = archive.extracted_folder / "Metadata.json"
    if info_file.exists():
        try:
            CONSOLE.print("Parsing Metadata.json", style="logging.level.debug")
            return Metadata.from_file(info_file)
        except ValidationError:
            CONSOLE.print("Unable to parse Metadata.json", style="logging.level.warning")
    info_file = archive.extracted_folder / "MetronInfo.xml"
    if info_file.exists():
        try:
            CONSOLE.print("Parsing MetronInfo.xml", style="logging.level.debug")
            metron_info = MetronInfo.from_file(info_file)
            return metron_info.to_metadata()
        except ValidationError:
            CONSOLE.print("Unable to parse MetronInfo.xml", style="logging.level.warning")
    info_file = archive.extracted_folder / "ComicInfo.xml"
    if info_file.exists():
        try:
            CONSOLE.print("Parsing ComicInfo.xml", style="logging.level.debug")
            comic_info = ComicInfo.from_file(info_file)
            return comic_info.to_metadata()
        except ValidationError:
            CONSOLE.print("Unable to parse ComicInfo.xml", style="logging.level.warning")
    return create_metadata()


def write_info_file(archive: Archive, settings: Settings, metadata: Metadata):
    if settings.general.generate_metadata_file:
        metadata.to_file(archive.extracted_folder / "Metadata.json")
    if settings.metron.generate_info_file:
        metron_info = to_metron_info(metadata, settings.general.resolution_order)
        metron_info.to_file(archive.extracted_folder / "MetronInfo.xml")
    if settings.general.generate_comicinfo_file:
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
        CONSOLE.print(f"Pulling from {service}", style="bold blue")
        services[service].update_metadata(metadata)


def setup_logging(debug: bool = False):
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                log_time_format="[%Y-%m-%d %H:%M:%S]",
                omit_repeated_times=False,
                console=CONSOLE,
            )
        ],
    )


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog="Dex-Starr")
    parser.add_argument("import_folder", type=sanitize_filepath_arg)
    parser.add_argument("--manual-edit", action="store_true")
    parser.add_argument("--resolve-manually", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main():
    args = parse_arguments()
    setup_logging(args.debug)

    CONSOLE.print(
        Panel.fit("Welcome to Dex-Starr", subtitle=f"v{__version__}", box=box.SQUARE),
        style="bold magenta",
        justify="center",
    )
    settings = Settings.load()
    settings.save()

    services = {}
    if settings.comicvine.api_key:
        services["Comicvine"] = SimyanTalker(api_key=settings.comicvine.api_key)
    if settings.metron.username and settings.metron.password:
        services["Metron"] = MokkariTalker(
            username=settings.metron.username, password=settings.metron.password
        )
    if settings.league_of_comic_geeks.api_key and settings.league_of_comic_geeks.client_id:
        services["League of Comic Geeks"] = HimonTalker(
            api_key=settings.league_of_comic_geeks.api_key,
            client_id=settings.league_of_comic_geeks.client_id,
        )
    if settings.marvel.public_key and settings.marvel.private_key:
        services["Marvel"] = EsakTalker(
            public_key=settings.marvel.public_key, private_key=settings.marvel.private_key
        )

    # region Clean cache
    for child in get_cache_root().iterdir():
        if child.is_dir():
            del_folder(child)
        elif child.name != "cache.sqlite":
            child.unlink(missing_ok=True)
    # endregion

    try:
        for archive_file in filter_files(
            Path(args.import_folder).resolve(), filter_=SUPPORTED_EXTENSIONS
        ):
            CONSOLE.rule(f"[bold blue]Importing {archive_file.name}[/]", style="dim blue")
            archive = Archive(archive_file)

            if not archive.extract():
                CONSOLE.print(
                    f"Unable to extract: {archive.source_file}", style="logging.level.warning"
                )
                continue

            metadata = read_info_file(archive)
            # region Delete extras
            for child in list_files(archive.extracted_folder):
                if child.suffix not in IMAGE_EXTENSIONS:
                    CONSOLE.print(f"Deleting {child.name}", style="logging.level.debug")
                    child.unlink(missing_ok=True)
            # endregion
            pull_info(metadata, services, settings.general.resolution_order, args.resolve_manually)

            if args.manual_edit:
                write_info_file(archive, settings, metadata)
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
