import logging
from enum import Enum, auto
from typing import Optional

LOGGER = logging.getLogger(__name__)


class ComicGenre(Enum):
    SUPERHERO = auto()
    COMEDY = auto()
    CHILDRENS = auto()
    ROMANCE = auto()
    VIDEO_GAMES = auto()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{type(self).__name__}({self.name})"

    def get_title(self) -> str:
        return " ".join([x.title() for x in self.name.split("_")])

    @classmethod
    def from_string(cls, value: str) -> Optional["ComicGenre"]:
        if value.lower() in ("superhero", "super hero", "super-hero"):
            return cls.SUPERHERO
        if value.lower() in ("comedy",):
            return cls.COMEDY
        if value.lower() in ("children", "children's", "childrens"):
            return cls.CHILDRENS
        if value.lower() in ("romance",):
            return cls.ROMANCE
        if value.lower() in ("video games", "video", "games", "game", "video game"):
            return cls.VIDEO_GAMES
        LOGGER.warning(f"Unmapped Genre: `{value}`")
        return None
