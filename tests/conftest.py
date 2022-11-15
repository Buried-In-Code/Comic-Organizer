from pathlib import Path

import pytest

from tests.validators import JsonValidator, XmlValidator


@pytest.fixture(scope="session")
def schemas_folder() -> Path:
    return Path(__file__).parent.parent / "schemas"


@pytest.fixture(scope="session")
def files_folder() -> Path:
    return Path(__file__).parent / "files"


@pytest.fixture(scope="session")
def output_folder() -> Path:
    return Path(__file__).parent / "output"


@pytest.fixture(scope="session")
def metadata_validator(schemas_folder: Path) -> JsonValidator:
    return JsonValidator(schemas_folder / "Metadata.schema.json")


@pytest.fixture(scope="session")
def comic_info_validator(schemas_folder: Path) -> XmlValidator:
    return XmlValidator(schemas_folder / "ComicInfo.xsd")


@pytest.fixture(scope="session")
def metron_info_validator(schemas_folder: Path) -> XmlValidator:
    return XmlValidator(schemas_folder / "MetronInfo.xsd")
