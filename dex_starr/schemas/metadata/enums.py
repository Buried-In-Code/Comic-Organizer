__all__ = ["Role", "Format", "Genre"]

from enum import Enum

from dex_starr.console import CONSOLE


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
        CONSOLE.print(f"Unable to find Role: '{value}'", style="logging.level.warning")
        return Role.OTHER

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

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
        CONSOLE.print(f"Unable to find Format: '{value}'", style="logging.level.warning")
        return Format.COMIC

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

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
        CONSOLE.print(f"Unable to find Genre: '{value}'", style="logging.level.warning")
        return Genre.OTHER

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, Genre):
            raise NotImplementedError()
        return self.value < other.value
