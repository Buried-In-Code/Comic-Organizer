import logging
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Union

from pydantic import ValidationError
from rich import box
from rich.panel import Panel
from rich.prompt import Prompt

from dex_starr import (
    IMAGE_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    __version__,
    del_folder,
    filter_files,
    get_cache_root,
    list_files,
    setup_logging,
)
from dex_starr.archive import Archive
from dex_starr.console import CONSOLE, RichLogger
from dex_starr.models.comic_info.schema import ComicInfo
from dex_starr.models.metadata.schema import Metadata
from dex_starr.models.metron_info.schema import MetronInfo
from dex_starr.models.utils import create_metadata, to_comic_info, to_metron_info
from dex_starr.services.comicvine import SimyanTalker
from dex_starr.services.league_of_comic_geeks import HimonTalker
from dex_starr.services.marvel import EsakTalker
from dex_starr.services.metron import MokkariTalker
from dex_starr.settings import Settings

LOGGER = RichLogger(logging.getLogger("Dex-Starr"))


def read_info_file(archive: Archive) -> Metadata:
    info_file = archive.extracted_folder / "Metadata.json"
    if info_file.exists():
        try:
            LOGGER.debug("Parsing Metadata.json")
            return Metadata.from_file(info_file)
        except ValidationError as err:
            LOGGER.warning(f"Unable to parse Metadata.json: {err}")
    info_file = archive.extracted_folder / "MetronInfo.xml"
    if info_file.exists():
        try:
            LOGGER.debug("Parsing MetronInfo.xml")
            metron_info = MetronInfo.from_file(info_file)
            return metron_info.to_metadata()
        except ValidationError as err:
            LOGGER.warning(f"Unable to parse MetronInfo.xml: {err}")
    info_file = archive.extracted_folder / "ComicInfo.xml"
    if info_file.exists():
        try:
            LOGGER.debug("Parsing ComicInfo.xml")
            comic_info = ComicInfo.from_file(info_file)
            return comic_info.to_metadata()
        except ValidationError as err:
            LOGGER.warning(f"Unable to parse ComicInfo.xml: {err}")
    return create_metadata()


def write_info_file(archive: Archive, settings: Settings, metadata: Metadata):
    if settings.general.generate_metadata_file:
        metadata.to_file(archive.extracted_folder / "Metadata.json")
    if settings.metron.generate_metroninfo_file:
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


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog="Dex-Starr")
    parser.version = __version__
    parser.add_argument("--manual-edit", action="store_true")
    parser.add_argument("--resolve-manually", action="store_true")
    parser.add_argument("--version", action="version")
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
        services["Comicvine"] = SimyanTalker(settings=settings.comicvine)
    if settings.metron.username and settings.metron.password:
        services["Metron"] = MokkariTalker(settings=settings.metron)
    if settings.league_of_comic_geeks.client_id and settings.league_of_comic_geeks.client_secret:
        services["League of Comic Geeks"] = HimonTalker(settings=settings.league_of_comic_geeks)
    if settings.marvel.public_key and settings.marvel.private_key:
        services["Marvel"] = EsakTalker(settings=settings.marvel)
    settings.save()

    # region Clean cache
    for child in get_cache_root().iterdir():
        if child.is_dir():
            del_folder(child)
        elif child.name != "cache.sqlite":
            child.unlink(missing_ok=True)
    # endregion

    try:
        for archive_file in filter_files(
            settings.general.import_folder, filter_=SUPPORTED_EXTENSIONS
        ):
            CONSOLE.rule(f"[bold blue]Importing {archive_file.name}[/]", style="dim blue")
            archive = Archive(archive_file)

            if not archive.extract():
                LOGGER.error(f"Unable to extract: {archive.source_file.name}")
                continue

            metadata = read_info_file(archive)
            # region Delete extras
            for child in list_files(archive.extracted_folder):
                if child.suffix not in IMAGE_EXTENSIONS:
                    LOGGER.debug(f"Deleting {child.name}")
                    child.unlink(missing_ok=True)
            # endregion
            pull_info(metadata, services, settings.general.resolution_order, args.resolve_manually)

            if args.manual_edit:
                write_info_file(archive, settings, metadata)
                CONSOLE.print(metadata)
                Prompt.ask("Press <Enter> to continue", console=CONSOLE)
                metadata = read_info_file(archive)
            write_info_file(archive, settings, metadata)

            if archive.archive(metadata, settings.general):
                if not args.debug:
                    archive.source_file.unlink(missing_ok=True)
            else:
                LOGGER.error(f"Unable to archive: {archive.result_file.name}")
            del_folder(archive.extracted_folder)
    except KeyboardInterrupt:
        LOGGER.info("Shutting down Dex-Starr")


if __name__ == "__main__":
    main()
