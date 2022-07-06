import re


def sanitize(dirty: str) -> str:
    dirty = re.sub(r"[^0-9a-zA-Z ]+", "", dirty.replace("-", " "))
    dirty = " ".join(dirty.split())
    return dirty.replace(" ", "-")
