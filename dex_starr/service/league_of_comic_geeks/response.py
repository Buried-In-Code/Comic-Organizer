from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from dataclasses_json import Undefined, config, dataclass_json

from dex_starr.archive import FormatEnum


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ComicResult:
    id_: int = field(metadata=config(field_name="id"))
    parent_id: int
    publisher_id: int
    publisher_name: str
    series_id: int
    series_name: str
    series_volume: int
    series_end: int
    series_begin: int
    title: str
    parent_title: Optional[str]
    date_release: str
    description: Optional[str]
    format_: str = field(metadata=config(field_name="format"))
    variant: int
    price: float
    # cover: int
    # count_pulls: int
    date_modified: str
    # enabled: int
    # pulled: int
    # collected: int
    # wishlist: int
    # readlist: int
    # my_rating: Optional[str]
    # my_pick: Optional[str]

    def __post_init__(self):
        self.id_ = int(self.id_)
        self.parent_id = int(self.parent_id)
        self.publisher_id = int(self.publisher_id)
        self.series_id = int(self.series_id)
        self.series_volume = int(self.series_volume)
        self.series_end = int(self.series_end)
        self.series_begin = int(self.series_begin)
        self.variant = int(self.variant)
        self.price = float(self.price)

    @property
    def release_date(self) -> date:
        return date.fromisoformat(self.date_release)

    @property
    def comic_format(self) -> FormatEnum:
        return FormatEnum.get(self.format_)

    @property
    def modified_date(self) -> datetime:
        return datetime.fromisoformat(self.date_modified)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ComicDetails:
    id_: int = field(metadata=config(field_name="id"))
    parent_id: int
    publisher_id: int
    series_id: int
    title: str
    date_release: str
    # cover: int
    format_: str = field(metadata=config(field_name="format"))
    variant: int
    pages: int
    price: float
    # upc: int
    # isbn: str
    # sku: str
    # consensus_users: int
    # count_votes: int
    # count_pulls: int
    # count_collected: int
    date_added: str
    date_modified: str
    # enabled: int
    description: str
    parent_title: Optional[str]
    publisher_name: str
    publisher_slug: str

    def __post_init__(self):
        self.id_ = int(self.id_)
        self.parent_id = int(self.parent_id)
        self.publisher_id = int(self.publisher_id)
        self.series_id = int(self.series_id)
        self.variant = int(self.variant)
        self.pages = int(self.pages)
        self.price = float(self.price)

    @property
    def release_date(self) -> date:
        return date.fromisoformat(self.date_release)

    @property
    def comic_format(self) -> FormatEnum:
        return FormatEnum.get(self.format_)

    @property
    def added_date(self) -> datetime:
        return datetime.fromisoformat(self.date_added)

    @property
    def modified_date(self) -> datetime:
        return datetime.fromisoformat(self.date_modified)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ComicCreators:
    # assoc_id: int
    id_: int = field(metadata=config(field_name="id"))
    name: str
    slug: str
    # avatar: int
    role_id: int
    role: str

    def __post_init__(self):
        self.id_ = int(self.id_)
        self.role_id = int(self.role_id)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ComicCharacters:
    id_: int = field(metadata=config(field_name="id"))
    parent_id: int
    type_id: int
    name: str
    # avatar: int
    # banner: int
    universe_id: Optional[int]
    date_added: str
    date_modified: str
    # enabled: int
    # map_to_id: int
    parent_name: Optional[str]
    # avatar_id: int
    full_name: str
    universe_name: str
    publisher_name: str

    def __post_init__(self):
        self.id_ = int(self.id_)
        self.parent_id = int(self.parent_id)
        self.type_id = int(self.type_id)
        self.universe_id = int(self.universe_id) if self.universe_id else None

    @property
    def added_date(self) -> datetime:
        return datetime.fromisoformat(self.date_added)

    @property
    def modified_date(self) -> datetime:
        return datetime.fromisoformat(self.date_modified)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Series:
    id_: int = field(metadata=config(field_name="id"))
    publisher_id: int
    title: str
    description: str
    volume: int
    year_begin: int
    year_end: int
    # banner: int
    # cover: int
    date_added: str
    date_modified: str
    # enabled: int
    # map_to_id: int
    publisher_name: str
    publisher_slug: str
    comic_id: int
    series_string: int

    def __post_init__(self):
        self.id_ = int(self.id_)
        self.publisher_id = int(self.publisher_id)
        self.volume = int(self.volume)
        self.year_begin = int(self.year_begin)
        self.year_end = int(self.year_end)
        self.comic_id = int(self.comic_id)
        self.series_string = int(self.series_string)

    @property
    def added_date(self) -> datetime:
        return datetime.fromisoformat(self.date_added)

    @property
    def modified_date(self) -> datetime:
        return datetime.fromisoformat(self.date_modified)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Comic:
    details: ComicDetails
    creators: List[ComicCreators]
    characters: List[ComicCharacters]
    series: Series
    # banner: str
    # critic_reviews: List
    # user_reviews: List
    # community_reviews: List
    # keys: Dict
    # collected_in: List
    # variants: List
    # covers: List
    # preview_pages: List
    # comments: List
    # user_rating_count: int
    # user_review_count: int
    # user_review_score: int
    # user_review_avg: int
    # listed_members_count: int
    # count_read: int
