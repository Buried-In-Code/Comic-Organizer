__all__ = ["Role", "Format", "Genre", "PageType", "Source"]

import logging
from enum import Enum

from dex_starr.console import RichLogger

LOGGER = RichLogger(logging.getLogger(__name__))


class Source(Enum):
    COMICVINE = "Comicvine"
    GRAND_COMICS_DATABASE = "Grand Comics Database"
    LEAGUE_OF_COMIC_GEEKS = "League of Comic Geeks"
    MARVEL = "Marvel"
    METRON = "Metron"

    @staticmethod
    def load(value: str) -> "Source":
        for entry in Source:
            if entry.value.lower() == value.lower():
                return entry
        mappings = {"comic vine": Source.COMICVINE}
        if value.lower() in mappings:
            return mappings[value.lower()]
        raise ValueError(f"Unable to find Source: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, Source):
            raise NotImplementedError()
        return self.value < other.value


class PageType(Enum):
    FRONT_COVER = "Front Cover"
    INNER_COVER = "Inner Cover"
    ROUNDUP = "Roundup"
    STORY = "Story"
    ADVERTISEMENT = "Advertisement"
    EDITORIAL = "Editorial"
    LETTERS = "Letters"
    PREVIEW = "Preview"
    BACK_COVER = "Back Cover"
    OTHER = "Other"

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
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, PageType):
            raise NotImplementedError()
        return self.value < other.value


class Role(Enum):
    WRITER = "Writer"
    STORY = "Story"
    ARTIST = "Artist"
    PENCILLER = "Penciller"
    INKER = "Inker"
    COLOURIST = "Colourist"
    LETTERER = "Letterer"
    DESIGNER = "Designer"
    COVER_ARTIST = "Cover Artist"
    VARIANT_COVER_ARTIST = "Variant Cover Artist"
    EDITOR = "Editor"
    ASSISTANT_EDITOR = "Assistant Editor"
    ASSOCIATE_EDITOR = "Associate Editor"
    CONSULTING_EDITOR = "Consulting Editor"
    SENIOR_EDITOR = "Senior Editor"
    GROUP_EDITOR = "Group Editor"
    EXECUTIVE_EDITOR = "Executive Editor"
    EDITOR_IN_CHIEF = "Editor in Chief"
    CREATOR = "Creator"
    TRANSLATOR = "Translator"
    OTHER = "Other"

    @staticmethod
    def load(value: str) -> "Role":
        for entry in Role:
            if entry.value.lower() == value.lower():
                return entry
        mappings = {
            "colorist": Role.COLOURIST,
            "cover": Role.COVER_ARTIST,
            "penciler": Role.PENCILLER,
            "editor-in-chief": Role.EDITOR_IN_CHIEF,
        }
        if value.lower() in mappings:
            return mappings[value.lower()]
        LOGGER.warning(f"Unable to find Role: '{value}'")
        return Role.OTHER

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, Role):
            raise NotImplementedError()
        return self.value < other.value


class Format(Enum):
    COMIC = "Comic"
    DIGITAL_CHAPTER = "Digital Chapter"
    ANNUAL = "Annual"
    TRADE_PAPERBACK = "Trade Paperback"
    HARDCOVER = "Hardcover"
    GRAPHIC_NOVEL = "Graphic Novel"

    @staticmethod
    def load(value: str) -> "Format":
        for entry in Format:
            if entry.value.lower() == value.lower():
                return entry
        mappings = {"hard cover": Format.HARDCOVER}
        if value.lower() in mappings:
            return mappings[value.lower()]
        LOGGER.warning(f"Unable to find Format: '{value}'")
        return Format.COMIC

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, Format):
            raise NotImplementedError()
        return self.value < other.value


class Genre(Enum):
    ADULT = "Adult"
    CRIME = "Crime"
    ESPIONAGE = "Espionage"
    FANTASY = "Fantasy"
    HISTORICAL = "Historical"
    HORROR = "Horror"
    HUMOR = "Humor"
    MANGA = "Manga"
    PARODY = "Parody"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"
    SPORT = "Sport"
    SUPER_HERO = "Super-Hero"
    WAR = "War"
    WESTERN = "Western"
    OTHER = "Other"

    @staticmethod
    def load(value: str) -> "Genre":
        for entry in Genre:
            if entry.value.lower() == value.lower():
                return entry
        LOGGER.warning(f"Unable to find Genre: '{value}'")
        return Genre.OTHER

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, Genre):
            raise NotImplementedError()
        return self.value < other.value
