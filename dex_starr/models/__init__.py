__all__ = ["XmlModel", "JsonModel"]

from pydantic import BaseModel, Extra


def to_pascal_case(value: str) -> str:
    return value.replace("_", " ").title().replace(" ", "")


class XmlModel(BaseModel):
    class Config:
        alias_generator = to_pascal_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore


def to_camel_case(value: str) -> str:
    temp = value.replace("_", " ").title().replace(" ", "")
    return temp[0].lower() + temp[1:]


class JsonModel(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = Extra.ignore
