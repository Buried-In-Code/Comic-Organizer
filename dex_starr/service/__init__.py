__all__ = ["pull_info"]

from typing import Any, Dict

from simyan.sqlite_cache import SQLiteCache

from dex_starr.metadata import Metadata
from dex_starr.service.league_of_comic_geeks import pull_info as pull_from_league_of_comic_geeks
from dex_starr.service.mokkari import pull_info as pull_from_metron
from dex_starr.service.simyan import pull_info as pull_from_comicvine
from dex_starr.settings import SETTINGS


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
            pulled_info,
            pull_from_comicvine(
                api_key=SETTINGS.comicvine_api_key,
                cache=cache,
                metadata=metadata,
            ),
        )
    if SETTINGS.metron_username and SETTINGS.metron_password:
        pulled_info = merge_dicts(
            pulled_info,
            pull_from_metron(
                username=SETTINGS.metron_username,
                password=SETTINGS.metron_password,
                cache=cache,
                metadata=metadata,
            ),
        )
    if SETTINGS.league_api_key and SETTINGS.league_client_id:
        pulled_info = merge_dicts(
            pulled_info,
            pull_from_league_of_comic_geeks(
                api_key=SETTINGS.league_api_key,
                client_id=SETTINGS.league_client_id,
                cache=cache,
                metadata=metadata,
            ),
        )
    metadata.set_metadata(pulled_info, resolve_manually)
