import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

import PyLogger
from ComicInfo import add_comicvine_info, add_league_info, add_manual_info, load_comic_info, save_comic_info
from Common import CONFIG, Console, del_folder, get_files, pack, slug_comic, slug_publisher, slug_series, unpack

LOGGER = logging.getLogger('ComicInfo')
PROCESSING = Path(CONFIG['Root Folder']).joinpath('Processing')


def main(input_folder: str, use_yaml: bool = False, manual_image_check: bool = False, add_manual_data: bool = False,
         add_league_data: bool = False, add_comicvine_data: bool = False, show_variants: bool = False,
         debug: bool = False):
    for file in get_files(input_folder):
        LOGGER.info(f"Converting {file.stem}")
        unpacked_folder = unpack(file, PROCESSING)
        if not unpacked_folder:
            continue
        comic_info = load_comic_info(unpacked_folder)
        if not comic_info['Series']['Title']:
            comic_info['Series']['Title'] = Console.display_prompt('Series Title')
        if not comic_info['Comic']['Number']:
            comic_info['Comic']['Number'] = Console.display_prompt('Comic Number') or '1'
        if add_comicvine_data:
            comic_info = add_comicvine_info(comic_info, show_variants)
        if add_league_data:
            comic_info = add_league_info(comic_info, show_variants)
        if add_manual_data:
            comic_info = add_manual_info(comic_info)

        save_comic_info(unpacked_folder, comic_info, use_yaml=use_yaml)

        publisher_slug = slug_publisher(comic_info['Publisher'])
        series_slug = slug_series(comic_info['Series']['Title'], comic_info['Series']['Volume'])
        issue_slug = slug_comic(series_slug, comic_info['Format'], comic_info['Comic']['Number'])

        if manual_image_check:
            Console.display_prompt('Press <ENTER> to continue')

        packed_file = pack(unpacked_folder, issue_slug, use_yaml=use_yaml)
        if not packed_file:
            continue
        del_folder(unpacked_folder)
        file.unlink(missing_ok=True)

        parent_folder = Path(CONFIG['Root Folder']) \
            .joinpath('Collection') \
            .joinpath(publisher_slug) \
            .joinpath(series_slug)
        parent_folder.mkdir(exist_ok=True, parents=True)
        cleaned_file = parent_folder.joinpath(packed_file.name)
        if not cleaned_file.exists():
            packed_file.rename(cleaned_file)
        else:
            LOGGER.error(f"Unable to move the result as a file with the same name already exists: {cleaned_file}")


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog='Comic-Info')
    parser.add_argument('--input-folder', type=str, required=True)
    parser.add_argument('--use-yaml', action='store_true')
    parser.add_argument('--manual-image-check', action='store_true')
    parser.add_argument('--add-manual-data', action='store_true')
    parser.add_argument('--add-league-data', action='store_true')
    parser.add_argument('--add-comicvine-data', action='store_true')
    parser.add_argument('--show-variants', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_arguments()
        PyLogger.init('Comic-Info', console_level=logging.DEBUG if args.debug else logging.INFO)
        main(input_folder=args.input_folder, use_yaml=args.use_yaml, manual_image_check=args.manual_image_check,
             add_manual_data=args.add_manual_data, add_league_data=args.add_league_data,
             add_comicvine_data=args.add_comicvine_data, show_variants=args.show_variants, debug=args.debug)
    except KeyboardInterrupt:
        pass
