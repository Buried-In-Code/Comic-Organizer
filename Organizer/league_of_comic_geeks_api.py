import logging
import time
from datetime import datetime
from json import JSONDecodeError
from typing import Dict, Any, List, Tuple, Optional, Union

from requests import get
from requests.exceptions import HTTPError, ConnectionError

from .comic_format import ComicFormat
from .comic_info import ComicInfo, IdentifierInfo
from .console import Console
from .utils import LOCG_API_KEY, LOCG_CLIENT_ID, remove_extra

LOGGER = logging.getLogger(__name__)


def add_info(comic_info: ComicInfo, show_variants: bool = False) -> ComicInfo:
    if 'league of comic geeks' in [x.website.lower() for x in comic_info.identifiers]:
        comic_id = [x.identifier for x in comic_info.identifiers if x.website.lower() == 'league of comic geeks'][0]
    else:
        comic_id = search_comic(series_title=comic_info.series.title, comic_format=comic_info.comic_format, number=comic_info.number, show_variants=show_variants)
    return parse_comic_result(result=select_comic(comic_id=comic_id), comic_info=comic_info)


def parse_comic_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Comic Results')
    # region Publisher
    if 'league of comic geeks' not in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        comic_info.series.publisher.identifiers.append(IdentifierInfo(website='League of Comic Geeks', identifier=result['series']['publisher_id']))
    comic_info.series.publisher.title = comic_info.series.publisher.title or result['series']['publisher_name']
    # endregion
    # region Series
    if 'league of comic geeks' not in [x.website.lower() for x in comic_info.series.identifiers]:
        comic_info.series.identifiers.append(IdentifierInfo(website='League of Comic Geeks', identifier=result['series']['id']))
    comic_info.series.title = comic_info.series.title or result['series']['title']
    comic_info.series.volume = comic_info.series.volume or int(result['series']['volume'])
    comic_info.series.start_year = comic_info.series.start_year or int(result['series']['year_begin'])
    # endregion
    # region Comic
    if 'league of comic geeks' not in [x.website.lower() for x in comic_info.identifiers]:
        comic_info.identifiers.append(IdentifierInfo(website='League of Comic Geeks', identifier=result['details']['id']))
    # TODO: Number
    # TODO: Title
    comic_info.cover_date = comic_info.cover_date or datetime.strptime(result['details']['date_release'], '%Y-%m-%d').date()
    for creator in result['creators']:
        for role in creator['role'].split(','):
            if role.strip() not in comic_info.creators:
                comic_info.creators[role.strip()] = []
            comic_info.creators[role.strip()].append(creator['name'])
    comic_info.comic_format = comic_info.comic_format or ComicFormat.from_string(result['details']['format']).get_title()
    # TODO: Genres
    # TODO: Language ISO
    comic_info.page_count = comic_info.page_count or int(result['details']['pages'])
    comic_info.summary = comic_info.summary or remove_extra(result['details']['description'])
    # TODO: Variant
    # endregion
    return comic_info


def search_comic(series_title: str, comic_format: str, number: Optional[str] = None, show_variants: bool = False) -> Optional[int]:
    search_1, search_2 = __calculate_search_terms(series_title=series_title, comic_format=comic_format, number=number)
    results_1 = __request('/search/format/json', params=[('query', search_1)])
    if search_1 != search_2:
        results_2 = __request('/search/format/json', params=[('query', search_2)])
    else:
        results_2 = []
    results = results_1 + results_2
    if not results:
        return None
    results = filter(lambda x: x['format'] == comic_format, results)
    results = sorted(results if show_variants else filter(lambda x: x['variant'] == '0', results),
                     key=lambda x: (x['publisher_name'], x['series_name'], x['series_volume'], x['title']))
    if len(results) >= 1:
        index = Console.display_menu(
            items=[f"{item['id']} | [{item['publisher_name']}] {item['series_name']} v{item['series_volume']} - {item['title']} - {item['format']}" for item in results],
            exit_text='None of the Above', prompt='Select Comic')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    return None


def select_comic(comic_id: int) -> Dict[str, Any]:
    result = __request('/comic/format/json', params=[('comic_id', str(comic_id))])
    if result:
        return result
    return {}


def __request(endpoint: str, params: List[Tuple[str, str]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    if not params:
        params = []
    try:
        response = get(url=f"https://leagueofcomicgeeks.com/api{endpoint}", headers={
            'X-API-KEY': LOCG_API_KEY,
            'X-API-CLIENT': LOCG_CLIENT_ID
        }, params=params)
        if response.status_code == 200:
            try:
                LOGGER.info(f"{response.status_code}: GET - {response.url}")
                return response.json()
            except (JSONDecodeError, KeyError):
                LOGGER.error(f'Unable to parse the response message: {response.text}')
        return {}
    except (HTTPError, ConnectionError) as err:
        LOGGER.error(err)
        return {}
    finally:
        time.sleep(0.5)


def __calculate_search_terms(series_title: str, comic_format: str, number: Optional[str] = None) -> Tuple[str, str]:
    if number and number != '1':
        item_1 = f"{series_title} #{number}"
    else:
        item_1 = series_title
    if number and number != '1':
        if comic_format == ComicFormat.TRADE_PAPERBACK.get_title():
            item_2 = f"{series_title} Vol. {number} TP"
        elif comic_format == ComicFormat.HARDCOVER.get_title():
            item_2 = f"{series_title} Vol. {number} HC"
        elif comic_format == ComicFormat.ANNUAL.get_title():
            item_2 = f"{series_title} Annual #{number}"
        elif comic_format == ComicFormat.DIGITAL_CHAPTER.get_title():
            item_2 = f"{series_title} Chapter #{number}"
        else:
            item_2 = f"{series_title} #{number}"
    else:
        item_2 = series_title
    return item_1, item_2
