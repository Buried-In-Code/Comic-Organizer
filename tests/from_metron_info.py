import json
from pathlib import Path
from typing import Tuple

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from lxml import etree
from rich import print

from dex_starr import get_project_root
from dex_starr.schemas.metron_info import MetronInfo
from dex_starr.schemas.utils import to_comic_info


class JsonValidator:
    def __init__(self, schema_path: Path):
        with schema_path.open("r") as stream:
            self.schema = json.load(stream)

    def validate(self, json_path: Path) -> bool:
        with json_path.open("r") as stream:
            data = json.load(stream)
        try:
            validate(instance=data, schema=self.schema)
            return True
        except ValidationError as err:
            print(err)
        return False


class XmlValidator:
    def __init__(self, xsd_path: Path):
        xsd_doc = etree.parse(xsd_path)
        self.xsd = etree.XMLSchema(xsd_doc)

    def validate(self, xml_path: Path) -> bool:
        xml_doc = etree.parse(xml_path)
        return self.xsd.validate(xml_doc)


SCHEMAS_ROOT = get_project_root() / "schemas"
TESTS_ROOT = get_project_root() / "tests"
metadata_validator = JsonValidator(SCHEMAS_ROOT / "Metadata.schema.json")
comic_info_validator = XmlValidator(SCHEMAS_ROOT / "ComicInfo.xsd")
metron_info_validator = XmlValidator(SCHEMAS_ROOT / "MetronInfo.xsd")


def load_metron_info() -> Tuple[Path, MetronInfo]:
    metron_info_file = TESTS_ROOT / "MetronInfo.xml"
    return metron_info_file, MetronInfo.from_file(metron_info_file)


def validate_metadata():
    _, metron_info = load_metron_info()
    metadata_file = TESTS_ROOT / "Metadata_from-metron-info.json"
    metadata_file.unlink(missing_ok=True)
    metron_info.to_metadata().to_file(metadata_file)
    if metadata_validator.validate(metadata_file):
        print("Valid Metadata")
    else:
        print("Invalid Metadata")


def validate_comic_info():
    _, metron_info = load_metron_info()
    comic_info_file = TESTS_ROOT / "ComicInfo_from-metron-info.xml"
    comic_info_file.unlink(missing_ok=True)
    to_comic_info(metron_info.to_metadata()).to_file(comic_info_file)
    if comic_info_validator.validate(comic_info_file):
        print("Valid ComicInfo")
    else:
        print("Invalid ComicInfo")
        for error in comic_info_validator.xsd.error_log.filter_from_errors():
            print(f" - {error.path}: {error.message}")


def validate_metron_info():
    metron_info_file, _ = load_metron_info()
    if metron_info_validator.validate(metron_info_file):
        print("Valid MetronInfo")
    else:
        print("Invalid MetronInfo")
        for error in metron_info_validator.xsd.error_log.filter_from_errors():
            print(f" - {error.path}: {error.message}")


if __name__ == "__main__":
    validate_metadata()
    validate_comic_info()
    validate_metron_info()
