import logging
from enum import auto, Enum
from typing import Optional

LOGGER = logging.getLogger(__name__)


class ComicFormat(Enum):
    COMIC = auto()
    ANNUAL = auto()
    DIGITAL_CHAPTER = auto()
    TRADE_PAPERBACK = auto()
    HARDCOVER = auto()

    def __str__(self):
        return self.get_title()

    def get_title(self) -> str:
        return ' '.join([x.title() for x in self.name.split('_')])

    @classmethod
    def from_string(cls, value: str) -> Optional['ComicFormat']:
        if value.lower() in ('comic', 'issue',):
            return cls.COMIC
        if value.lower() in ('annual',):
            return cls.ANNUAL
        if value.lower() in ('digital chapter', 'digital', 'chapter',):
            return cls.DIGITAL_CHAPTER
        if value.lower() in ('trade paperback', 'tradepaperback', 'trade',):
            return cls.TRADE_PAPERBACK
        if value.lower() in ('hardcover', 'hardback',):
            return cls.HARDCOVER
        LOGGER.warning(f"Unmapped Format: `{value}`")
        return None
