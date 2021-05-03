import logging
from enum import auto, Enum
from typing import Optional

LOGGER = logging.getLogger(__name__)


class ComicGenre(Enum):
    SUPERHERO = auto()

    def __str__(self):
        return self.get_title()

    def get_title(self) -> str:
        return ' '.join([x.title() for x in self.name.split('_')])

    @classmethod
    def from_string(cls, value: str) -> Optional['ComicGenre']:
        if value.lower() in ('superhero', 'super hero', 'super-hero',):
            return cls.SUPERHERO
        LOGGER.warning(f"Unmapped Genre: `{value}`")
        return None
