import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

import PyLogger
from Organizer import add_comicvine_info, add_league_info, add_manual_info, CONFIG, Console, del_folder, get_files, \
    load_comic_info, pack, save_comic_info, slug_comic, slug_publisher, slug_series, unpack, add_metron_info

LOGGER = logging.getLogger('Comic-Organizer')
PROCESSING = Path(CONFIG['Root Folder']).joinpath('Processing')


def main(input_folder: str, manual_image_check: bool = False, add_manual_data: bool = False, show_variants: bool = False, debug: bool = False):
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
        LOGGER.info(f"Looking up {file.stem} in Metron DB")
        comic_info = add_metron_info(comic_info, show_variants)
        continue
        # if add_comicvine_data:
        #     LOGGER.info(f"Looking up {file.stem} in Comicvine DB")
        #     comic_info = add_comicvine_info(comic_info, show_variants)
        # if add_league_data:
        #     LOGGER.info(f"Looking up {file.stem} in League of Comic Geeks DB")
        #     comic_info = add_league_info(comic_info, show_variants)
        # if add_manual_data:
        #     LOGGER.info(f"Preparing Manual steps for {file.stem} data entry")
        #     comic_info = add_manual_info(comic_info)
        #
        # save_comic_info(unpacked_folder, comic_info, use_yaml=use_yaml)
        #
        # publisher_slug = slug_publisher(comic_info['Publisher'])
        # series_slug = slug_series(comic_info['Series']['Title'], comic_info['Series']['Volume'])
        # issue_slug = slug_comic(series_slug, comic_info['Format'], comic_info['Comic']['Number'])
        #
        # if manual_image_check:
        #     Console.display_prompt('Press <ENTER> to continue')
        #
        # packed_file = pack(unpacked_folder, issue_slug, use_yaml=use_yaml)
        # if not packed_file:
        #     continue
        # LOGGER.info(f"Cleaning up {unpacked_folder}")
        # del_folder(unpacked_folder)
        # LOGGER.info(f"Cleaning up {file}")
        # file.unlink(missing_ok=True)
        #
        # parent_folder = Path(CONFIG['Root Folder']) \
        #     .joinpath('Collection') \
        #     .joinpath(publisher_slug) \
        #     .joinpath(series_slug)
        # parent_folder.mkdir(exist_ok=True, parents=True)
        # cleaned_file = parent_folder.joinpath(packed_file.name)
        # if not cleaned_file.exists():
        #     Console.display(f"Moving `{cleaned_file}` to Collection")
        #     packed_file.rename(cleaned_file)
        # else:
        #     LOGGER.error(f"Unable to move the result as a file with the same name already exists: {cleaned_file}")
        # LOGGER.info(f"Finished converting {file.stem}")


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog='Comic-Organizer')
    parser.add_argument('--input-folder', type=str, required=True)
    parser.add_argument('--manual-image-check', action='store_true')
    parser.add_argument('--add-manual-data', action='store_true')
    parser.add_argument('--show-variants', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_arguments()
        PyLogger.init('Comic-Organizer', console_level=logging.DEBUG if args.debug else logging.INFO)
        main(input_folder=args.input_folder, manual_image_check=args.manual_image_check, add_manual_data=args.add_manual_data, show_variants=args.show_variants, debug=args.debug)
    except KeyboardInterrupt:
        pass
