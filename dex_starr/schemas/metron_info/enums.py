__all__ = ["FormatType", "InformationSource", "Role", "Genre", "AgeRating", "ComicPageType"]

from enum import Enum

from dex_starr.schemas.comic_info.enums import ComicPageType
from dex_starr.schemas.metadata.enums import Genre


class FormatType(Enum):
    ANNUAL = "Annual"
    GRAPHIC_NOVEL = "Graphic Novel"
    LIMITED = "Limited"  # Used for mini/maxi series
    ONE_SHOT = "One-Shot"
    SERIES = "Series"  # Needs better name, but used for ongoing/cancelled series
    TRADE_PAPERBACK = "Trade Paperback"

    @staticmethod
    def load(value: str) -> "FormatType":
        for entry in FormatType:
            if entry.value == value:
                return entry
        if value == "Comic":
            return FormatType.SERIES
        raise ValueError(f"Unable to find FormatType: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, FormatType):
            raise NotImplementedError()
        return self.value < other.value


class InformationSource(Enum):
    COMIC_VINE = "Comic Vine"
    GRAND_COMICS_DATABASE = "Grand Comics Database"
    METRON = "Metron"
    LEAGUE_OF_COMIC_GEEKS = "League of Comic Geeks"
    MARVEL = "Marvel"

    @staticmethod
    def load(value: str) -> "InformationSource":
        for entry in InformationSource:
            if entry.value == value:
                return entry
        if value == "Comicvine":
            return InformationSource.COMIC_VINE
        raise ValueError(f"Unable to find InformationSource: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, InformationSource):
            raise NotImplementedError()
        return self.value < other.value


class Role(Enum):
    WRITER = "Writer"
    SCRIPT = "Script"
    STORY = "Story"
    PLOT = "Plot"
    INTERVIEWER = "Interviewer"
    ARTIST = "Artist"
    PENCILLER = "Penciller"
    BREAKDOWNS = "Breakdowns"
    ILLUSTRATOR = "Illustrator"
    LAYOUTS = "Layouts"
    INKER = "Inker"
    EMBELLISHER = "Embellisher"
    FINISHES = "Finishes"
    INK_ASSISTS = "Ink Assists"
    COLORIST = "Colorist"
    COLOR_SEPARATIONS = "Color Separations"
    COLOR_ASSISTS = "Color Assists"
    COLOR_FLATS = "Color Flats"
    DIGITAL_ART_TECHNICIAN = "Digital Art Technician"
    GRAY_TONE = "Gray Tone"
    LETTERER = "Letterer"
    COVER = "Cover"
    EDITOR = "Editor"
    CONSULTING_EDITOR = "Consulting Editor"
    ASSISTANT_EDITOR = "Assistant Editor"
    ASSOCIATE_EDITOR = "Associate Editor"
    GROUP_EDITOR = "Group Editor"
    SENIOR_EDITOR = "Senior Editor"
    MANAGING_EDITOR = "Managing Editor"
    COLLECTION_EDITOR = "Collection Editor"
    PRODUCTION = "Production"
    DESIGNER = "Designer"
    LOGO_DESIGN = "Logo Design"
    TRANSLATOR = "Translator"
    SUPERVISING_EDITOR = "Supervising Editor"
    EXECUTIVE_EDITOR = "Executive Editor"
    EDITOR_IN_CHIEF = "Editor In Chief"
    PRESIDENT = "President"
    PUBLISHER = "Publisher"
    CHIEF_CREATIVE_OFFICER = "Chief Creative Officer"
    EXECUTIVE_PRODUCER = "Executive Producer"
    OTHER = "Other"

    @staticmethod
    def load(value: str) -> "Role":
        for entry in Role:
            if entry.value == value:
                return entry
        if value == "Cover Artist":
            return Role.COVER
        if value == "Colourist":
            return Role.COLORIST
        if value == "Colour Separations":
            return Role.COLOR_SEPARATIONS
        if value == "Colour Assists":
            return Role.COLOR_ASSISTS
        if value == "Colour Flats":
            return Role.COLOR_FLATS
        raise ValueError(f"Unable to find Role: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, Role):
            raise NotImplementedError()
        return self.value < other.value


class AgeRating(Enum):
    EVERYONE = "Everyone"  # All Ages
    TEEN = "Teen"  # 12+
    TEEN_PLUS = "Teen Plus"  # 15+
    MATURE = "Mature"  # 17+
    UNKNOWN = "Unknown"

    @staticmethod
    def load(value: str) -> "AgeRating":
        for entry in AgeRating:
            if entry.value == value:
                return entry
        raise ValueError(f"Unable to find AgeRating: '{value}'")

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, AgeRating):
            raise NotImplementedError()
        return self.value < other.value
