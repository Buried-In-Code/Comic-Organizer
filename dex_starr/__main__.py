from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from rich import inspect
from rich.panel import Panel
from rich.prompt import Prompt

from dex_starr import INFO_EXTENSIONS, __version__, del_folder, list_files
from dex_starr.archive import Archive
from dex_starr.console import CONSOLE
from dex_starr.service import pull_info
from dex_starr.settings import SETTINGS, OutputFormatEnum

COMIC_EXTENSIONS = [".cbz", ".cbr", ".cb7", ".cbt", ".cba"]


def extract_file(file: Path) -> Optional[Archive]:
    CONSOLE.print(f"Extracting {file.stem}", style="logging.level.info")
    archive = Archive(file=file)
    if archive.extract(processing_folder=SETTINGS.processing_folder):
        return archive
    return None


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog="Dex-Starr")
    parser.add_argument(
        "-o", "--set-output-format", choices=[x.get_title() for x in list(OutputFormatEnum)]
    )
    parser.add_argument("-d", "--set-delete-extras", choices=["True", "False"])
    parser.add_argument("--manual-edit", action="store_true")
    parser.add_argument("--resolve-manually", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        inspect(args, console=CONSOLE)
    return args


def main():
    try:
        args = parse_arguments()

        if args.set_output_format:
            SETTINGS.output_format = OutputFormatEnum.get(args.set_output_format)
            SETTINGS.save()
        if args.set_delete_extras:
            SETTINGS.delete_extras = args.set_delete_extras == "True"
            SETTINGS.save()

        CONSOLE.print(
            Panel.fit(f"Welcome to Dex-Starr v{__version__}"), style="bold blue", justify="center"
        )

        for import_file in list_files(folder=SETTINGS.import_folder, filter_=COMIC_EXTENSIONS):
            CONSOLE.rule(f"Importing {import_file.name}", style="cyan")
            archive = Archive(file=import_file)

            CONSOLE.print(f"Extracting {import_file.name}", style="logging.level.info")
            if not archive.extract(processing_folder=SETTINGS.processing_folder):
                inspect(archive, console=CONSOLE)
                CONSOLE.print(f"Unable to extract: {import_file.name}", style="logging.level.error")
                continue

            metadata = archive.parse_info()
            if args.debug:
                inspect(metadata, console=CONSOLE)
            pull_info(metadata=metadata, resolve_manually=args.resolve_manually)
            archive.save_info(metadata=metadata)

            if SETTINGS.delete_extras:
                for file in list_files(folder=archive.extracted_folder, filter_=INFO_EXTENSIONS):
                    if file.name == "ComicInfo." + SETTINGS.output_format.name.lower():
                        continue
                    CONSOLE.print(f"Deleting {file.name}", style="logging.level.info")
                    file.unlink(missing_ok=True)

            if args.manual_edit:
                Prompt.ask("Press <Enter> to continue", console=CONSOLE)
                metadata = archive.parse_info()

            if not archive.archive(metadata=metadata, collection_folder=SETTINGS.collection_folder):
                inspect(archive, console=CONSOLE)
                CONSOLE.print(
                    f"Unable to archive: {archive.result_file.name}", style="logging.level.error"
                )
                continue
            try:
                del_folder(folder=archive.extracted_folder)
                archive.source_file.unlink(missing_ok=True)
            except PermissionError:
                CONSOLE.print(
                    "Unable to clean up files, requires manual intervention",
                    style="logging.level.error",
                )
    except KeyboardInterrupt:
        CONSOLE.print("Shutting down Dex-Starr", style="logging.level.critical")


if __name__ == "__main__":
    main()
