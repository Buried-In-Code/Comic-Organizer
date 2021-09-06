import html
import logging
import re
from typing import Optional

from titlecase import titlecase

from Organizer.comic_format import ComicFormat

LOGGER = logging.getLogger(__name__)


def remove_extra(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    tag_re = re.compile(r"(<!--.*?-->|<[^>]*>)")
    return " ".join(html.unescape(tag_re.sub("", value.strip())).split())


def to_titlecase(text: str) -> str:
    return titlecase(
        text=re.sub(r"[^a-zA-Z0-9\s\-&]+", "", text.strip().lower()).replace("-", " "), callback=abbreviations
    )


def abbreviations(word, **kwargs):
    if word.upper() in ["DC", "INC"]:
        return word.upper()


def slugify(text: str) -> str:
    return " ".join(to_titlecase(text=text).split()).replace(" ", "-")


def slugify_publisher(title: str) -> str:
    return slugify(title)


def slugify_series(title: str, volume: int) -> str:
    series_slug = slugify(title)
    if volume and volume != 1:
        series_slug += f"-v{volume}"
    return series_slug


def slugify_comic(series_slug: str, comic_format: str, number: str) -> str:
    if comic_format == ComicFormat.TRADE_PAPERBACK.get_title():
        comic_slug = f"{series_slug}-Vol.{number}-TP"
    elif comic_format == ComicFormat.HARDCOVER.get_title():
        comic_slug = f"{series_slug}-Vol.{number}-HC"
    elif comic_format == ComicFormat.ANNUAL.get_title():
        comic_slug = f"{series_slug}-Annual-#{number}"
    elif comic_format == ComicFormat.DIGITAL_CHAPTER.get_title():
        comic_slug = f"{series_slug}-Chapter-#{number}"
    else:
        comic_slug = f"{series_slug}-#{number}"
    LOGGER.info(f"{series_slug}-{comic_format}-{number} => {comic_slug}")
    return comic_slug
