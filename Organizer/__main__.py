import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Tuple

import painted_logger

from Organizer import (
    ComicInfo,
    Console,
    PublisherInfo,
    SeriesInfo,
    Settings,
    add_info,
    create_archive,
    extract_archive,
    load_info,
    save_info,
    slugify_comic,
    slugify_publisher,
    slugify_series,
)

LOGGER = logging.getLogger("Organizer")
SETTINGS = Settings()


def list_files(folder: Path, filter: Tuple[str, ...] = ()) -> List[Path]:
    files = []
    for file in folder.iterdir():
        if file.is_dir():
            files.extend(list_files(folder=file, filter=filter))
        elif file.suffix in filter:
            files.append(file)
    return files


def del_folder(folder: Path):
    for child in folder.iterdir():
        if child.is_file():
            child.unlink(missing_ok=True)
        else:
            del_folder(folder=child)
    folder.rmdir()


def slugify(comic_info: ComicInfo) -> Tuple[Path, Path, Path]:
    publisher_folder = SETTINGS.collection_folder.joinpath(slugify_publisher(title=comic_info.series.publisher.title))
    series_folder = publisher_folder.joinpath(
        slugify_series(title=comic_info.series.title, volume=comic_info.series.volume)
    )
    comic_path = series_folder.joinpath(
        slugify_comic(series_slug=series_folder.name, comic_format=comic_info.comic_format, number=comic_info.number)
    )
    return publisher_folder, series_folder, comic_path


def main(
    pull_info: bool,
    show_variants: bool,
    manual_info: bool,
    image_check: bool,
    reset_info: bool,
    debug: bool = False,
):
    Console.display_heading("Welcome to Comic Organizer")
    for comic_file in list_files(
        SETTINGS.import_folder, (".cbz", ".zip", ".cb7", ".7z", ".cba", ".ace", ".cbr", ".rar", ".cbt", ".tar")
    ):
        LOGGER.info(f"Extracting {comic_file.stem}")
        Console.display_sub_heading(comic_file.stem)
        comic_folder = extract_archive(src=comic_file, dest=SETTINGS.processing_folder)
        if not comic_folder:
            continue
        info_files = list_files(comic_folder, (".xml", ".json", ".yaml"))
        if len(info_files) == 1:
            comic_info = load_info(info_files[0])
        elif len(info_files) > 1:
            selected = Console.display_menu(
                items=[x.stem for x in info_files], exit_text="None", prompt="Select Info File"
            )
            if len(info_files) >= selected >= 1:
                comic_info = load_info(info_files[selected - 1])
            else:
                comic_info = None
        else:
            comic_info = None
        if not comic_info:
            publisher = PublisherInfo(title=Console.request_str(prompt="Publisher Title"))
            series = SeriesInfo(publisher=publisher, title=Console.request_str(prompt="Series Title"))
            comic_info = ComicInfo(series=series, number=Console.request_str(prompt="Issue Number") or "1")
        else:
            if not comic_info.series.publisher.title:
                comic_info.series.publisher.title = Console.request_str(prompt="Publisher Title")
            if not comic_info.series.title:
                comic_info.series.title = Console.request_str(prompt="Series Title")
            if not comic_info.number:
                comic_info.number = Console.request_str(prompt="Issue Number")
        if reset_info:
            comic_info.reset()
        if pull_info:
            add_info(settings=SETTINGS, comic_info=comic_info, show_variants=show_variants)
        if manual_info:
            Console.display_text("Manually adding info")
            # comic_info = add_manual_info(comic_info=comic_info, show_variants=show_variants)

        for file in info_files:
            file.unlink(missing_ok=True)

        save_info(file=comic_folder.joinpath("ComicInfo.json"), comic_info=comic_info)

        if image_check:
            Console.request_str(prompt="Press <ENTER> to continue")

        publisher_path, series_path, comic_path = slugify(comic_info=comic_info)
        clean_archive = create_archive(src=comic_folder, filename=comic_path.name)
        if not clean_archive:
            continue

        del_folder(comic_folder)
        comic_file.unlink(missing_ok=True)

        publisher_path.mkdir(parents=True, exist_ok=True)
        series_path.mkdir(parents=True, exist_ok=True)
        clean_comic = series_path.joinpath(f"{comic_path.name}.cbz")
        if not clean_comic.exists():
            clean_archive.rename(clean_comic)
        else:
            LOGGER.error(f"Unable to move the result as a file with the same name already exists: {clean_comic}")
        LOGGER.info(f"Cleaned {clean_comic.stem}")


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog="Comic-Organizer")
    parser.add_argument("--pull-info", action="store_true")
    parser.add_argument("--show-variants", action="store_true")
    parser.add_argument("--add-manual-info", action="store_true")
    parser.add_argument("--manual-image-check", action="store_true")
    parser.add_argument("--reset-info", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_arguments()
        painted_logger.init(
            root_path=Path(__file__).resolve().parent.parent,
            file_level=logging.DEBUG if args.debug else logging.INFO,
            console_level=logging.INFO if args.debug else logging.WARNING,
        )
        main(
            pull_info=args.pull_info,
            show_variants=args.show_variants,
            manual_info=args.add_manual_info,
            image_check=args.manual_image_check,
            reset_info=args.reset_info,
            debug=args.debug,
        )
    except KeyboardInterrupt:
        pass
