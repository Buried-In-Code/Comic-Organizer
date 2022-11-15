__all__ = ["Role", "FormatType", "Genre"]

from enum import Enum


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
            if entry.value == value:
                return entry
        if value == "Colorist":
            return Role.COLOURIST
        if value == "Cover":
            return Role.COVER_ARTIST
        raise ValueError(f"Unable to find Role: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, Role):
            raise NotImplementedError()
        return self.value < other.value


class FormatType(Enum):
    COMIC = "Comic"
    DIGITAL_CHAPTER = "Digital Chapter"
    ANNUAL = "Annual"
    TRADE_PAPERBACK = "Trade Paperback"
    HARDCOVER = "Hardcover"
    GRAPHIC_NOVEL = "Graphic Novel"

    @staticmethod
    def load(value: str) -> "FormatType":
        for entry in FormatType:
            if entry.value == value:
                return entry
        raise ValueError(f"Unable to find FormatType: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, FormatType):
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

    @staticmethod
    def load(value: str) -> "Genre":
        for entry in Genre:
            if entry.value == value:
                return entry
        raise ValueError(f"Unable to find Genre: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, Genre):
            raise NotImplementedError()
        return self.value < other.value
