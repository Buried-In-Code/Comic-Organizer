__all__ = ["Format", "InformationSource", "Role", "Genre", "AgeRating", "PageType"]

from enum import Enum

from dex_starr.console import CONSOLE


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
        CONSOLE.print(f"'{value}' isnt a valid metron_info.PageType", style="logging.level.warning")
        return PageType.STORY

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, PageType):
            raise NotImplementedError()
        return self.value < other.value


class Format(Enum):
    ANNUAL = "Annual"
    GRAPHIC_NOVEL = "Graphic Novel"
    LIMITED = "Limited"  # Used for mini/maxi series
    ONE_SHOT = "One-Shot"
    SERIES = "Series"  # Needs better name, but used for ongoing/cancelled series
    TRADE_PAPERBACK = "Trade Paperback"

    @staticmethod
    def load(value: str) -> "Format":
        for entry in Format:
            if entry.value.lower() == value.lower():
                return entry
        mappings = {"comic": Format.SERIES}
        if value.lower() in mappings:
            return mappings[value.lower()]
        CONSOLE.print(f"'{value}' isnt a valid metron_info.Format", style="logging.level.warning")
        return Format.SERIES

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, Format):
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
            if entry.value.lower() == value.lower():
                return entry
        mappings = {"comicvine": InformationSource.COMIC_VINE}
        if value.lower() in mappings:
            return mappings[value.lower()]
        raise ValueError(f"'{value}' isnt a valid metron_info.InformationSource")

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

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
            if entry.value.lower() == value.lower():
                return entry
        mappings = {
            "cover artist": Role.COVER,
            "colourist": Role.COLORIST,
            "colour separations": Role.COLOR_SEPARATIONS,
            "colour assists": Role.COLOR_ASSISTS,
            "colour flats": Role.COLOR_FLATS,
            "penciler": Role.PENCILLER,
        }
        if value.lower() in mappings:
            return mappings[value.lower()]
        CONSOLE.print(f"'{value}' isnt a valid metron_info.Role", style="logging.level.warning")
        return Role.OTHER

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

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
            if entry.value.lower() == value.lower():
                return entry
        CONSOLE.print(
            f"'{value}' isnt a valid metron_info.AgeRating", style="logging.level.warning"
        )
        return AgeRating.UNKNOWN

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, AgeRating):
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
        CONSOLE.print(f"'{value}' isnt a valid metron_info.Genre", style="logging.level.warning")
        return Genre.OTHER

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{type(self).__name__}{{{self.value}}}"

    def __lt__(self, other):
        if not isinstance(other, Genre):
            raise NotImplementedError()
        return self.value < other.value
