import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

import PyLogger
from ComicInfo import load_comic_info, save_comic_info, add_league_info
from Common import get_files, del_folder, pack, slug_comic, slug_publisher, slug_series, unpack

LOGGER = logging.getLogger('ComicInfo')
PROCESSING = Path(__file__).parent.parent.joinpath('Processing')


def main(folder: List[str] = None, keep_xml: bool = False, add_league_data: bool = False, show_variants: bool = False,
         manual_edit: bool = False, debug: bool = False):
    convert_files = set()
    for file in folder:
        convert_files |= get_files(file)
    LOGGER.debug(convert_files)
    for file in convert_files:
        LOGGER.info(f"Converting {file.stem}")
        unpacked_folder = unpack(file, PROCESSING)
        if not unpacked_folder:
            continue
        comic_info = load_comic_info(unpacked_folder, keep_xml)
        if add_league_data:
            add_league_info(comic_info, show_variants)
            # TODO: Add League of Comic Geeks data to ComicInfo
            pass
        if manual_edit:
            # TODO: Manually Edit fields in ComicInfo
            pass

        save_comic_info(unpacked_folder, comic_info)

        publisher_slug = slug_publisher(comic_info['Publisher'])
        series_slug = slug_series(comic_info['Series']['Title'], comic_info['Series']['Volume'])
        issue_slug = slug_comic(series_slug, comic_info['Format'], comic_info['Comic']['Number'])
        cleaned_file = pack(unpacked_folder, issue_slug, keep_xml)
        if not cleaned_file:
            continue
        del_folder(unpacked_folder)

        returned_file = file.parent.joinpath(cleaned_file.name)
        if not returned_file.exists():
            cleaned_file.rename(returned_file)
        else:
            LOGGER.error(f"Unable to move the result as a file with the same name already exists: {returned_file}")


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog='Comic-Info')
    parser.add_argument('folder', action='extend', type=str, nargs='+')
    parser.add_argument('--keep-xml', action='store_true')
    parser.add_argument('--add-league-data', action='store_true')
    parser.add_argument('--show-variants', action='store_true')
    parser.add_argument('--manual-edit', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    PyLogger.init('Comic-Info', console_level=logging.DEBUG if args.debug else logging.INFO)
    main(folder=args.folder, keep_xml=args.keep_xml, add_league_data=args.add_league_data,
         show_variants=args.show_variants, manual_edit=args.manual_edit, debug=args.debug)
