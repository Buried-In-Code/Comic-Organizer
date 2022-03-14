__all__ = ["pull_info"]

from typing import Any, Dict

from simyan.sqlite_cache import SQLiteCache

from ..metadata import Metadata
from ..settings import SETTINGS
from .comicvine import pull_info as pull_comicvine_info
from .league_of_comic_geeks_api import pull_info as pull_league_info
from .metron import pull_info as pull_metron_info


def merge_dicts(input_1: Dict[str, Any], input_2: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in input_1.items():
        if isinstance(value, dict):
            if key in input_2:
                input_2[key] = merge_dicts(input_1[key], input_2[key])
    return {**input_1, **input_2}


def pull_info(metadata: Metadata, resolve_manually: bool = False):
    cache = SQLiteCache("Dex-Starr-cache.sqlite")
    pulled_info = {}
    if SETTINGS.comicvine_api_key:
        pulled_info = merge_dicts(
            pulled_info, pull_comicvine_info(SETTINGS.comicvine_api_key, cache, metadata)
        )
    if SETTINGS.metron_username and SETTINGS.metron_password:
        pulled_info = merge_dicts(
            pulled_info,
            pull_metron_info(SETTINGS.metron_username, SETTINGS.metron_password, cache, metadata),
        )
    if SETTINGS.league_api_key and SETTINGS.league_client_id:
        pulled_info = merge_dicts(
            pulled_info,
            pull_league_info(SETTINGS.league_api_key, SETTINGS.league_client_id, cache, metadata),
        )
    metadata.set_metadata(pulled_info, resolve_manually)
