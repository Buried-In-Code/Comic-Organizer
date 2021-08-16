import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

import PyLogger
from Organizer import Console, PROCESSING_FOLDER, COLLECTION_FOLDER, list_files, del_folder, extract_archive, \
    create_archive, PublisherInfo, SeriesInfo, ComicInfo, load_info, save_info, slugify_publisher, slugify_series, \
    slugify_comic, add_comicvine_info, add_league_info, add_metron_info, COMICVINE_API_KEY, LOCG_API_KEY, \
    LOCG_CLIENT_ID, METRON_USERNAME, METRON_PASSWORD

LOGGER = logging.getLogger('Organizer')


def main(input_path: str, pull_info: bool, show_variants: bool, manual_info: bool, image_check: bool, reset_info: bool, debug: bool = False):
    Console.display_heading('Welcome to Comic Organizer')
    input_folder = Path(input_path).resolve()
    if not input_folder.exists():
        LOGGER.error(f"Invalid Input Folder: `{input_folder}`")
        return
    for comic_file in list_files(input_folder, ('.cbr', '.cbz',)):
        LOGGER.info(f"Extracting {comic_file.stem}")
        Console.display_sub_heading(comic_file.stem)
        comic_folder = extract_archive(src=comic_file, dest=PROCESSING_FOLDER)
        if not comic_folder:
            continue
        info_files = list_files(comic_folder, ('.xml', '.json', '.yaml',))
        if len(info_files) == 1:
            comic_info = load_info(info_files[0])
        elif len(info_files) > 1:
            selected = Console.display_menu(items=[x.stem for x in info_files], exit_text='None', prompt='Select Info File')
            if len(info_files) >= selected >= 1:
                comic_info = load_info(info_files[selected - 1])
            else:
                comic_info = None
        else:
            comic_info = None
        if not comic_info:
            publisher = PublisherInfo(
                title=Console.request_str(prompt='Publisher Title')
            )
            series = SeriesInfo(
                publisher=publisher,
                start_year=Console.request_int(prompt='Series Start Year') or 2020,
                title=Console.request_str(prompt='Series Title'),
                volume=Console.request_int(prompt='Series Volume') or 1
            )
            comic_info = ComicInfo(
                series=series,
                number=Console.request_str(prompt='Issue Number') or '1'
            )
        else:
            if not comic_info.series.publisher.title:
                comic_info.series.publisher.title = Console.request_str(prompt='Publisher Title')
            if not comic_info.series.title:
                comic_info.series.title = Console.request_str(prompt='Series Title')
            if not comic_info.number:
                comic_info.number = Console.request_str(prompt='Issue Number')
        if reset_info:
            comic_info.reset()
        if pull_info:
            if LOCG_API_KEY and LOCG_CLIENT_ID:
                Console.display_item_value(item='Pulling info from', value='League of Comic Geeks')
                comic_info = add_league_info(comic_info=comic_info, show_variants=show_variants)
            if METRON_USERNAME and METRON_PASSWORD:
                Console.display_item_value(item='Pulling info from', value='Metron')
                comic_info = add_metron_info(comic_info=comic_info)
            if COMICVINE_API_KEY:
                Console.display_item_value(item='Pulling info from', value='Comicvine')
                comic_info = add_comicvine_info(comic_info=comic_info)
        if manual_info:
            Console.display_text('Manually adding info')
            # comic_info = add_manual_info(comic_info=comic_info, show_variants=show_variants)

        for file in info_files:
            file.unlink(missing_ok=True)

        save_info(file=comic_folder.joinpath('ComicInfo.json'), comic_info=comic_info)
        publisher_folder = COLLECTION_FOLDER.joinpath(slugify_publisher(title=comic_info.series.publisher.title))
        series_folder = publisher_folder.joinpath(slugify_series(title=comic_info.series.title, volume=comic_info.series.volume))
        comic_file_path = series_folder.joinpath(slugify_comic(series_slug=series_folder.name, comic_format=comic_info.comic_format, number=comic_info.number))
        if image_check:
            Console.request_str(prompt='Press <ENTER> to continue')

        clean_archive = create_archive(src=comic_folder, filename=comic_file_path.name)
        if not clean_archive:
            continue

        del_folder(comic_folder)
        comic_file.unlink(missing_ok=True)

        publisher_folder.mkdir(parents=True, exist_ok=True)
        series_folder.mkdir(parents=True, exist_ok=True)
        clean_comic = series_folder.joinpath(f"{comic_file_path.name}.cbz")
        if not clean_comic.exists():
            clean_archive.rename(clean_comic)
        else:
            LOGGER.error(f"Unable to move the result as a file with the same name already exists: {clean_comic}")
        LOGGER.info(f"Cleaned {clean_comic.stem}")


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog='Comic-Organizer')
    parser.add_argument('--input-folder', type=str, required=True)
    parser.add_argument('--pull-info', action='store_true')
    parser.add_argument('--show-variants', action='store_true')
    parser.add_argument('--add-manual-info', action='store_true')
    parser.add_argument('--manual-image-check', action='store_true')
    parser.add_argument('--reset-info', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_arguments()
        PyLogger.init('Comic-Organizer', file_level=logging.DEBUG if args.debug else logging.INFO, console_level=logging.INFO if args.debug else logging.WARNING)
        main(input_path=args.input_folder, pull_info=args.pull_info, show_variants=args.show_variants, manual_info=args.add_manual_info, image_check=args.manual_image_check,
             reset_info=args.reset_info, debug=args.debug)
    except KeyboardInterrupt:
        pass
