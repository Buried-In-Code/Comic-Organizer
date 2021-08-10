import logging
import time
from datetime import datetime
from json import JSONDecodeError
from typing import Dict, Any, List, Tuple, Optional

from requests import get
from requests.exceptions import HTTPError, ConnectionError

from .comic_info import ComicInfo, IdentifierInfo
from .console import Console
from .utils import METRON_USERNAME, METRON_PASSWORD, remove_extra

LOGGER = logging.getLogger(__name__)


def add_info(comic_info: ComicInfo, show_variants: bool = False) -> ComicInfo:
    # TODO: Work in Progress
    comic_info.series.publisher.identifiers = [x for x in comic_info.series.publisher.identifiers if x.website.lower() != 'metron']
    comic_info.series.identifiers = [x for x in comic_info.series.identifiers if x.website.lower() != 'metron']
    comic_info.identifiers = [x for x in comic_info.identifiers if x.website.lower() != 'metron']
    if 'metron' in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        publisher_id = [x.identifier for x in comic_info.series.publisher.identifiers if x.website.lower() == 'metron'][0]
    else:
        publisher_id = search_publishers(name=comic_info.series.publisher.title)
    if not publisher_id:
        return comic_info
    comic_info = parse_publisher_result(result=select_publisher(publisher_id=publisher_id), comic_info=comic_info)
    if 'metron' in [x.website.lower() for x in comic_info.series.identifiers]:
        series_id = [x.identifier for x in comic_info.series.identifiers if x.website.lower() == 'metron'][0]
    else:
        series_id = search_series(publisher_id=[x.identifier for x in comic_info.series.publisher.identifiers if x.website.lower() == 'metron'][0], name=comic_info.series.title,
                                  volume=comic_info.series.volume)
    if not series_id:
        return comic_info
    comic_info = parse_series_result(result=select_series(series_id=series_id), comic_info=comic_info)
    if 'metron' in [x.website.lower() for x in comic_info.identifiers]:
        issue_id = [x.identifier for x in comic_info.identifiers if x.website.lower() == 'metron'][0]
    else:
        issue_id = search_issues(series_id=[x.identifier for x in comic_info.series.identifiers if x.website.lower() == 'metron'][0], number=comic_info.number)
    if not issue_id:
        return comic_info
    return parse_issue_result(result=select_issue(issue_id=issue_id), comic_info=comic_info)


def parse_publisher_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Publisher Results')
    if 'metron' not in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        comic_info.series.publisher.identifiers.append(IdentifierInfo(website='Metron', identifier=result['id']))
    comic_info.series.publisher.title = comic_info.series.publisher.title if comic_info.series.publisher.title else result['name']
    return comic_info


def parse_series_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Series Results')
    if 'metron' not in [x.website.lower() for x in comic_info.series.identifiers]:
        comic_info.series.identifiers.append(IdentifierInfo(website='Metron', identifier=result['id']))
    comic_info.series.title = comic_info.series.title if comic_info.series.title else result['name']
    comic_info.series.volume = comic_info.series.volume if comic_info.series.volume else result['volume']
    comic_info.series.start_year = comic_info.series.start_year if comic_info.series.start_year else result['year_began']
    return comic_info


def parse_issue_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Comic Results')
    if 'metron' not in [x.website.lower() for x in comic_info.identifiers]:
        comic_info.identifiers.append(IdentifierInfo(website='Metron', identifier=result['id']))
    comic_info.number = comic_info.number if comic_info.number else result['number']
    comic_info.title = comic_info.title if comic_info.title else result['name'][0] if result['name'] else None
    comic_info.cover_date = comic_info.cover_date if comic_info.cover_date else datetime.strptime(result['cover_date'], '%Y-%m-%d').date()
    for credit in result['credits']:
        for role in credit['role']:
            if role['name'] not in comic_info.creators:
                comic_info.creators[role['name']] = []
            comic_info.creators[role['name']].append(credit['creator'])
    # TODO: Comic Format
    # TODO: Genres
    # TODO: Language ISO
    # TODO: Page Count
    comic_info.summary = comic_info.summary if comic_info.summary else remove_extra(result['desc'])
    # TODO: Variant
    return comic_info


def search_publishers(name: str) -> Optional[int]:
    LOGGER.debug('Search Publishers')
    results = []
    page = 1
    params = [('name', name)]
    result = __request('/publisher', params=params)
    if result:
        results.extend(result['results'])
    while result and result['next']:
        page += 1
        temp_params = [*params, ('page', page)]
        result = __request('/publisher', params=temp_params)
        if result:
            results.extend(result['results'])
    if len(results) >= 1:
        index = Console.display_menu(items=[f"{item['id']} - {item['name']}" for item in results], exit_text='None of the Above', prompt='Select Publisher')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    return None


def select_publisher(publisher_id: int) -> Dict[str, Any]:
    LOGGER.debug('Select Publisher')
    result = __request(f"/publisher/{publisher_id}")
    if result:
        return result
    return {}


def search_series(publisher_id: int, name: str, volume: Optional[int] = None) -> Optional[int]:
    LOGGER.debug('Search Series')
    results = []
    page = 1
    params = [('publisher_id', publisher_id), ('name', name)]
    if volume:
        params.append(('volume', volume))
    result = __request('/series', params=params)
    if result:
        results.extend(result['results'])
    while result and result['next']:
        page += 1
        temp_params = [*params, ('page', page)]
        result = __request('/series', params=temp_params)
        if result:
            results.extend(result['results'])
    if len(results) >= 1:
        index = Console.display_menu(items=[f"{item['id']} - {item['__str__']}" for item in results], exit_text='None of the Above', prompt='Select Series')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif volume:
        return search_series(publisher_id=publisher_id, name=name)
    return None


def select_series(series_id: int) -> Dict[str, Any]:
    LOGGER.debug('Select Series')
    result = __request(f"/series/{series_id}")
    if result:
        return result
    return {}


def search_issues(series_id: int, number: str) -> Optional[int]:
    LOGGER.debug('Search Issues')
    results = []
    page = 1
    params = [('series_id', series_id), ('number', number)]
    result = __request('/issue', params=params)
    if result:
        results.extend(result['results'])
    while result and result['next']:
        page += 1
        temp_params = [*params, ('page', page)]
        result = __request('/issue', params=temp_params)
        if result:
            results.extend(result['results'])
    if len(results) >= 1:
        index = Console.display_menu(items=[f"{item['id']} - {item['__str__']} [{item['cover_date']}]" for item in results], exit_text='None of the Above', prompt='Select Issue')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    return None


def select_issue(issue_id: int) -> Dict[str, Any]:
    LOGGER.debug('Select Issue')
    result = __request(f"/issue/{issue_id}")
    if result:
        return result
    return {}


def search_arcs(name: str) -> List[int]:
    LOGGER.debug('Search Arcs')
    pass


def select_arc(arc_id: int) -> Dict[str, Any]:
    LOGGER.debug('Select Arc')
    pass


def __request(endpoint: str, params: List[Tuple[str, str]] = None) -> Dict[str, Any]:
    if not params:
        params = []
    try:
        response = get(url=f"https://metron.cloud/api{endpoint}", auth=(METRON_USERNAME, METRON_PASSWORD), headers={}, params=params)
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
