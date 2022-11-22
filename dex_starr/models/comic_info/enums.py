__all__ = ["YesNo", "Manga", "AgeRating", "PageType"]

import logging
from enum import Enum

from dex_starr.console import RichLogger

LOGGER = RichLogger(logging.getLogger(__name__))


class PageType(Enum):
    FRONT_COVER = "FrontCover"
    INNER_COVER = "InnerCover"
    ROUNDUP = "Roundup"
    STORY = "Story"
    ADVERTISEMENT = "Advertisement"
    EDITORIAL = "Editorial"
    LETTERS = "Letters"
    PREVIEW = "Preview"
    BACK_COVER = "BackCover"
    OTHER = "Other"
    DELETED = "Deleted"

    @staticmethod
    def load(value: str) -> "PageType":
        for entry in PageType:
            if entry.value.lower().replace(" ", "") == value.lower().replace(" ", ""):
                return entry
        LOGGER.warning(f"Unable to find PageType: '{value}'")
        return PageType.STORY

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, PageType):
            raise NotImplementedError()
        return self.value < other.value


class YesNo(Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"

    @staticmethod
    def load(value: str) -> "YesNo":
        for entry in YesNo:
            if entry.value.lower() == value.lower():
                return entry
        LOGGER.warning(f"Unable to find YesNo: '{value}'")
        return YesNo.UNKNOWN

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, YesNo):
            raise NotImplementedError()
        return self.value < other.value


class Manga(Enum):
    YES_AND_RIGHT_TO_LEFT = "YesAndRightToLeft"
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"

    @staticmethod
    def load(value: str) -> "Manga":
        for entry in Manga:
            if entry.value.lower() == value.lower():
                return entry
        LOGGER.warning(f"Unable to find Manga: '{value}'")
        return Manga.UNKNOWN

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, Manga):
            raise NotImplementedError()
        return self.value < other.value


class AgeRating(Enum):
    ADULTS_ONLY_18 = "Adults Only 18+"
    EARLY_CHILDHOOD = "Early Childhood"
    EVERYONE = "Everyone"
    EVERYONE_10 = "Everyone 10+"
    G = "G"
    KIDS_TO_ADULTS = "Kids to Adults"
    M = "M"
    MA15 = "MA15+"
    MATURE_17 = "Mature 17+"
    PG = "PG"
    R18 = "R18+"
    RATING_PENDING = "Rating Pending"
    TEEN = "Teen"
    X18 = "X18+"
    UNKNOWN = "Unknown"

    @staticmethod
    def load(value: str) -> "AgeRating":
        for entry in AgeRating:
            if entry.value.lower() == value.lower():
                return entry
        LOGGER.warning(f"Unable to find AgeRating: '{value}'")
        return AgeRating.UNKNOWN

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, AgeRating):
            raise NotImplementedError()
        return self.value < other.value
