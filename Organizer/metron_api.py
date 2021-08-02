import logging
from configparser import ConfigParser
from json import JSONDecodeError
from typing import Dict, Any, List, Tuple, Optional

from requests import get
from requests.exceptions import HTTPError, ConnectionError

from .console import Console

LOGGER = logging.getLogger(__name__)
CONFIG = ConfigParser()
CONFIG.read('config.ini')


def add_info(comic_info: Dict[str, Any], show_variants: bool = False) -> Dict[str, Any]:
    if 'Metron' in comic_info['Identifiers'] and 'Id' in comic_info['Identifiers']['Metron'] and comic_info['Identifiers']['Metron']['Id']:
        comic_info = select_issue(comic_info['Identifiers']['Metron']['Id'])
    else:
        if not comic_info['Publisher']:
            publisher_id = search_publisher(Console.display_prompt('Publisher'))
            if not publisher_id:
                return comic_info
            publisher_info = select_publisher(publisher_id)
        if not comic_info['Series']['Title']


def search_publisher(name: str) -> Optional[int]:
    results = []
    page = 1
    params = [('name', name)]
    result = __request('/publisher', params=params)
    while result and result['next']:
        results.extend(result['results'])
        page += 1
        temp_params = [*params, ('page', page)]
        result = __request('/publisher', params=temp_params)
    if len(results) > 1:
        index = Console.display_menu(items=[f"{item['id']} - {item['name']}" for item in results])
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif len(results) == 1:
        return results[0]['id']
    return None


def select_publisher(publisher_id: int) -> Dict[str, Any]:
    result = __request(f"/publisher/{publisher_id}")
    if result:
        return result
    return {}


def search_series(name: str, year_began: Optional[int] = None) -> Optional[int]:
    results = []
    page = 1
    params = [('name', name)]
    if year_began:
        params.append(('year_began', year_began))
    result = __request('/series', params=params)
    while result and result['next']:
        results.extend(result['results'])
        page += 1
        temp_params = [*params, ('page', page)]
        result = __request('/series', params=temp_params)
    if len(results) > 1:
        index = Console.display_menu(items=[f"{item['id']} - {item['__str__']}" for item in results])
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif len(results) == 1:
        return results[0]['id']
    return None


def select_series(series_id: int) -> Dict[str, Any]:
    result = __request(f"/series/{series_id}")
    if result:
        return result
    return {}


def search_issues(number: str, publisher_name: str, series_name: str, series_volume: int) -> Optional[int]:
    results = []
    page = 1
    params = [('number', number), ('publisher', publisher_name), ('series_name', series_name),
              ('series_volume', series_volume)]
    result = __request('/issue', params=params)
    while result and result['next']:
        results.extend(result['results'])
        page += 1
        temp_params = [*params, ('page', page)]
        result = __request('/issue', params=temp_params)
    if len(results) > 1:
        index = Console.display_menu(
            items=[f"{item['id']} - {item['__str__']} [{item['cover_date']}]" for item in results])
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif len(results) == 1:
        return results[0]['id']
    return None


def select_issue(issue_id: int) -> Dict[str, Any]:
    result = __request(f"/issue/{issue_id}")
    if result:
        return result
    return {}


def search_arcs(name: str) -> List[int]:
    pass


def select_arc(id: int) -> Dict[str, Any]:
    pass


def __request(endpoint: str, params: List[Tuple[str, str]] = None) -> Dict[str, Any]:
    if not CONFIG['Metron']['Username'] or not CONFIG['Metron']['Password']:
        LOGGER.warning('Unable to access Metron without a `Username` and `Password`')
        return {}
    if not params:
        params = []
    try:
        response = get(url=f"https://metron.cloud/api{endpoint}",
                       auth=(CONFIG['Metron']['Username'], CONFIG['Metron']['Password']), headers={}, params=params)
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
