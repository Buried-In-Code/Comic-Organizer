__all__ = ["add_info"]

from Organizer import ComicInfo, Console, Settings
from Organizer.external.comicvine_api import add_info as add_comicvine_info
from Organizer.external.league_of_comic_geeks_api import add_info as add_league_info
from Organizer.external.metron_api import add_info as add_metron_info


def add_info(settings: Settings, comic_info: ComicInfo, show_variants: bool = False) -> ComicInfo:
    if settings.league_api_key and settings.league_client_id:
        Console.display_item_value(item="Pulling info from", value="League of Comic Geeks")
        comic_info = add_league_info(settings=settings, comic_info=comic_info, show_variants=show_variants)
    if settings.metron_username and settings.metron_password:
        Console.display_item_value(item="Pulling info from", value="Metron")
        comic_info = add_metron_info(comic_info=comic_info)
    if settings.comicvine_api_key:
        Console.display_item_value(item="Pulling info from", value="Comicvine")
        comic_info = add_comicvine_info(comic_info=comic_info)
    return comic_info
