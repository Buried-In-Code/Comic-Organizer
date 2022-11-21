from pathlib import Path

from dex_starr import setup_logging
from dex_starr.models.comic_info.schema import ComicInfo
from dex_starr.models.metadata.schema import Metadata
from dex_starr.models.metron_info.schema import MetronInfo
from dex_starr.models.utils import to_comic_info, to_metron_info

FILES_FOLDER = Path(__file__).parent / "files"


def output_folder() -> Path:
    temp = Path(__file__).parent / "output"
    temp.mkdir(parents=True, exist_ok=True)
    return temp


def generate_metadata():
    metadata_file = FILES_FOLDER / "Metadata.xml"
    metadata = Metadata.from_file(metadata_file)
    metadata.to_file(output_folder() / "Metadata.xml")


def generate_metadata_from_comic_info():
    comic_info_file = FILES_FOLDER / "ComicInfo.xml"
    metadata = ComicInfo.from_file(comic_info_file).to_metadata()
    metadata.to_file(output_folder() / "Metadata-ComicInfo.xml")


def generate_metadata_from_metron_info():
    metron_info_file = FILES_FOLDER / "MetronInfo.xml"
    metadata = MetronInfo.from_file(metron_info_file).to_metadata()
    metadata.to_file(output_folder() / "Metadata-MetronInfo.xml")


def generate_comic_info():
    comic_info_file = FILES_FOLDER / "ComicInfo.xml"
    comic_info = ComicInfo.from_file(comic_info_file)
    comic_info.to_file(output_folder() / "ComicInfo.xml")


def generate_comic_info_from_metadata():
    metadata_file = FILES_FOLDER / "Metadata.xml"
    comic_info = to_comic_info(Metadata.from_file(metadata_file))
    comic_info.to_file(output_folder() / "ComicInfo-Metadata.xml")


def generate_metron_info():
    metron_info_file = FILES_FOLDER / "MetronInfo.xml"
    metron_info = MetronInfo.from_file(metron_info_file)
    metron_info.to_file(output_folder() / "MetronInfo.xml")


def generate_metron_info_from_metadata():
    metadata_file = FILES_FOLDER / "Metadata.xml"
    metron_info = to_metron_info(
        Metadata.from_file(metadata_file),
        ["Marvel", "League of Comic Geeks", "Metron", "Grand Comics Database", "Comicvine"],
    )
    metron_info.to_file(output_folder() / "MetronInfo-Metadata.xml")


def main():
    setup_logging()
    generate_metadata()
    generate_metadata_from_comic_info()
    generate_metadata_from_metron_info()
    generate_comic_info()
    generate_comic_info_from_metadata()
    generate_metron_info()
    generate_metron_info_from_metadata()


if __name__ == "__main__":
    main()
