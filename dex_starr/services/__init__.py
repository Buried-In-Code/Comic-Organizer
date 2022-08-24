__all__ = ["tidy_creators"]
from typing import List

from ..metadata.metadata import Creator

valid_roles = [
    "Writer",
    "Story",
    "Artist",
    "Penciller",
    "Inker",
    "Colorist",
    "Letterer",
    "Designer",
    "Cover Artist",
    "Variant Cover Artist",
    "Editor",
    "Assistant Editor",
    "Associate Editor",
    "Consulting Editor",
    "Senior Editor",
    "Group Editor",
    "Executive Editor",
    "Editor-in-Chief",
    "Creator",
    "Translator",
    "Other",
]


def tidy_creators(creators: List[Creator]) -> List[Creator]:
    for creator in creators:
        creator.roles = [x for x in creator.roles if x in valid_roles]
    return sorted(x for x in creators if x.roles)
