from pathlib import Path

from rich import print

from dex_starr.schemas.comic_info.schema import ComicInfo
from dex_starr.schemas.metadata.schema import Metadata
from dex_starr.schemas.metron_info.schema import MetronInfo
from dex_starr.schemas.utils import to_comic_info, to_metron_info
from tests.validators import JsonValidator, XmlValidator


def test_parsing_metadata(files_folder: Path, metadata_validator: JsonValidator):
    metadata_file = files_folder / "Metadata.json"
    assert metadata_validator.validate(metadata_file)


def test_parsing_comic_info(files_folder: Path, comic_info_validator: XmlValidator):
    comic_info_file = files_folder / "ComicInfo.xml"
    valid = comic_info_validator.validate(comic_info_file)
    if not valid:
        print("Invalid ComicInfo")
        for error in comic_info_validator.xsd.error_log.filter_from_errors():
            print(f" - {error.path}: {error.message}")
    assert valid


def test_parsing_metron_info(files_folder: Path, metron_info_validator: XmlValidator):
    metron_info_file = files_folder / "MetronInfo.xml"
    valid = metron_info_validator.validate(metron_info_file)
    if not valid:
        print("Invalid MetronInfo")
        for error in metron_info_validator.xsd.error_log.filter_from_errors():
            print(f" - {error.path}: {error.message}")
    assert valid


def test_converting_to_comic_info(
    files_folder: Path, output_folder: Path, comic_info_validator: XmlValidator
):
    metadata = Metadata.from_file(files_folder / "Metadata.json")
    comic_info_file = output_folder / "ComicInfo.xml"
    comic_info_file.unlink(missing_ok=True)
    to_comic_info(metadata).to_file(comic_info_file)
    valid = comic_info_validator.validate(comic_info_file)
    if not valid:
        print("Invalid ComicInfo")
        for error in comic_info_validator.xsd.error_log.filter_from_errors():
            print(f" - {error.path}: {error.message}")
    assert valid


def test_converting_from_comic_info(
    files_folder: Path, output_folder: Path, metadata_validator: JsonValidator
):
    comic_info = ComicInfo.from_file(files_folder / "ComicInfo.xml")
    metadata_file = output_folder / "Metadata-ComicInfo.json"
    metadata_file.unlink(missing_ok=True)
    comic_info.to_metadata().to_file(metadata_file)
    assert metadata_validator.validate(metadata_file)


def test_converting_to_metron_info(
    files_folder: Path, output_folder: Path, metron_info_validator: XmlValidator
):
    metadata = Metadata.from_file(files_folder / "Metadata.json")
    metron_info_file = output_folder / "MetronInfo.xml"
    metron_info_file.unlink(missing_ok=True)
    to_metron_info(metadata, ["League of Comic Geeks", "Marvel", "Metron", "Comicvine"]).to_file(
        metron_info_file
    )
    valid = metron_info_validator.validate(metron_info_file)
    if not valid:
        print("Invalid MetronInfo")
        for error in metron_info_validator.xsd.error_log.filter_from_errors():
            print(f" - {error.path}: {error.message}")
    assert valid


def test_converting_from_metron_info(
    files_folder: Path, output_folder: Path, metadata_validator: JsonValidator
):
    metron_info = MetronInfo.from_file(files_folder / "MetronInfo.xml")
    metadata_file = output_folder / "Metadata-MetronInfo.json"
    metadata_file.unlink(missing_ok=True)
    metron_info.to_metadata().to_file(metadata_file)
    assert metadata_validator.validate(metadata_file)
