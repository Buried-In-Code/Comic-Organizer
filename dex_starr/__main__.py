import json
import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from simyan.sqlite_cache import SQLiteCache

from dex_starr import SETTINGS, del_folder, list_files, merge_dicts, yaml_setup
from dex_starr.archive import Archive
from dex_starr.comicvine import pull_info as pull_comicvine_info
from dex_starr.console import ConsoleLog
from dex_starr.league_of_comic_geeks_api import pull_info as pull_league_info
from dex_starr.metadata import Metadata, parse_json, parse_xml, parse_yaml
from dex_starr.metron import pull_info as pull_metron_info
from dex_starr.settings import OutputFormatEnum

CONSOLE = ConsoleLog("Dex-Starr")
COMIC_EXTENSIONS = [".cbz", ".cbr", ".cb7", ".cbt", ".cba"]
INFO_EXTENSIONS = [".json", ".xml", ".yaml"]


def save_info(archive: Archive, metadata: Metadata):
    info_file = archive.extracted_folder.joinpath("ComicInfo." + SETTINGS.output_format.name.lower())
    CONSOLE.info(f"Saving Info File as {info_file.name}")

    with info_file.open("w", encoding="UTF-8") as stream:
        if SETTINGS.output_format == OutputFormatEnum.JSON:
            json.dump(metadata.dump(), stream, default=str, indent=2, ensure_ascii=False)
        elif SETTINGS.output_format == OutputFormatEnum.YAML:
            yaml_setup().dump(metadata.dump(), stream)


def pull_info(metadata: Metadata, resolve_manually: bool = False):
    cache = SQLiteCache("Dex-Starr-cache.sqlite")
    pulled_info = {}
    if SETTINGS.comicvine_api_key:
        pulled_info = merge_dicts(pulled_info, pull_comicvine_info(SETTINGS.comicvine_api_key, cache, metadata))
    if SETTINGS.metron_username and SETTINGS.metron_password:
        pulled_info = merge_dicts(
            pulled_info, pull_metron_info(SETTINGS.metron_username, SETTINGS.metron_password, cache, metadata)
        )
    if SETTINGS.league_api_key and SETTINGS.league_client_id:
        pulled_info = merge_dicts(
            pulled_info, pull_league_info(SETTINGS.league_api_key, SETTINGS.league_client_id, cache, metadata)
        )
    metadata.set_pulled_metadata(pulled_info, resolve_manually)


def parse_info(archive: Archive) -> Metadata:
    info_files = list_files(archive.extracted_folder, filter_=INFO_EXTENSIONS)
    CONSOLE.info(f"Info File/s Found: {[x.name for x in info_files]}")
    metadata = None
    if ".json" in [x.suffix for x in info_files]:
        metadata = parse_json([x for x in info_files if x.suffix == ".json"][0])
    elif ".yaml" in [x.suffix for x in info_files]:
        metadata = parse_yaml([x for x in info_files if x.suffix == ".yaml"][0])
    elif ".xml" in [x.suffix for x in info_files]:
        metadata = parse_xml([x for x in info_files if x.suffix == ".xml"][0])
    if not metadata:
        metadata = Metadata.create()
    return metadata


def extract_file(file: Path) -> Optional[Archive]:
    CONSOLE.info(f"Extracting {file.stem}")
    archive = Archive(file=file)
    if archive.extract(processing_folder=SETTINGS.processing_folder):
        return archive
    return None


def setup_logging(debug: bool = False):
    Path("logs").mkdir(exist_ok=True)
    file_handler = logging.FileHandler("logs/Dex-Starr.log")
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] {%(name)s} | %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        level=logging.NOTSET,
        handlers=[file_handler],
    )


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog="Dex-Starr")
    parser.add_argument("-o", "--set-output-format", choices=[x.get_title() for x in list(OutputFormatEnum)])
    parser.add_argument("-d", "--set-delete-extras", choices=["True", "False"])
    parser.add_argument("--manual-edit", action="store_true")
    parser.add_argument("--resolve-manually", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        CONSOLE.debug(object_=args)
    return args


def main():
    args = parse_arguments()
    setup_logging(args.debug)

    if args.set_output_format:
        SETTINGS.output_format = OutputFormatEnum.get(args.set_output_format)
        SETTINGS.save()
    if args.set_delete_extras:
        SETTINGS.delete_extras = args.set_delete_extras == "True"
        SETTINGS.save()

    CONSOLE.panel("Welcome to Dex-Starr", expand=False, style="bold blue")

    for import_file in list_files(folder=SETTINGS.import_folder, filter_=COMIC_EXTENSIONS):
        CONSOLE.rule(f"Importing {import_file.name}", text_style="cyan", line_style="blue")
        archive = Archive(file=import_file)

        CONSOLE.info(f"Extracting {import_file.name}")
        if not archive.extract(processing_folder=SETTINGS.processing_folder):
            CONSOLE.error(f"Unable to extract: {import_file.name}", archive)
            continue

        metadata = parse_info(archive)
        if args.debug:
            CONSOLE.debug(object_=metadata)
        pull_info(metadata, args.resolve_manually)
        save_info(archive, metadata)

        if SETTINGS.delete_extras:
            for file in list_files(archive.extracted_folder, filter_=INFO_EXTENSIONS):
                if file.name == "ComicInfo." + SETTINGS.output_format.name.lower():
                    continue
                CONSOLE.info(f"Deleting {file.name}")
                file.unlink(missing_ok=True)

        if args.manual_edit:
            CONSOLE.prompt("Press <Enter> to continue", require_response=False)
            metadata = parse_info(archive)

        if not archive.archive(metadata, SETTINGS.collection_folder):
            CONSOLE.error(f"Unable to archive: {archive.result_file.name}", archive)
            continue
        try:
            del_folder(archive.extracted_folder)
            archive.source_file.unlink(missing_ok=True)
        except PermissionError:
            CONSOLE.error("Unable to clean up files, requires manual intervention")


if __name__ == "__main__":
    main()
