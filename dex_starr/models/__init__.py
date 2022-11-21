__all__ = ["PascalModel", "CamelModel", "clean_contents", "from_xml_list", "to_xml_list"]

from enum import Enum
from typing import Any, Dict, List

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

def to_xml_list(mappings: Dict[str, str], content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in content.copy().items():
        if isinstance(value, dict):
            content[key] = to_xml_list(mappings, value)
        elif isinstance(value, list):
            for index, entry in enumerate(value):
                if isinstance(entry, dict):
                    content[key][index] = to_xml_list(mappings, entry)
            if key in mappings:
                content[key] = {mappings[key]: content[key]}
    return content


def from_xml_list(mappings: Dict[str, str], content: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in mappings.items():
        if key in content and isinstance(content[key], dict) and value in content[key]:
            content[key] = content[key][value]
    return content

def text_fields(mappings: List[str], content: Dict[str, Any]) -> Dict[str, str]:
    for field in mappings:
        if field in content:
            if isinstance(content[field], str):
                content[field] = {"#text": content[field]}
            elif isinstance(content[field], list):
                for index, entry in enumerate(content[field]):
                    if isinstance(entry, str):
                        content[field][index] = {"#text": entry}
    return content