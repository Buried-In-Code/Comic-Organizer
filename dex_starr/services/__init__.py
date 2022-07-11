__all__ = []

from typing import Any, Dict


def merge_dicts(input_1: Dict[str, Any], input_2: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in input_1.items():
        if isinstance(value, dict):
            if key in input_2:
                input_2[key] = merge_dicts(input_1[key], input_2[key])
    return {**input_1, **input_2}
