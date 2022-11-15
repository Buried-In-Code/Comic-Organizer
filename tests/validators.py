import json
from pathlib import Path

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from lxml import etree
from rich import print


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
