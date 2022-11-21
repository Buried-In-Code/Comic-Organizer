__all__ = ["PascalModel", "CamelModel", "clean_contents", "xml_lists"]

from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Extra


def to_pascal_case(value: str) -> str:
    return value.replace("_", " ").title().replace(" ", "")


class PascalModel(BaseModel):
    class Config:
        alias_generator = to_pascal_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore


def to_camel_case(value: str) -> str:
    temp = value.replace("_", " ").title().replace(" ", "")
    return temp[0].lower() + temp[1:]


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore


def clean_contents(content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in content.copy().items():
        if isinstance(key, Enum):
            content[str(key)] = value
            del content[key]
        if isinstance(value, bool):
            content[key] = "true" if value else "false"
        elif isinstance(value, Enum) or isinstance(value, int) or isinstance(value, float):
            content[key] = str(value)
        elif isinstance(value, dict):
            if value:
                content[key] = clean_contents(value)
            else:
                del content[key]
        elif isinstance(value, list):
            for index, entry in enumerate(value):
                if isinstance(entry, bool):
                    content[key][index] = "true" if entry else "false"
                elif isinstance(entry, Enum) or isinstance(entry, int) or isinstance(value, float):
                    content[key][index] = str(entry)
                elif isinstance(entry, dict):
                    content[key][index] = clean_contents(entry)
    return content


def xml_lists(mappings: Dict[str, str], content: Dict[str, Any]) -> Dict[str, Any]:
    return to_xml_list(mappings, content)


def to_xml_list(mappings: Dict[str, str], content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in content.copy().items():
        if isinstance(value, dict):
            content[key] = xml_lists(mappings, value)
        elif isinstance(value, list):
            for index, entry in enumerate(value):
                if isinstance(entry, dict):
                    content[key][index] = xml_lists(mappings, entry)
            if key in mappings:
                content[key] = {mappings[key]: content[key]}
    return content


def from_xml_list(mappings: Dict[str, str], content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in mappings.items():
        if key in content and isinstance(content[key], dict) and value in content[key]:
            content[key] = content[key][value]
    return content
