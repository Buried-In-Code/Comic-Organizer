import logging
import re

from titlecase import titlecase

from Common import ComicFormat

LOGGER = logging.getLogger(__name__)


def abbreviations(word, **kwargs):
    if word.upper() in ['DC', 'INC']:
        return word.upper()


def slugify(value):
    value = ' '.join(titlecase(re.sub(r"[\\/:*?\"<>|.]+", '', value).replace('-', ' '), callback=abbreviations).split())
    return value.replace(' ', '-')


def slug_publisher(publisher_name: str) -> str:
    return slugify(publisher_name)


def slug_series(series_title: str, series_vol: str) -> str:
    series_slug = slugify(series_title)
    if series_vol:
        try:
            vol = int(series_vol)
        except ValueError:
            vol = 0
        if vol and vol != 1:
            series_slug += f"-v{vol}"
    return series_slug


def slug_comic(series_slug: str, comic_format: ComicFormat, comic_num: str) -> str:
    if comic_format == ComicFormat.TRADE_PAPERBACK or comic_format == 'Trade Paperback':
        comic_slug = f"{series_slug}-Vol.{comic_num}-TP"
    elif comic_format == ComicFormat.HARDCOVER or comic_format == 'Hardcover':
        comic_slug = f"{series_slug}-Vol.{comic_num}-HC"
    elif comic_format == ComicFormat.ANNUAL or comic_format == 'Annual':
        comic_slug = f"{series_slug}-Annual-#{comic_num}"
    elif comic_format == ComicFormat.DIGITAL_CHAPTER or comic_format == 'Digital Chapter':
        comic_slug = f"{series_slug}-Chapter-#{comic_num}"
    else:
        comic_slug = f"{series_slug}-#{comic_num}"
    return comic_slug
