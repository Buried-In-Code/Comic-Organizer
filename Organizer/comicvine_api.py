import logging
import time
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple

from requests import get
from requests.exceptions import HTTPError, ConnectionError

from .comic_info import ComicInfo, IdentifierInfo
from .console import Console
from .utils import COMICVINE_API_KEY, remove_extra

LOGGER = logging.getLogger(__name__)


def add_info(comic_info: ComicInfo, show_variants: bool = False) -> ComicInfo:
    comic_info.series.publisher.identifiers = [x for x in comic_info.series.publisher.identifiers if x.website.lower() != 'comicvine']
    comic_info.series.identifiers = [x for x in comic_info.series.identifiers if x.website.lower() != 'comicvine']
    comic_info.identifiers = [x for x in comic_info.identifiers if x.website.lower() != 'comicvine']
    if 'comicvine' in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        publisher_id = [x.identifier for x in comic_info.series.publisher.identifiers if x.website.lower() == 'comicvine'][0]
    else:
        publisher_id = search_publishers(name=comic_info.series.publisher.title)
    if not publisher_id:
        return comic_info
    comic_info = parse_publisher_result(result=select_publisher(publisher_id=publisher_id), comic_info=comic_info)
    if 'comicvine' in [x.website.lower() for x in comic_info.series.identifiers]:
        volume_id = [x.identifier for x in comic_info.series.identifiers if x.website.lower() == 'comicvine'][0]
    else:
        volume_id = search_volumes(publisher=[x.identifier for x in comic_info.series.publisher.identifiers if x.website.lower() == 'comicvine'][0], name=comic_info.series.title,
                                   start_year=comic_info.series.start_year)
    if not volume_id:
        return comic_info
    comic_info = parse_volume_result(result=select_volume(volume_id=volume_id), comic_info=comic_info)
    if 'comicvine' in [x.website.lower() for x in comic_info.identifiers]:
        issue_id = [x.identifier for x in comic_info.identifiers if x.website.lower() == 'comicvine'][0]
    else:
        issue_id = search_issues(volume=[x.identifier for x in comic_info.series.identifiers if x.website.lower() == 'comicvine'][0], issue_number=comic_info.number)
    if not issue_id:
        return comic_info
    return parse_issue_result(result=select_issue(issue_id=issue_id), comic_info=comic_info)


def parse_publisher_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Publisher Results')
    if 'comicvine' not in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        comic_info.series.publisher.identifiers.append(IdentifierInfo(website='Comicvine', identifier=result['id'], url=result['site_detail_url']))
    comic_info.series.publisher.title = comic_info.series.publisher.title if comic_info.series.publisher.title else result['name']
    return comic_info


def parse_volume_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Volume Results')
    if 'comicvine' not in [x.website.lower() for x in comic_info.series.identifiers]:
        comic_info.series.identifiers.append(IdentifierInfo(website='Comicvine', identifier=result['id'], url=result['site_detail_url']))
    comic_info.series.title = comic_info.series.title if comic_info.series.title else result['name']
    # TODO: Volume
    comic_info.series.start_year = comic_info.series.start_year if comic_info.series.start_year else result['start_year']
    return comic_info


def parse_issue_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    LOGGER.debug('Parse Issue Results')
    if 'comicvine' not in [x.website.lower() for x in comic_info.identifiers]:
        comic_info.identifiers.append(IdentifierInfo(website='Comicvine', identifier=result['id'], url=result['site_detail_url']))
    comic_info.number = comic_info.number if comic_info.number else result['issue_number']
    comic_info.title = comic_info.title if comic_info.title else result['name']
    comic_info.cover_date = comic_info.cover_date if comic_info.cover_date else datetime.strptime(result['cover_date'], '%Y-%m-%d').date()
    for credit in result['person_credits']:
        for role in credit['role'].split(','):
            if role.strip() not in comic_info.creators:
                comic_info.creators[role.strip()] = []
            comic_info.creators[role.strip()].append(credit['name'])
    # TODO: Comic Format
    # TODO: Genres
    # TODO: Language ISO
    # TODO: Page Count
    comic_info.summary = comic_info.summary if comic_info.summary else remove_extra(result['deck'])
    # TODO: Variant
    return comic_info


def search_publishers(name: str) -> Optional[int]:
    results = []
    offset = 0
    params = [('filter', f"name:{name}"), ('field_list', 'id,name,site_detail_url')]
    result = __request('/publishers', params=params)
    if result:
        results.extend(result['results'])
    while result and (result['offset'] + result['limit']) <= result['number_of_total_results']:
        offset += result['limit']
        temp_params = [*params, ('offset', offset)]
        result = __request('/publishers', params=temp_params)
        if result:
            results.extend(result['results'])
    if len(results) >= 1:
        results = sorted(results, key=lambda x: (x['name'] is None, x['name']))
        index = Console.display_menu(items=[f"{item['id']} | {item['name']} - {item['site_detail_url']}" for item in results], exit_text='None of the Above',
                                     prompt='Select Publisher')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    return None


def select_publisher(publisher_id: int) -> Dict[str, Any]:
    params = [('field_list', 'id,name,api_detail_url,deck,image,site_detail_url')]
    result = __request(f"/publisher/4010-{publisher_id}", params=params)
    if result and result['results']:
        return result['results']
    return {}


def search_volumes(publisher: int, name: str, start_year: Optional[int] = None) -> Optional[int]:
    results = []
    offset = 0
    params = [('filter', f"publisher:{publisher},name:{name}"), ('field_list', 'id,name,site_detail_url,publisher,start_year')]
    result = __request('/volumes', params=params)
    if result:
        if start_year:
            results.extend([x for x in result['results'] if x['start_year'] == start_year])
        else:
            results.extend(result['results'])
    while result and (result['offset'] + result['limit']) <= result['number_of_total_results']:
        offset += result['limit']
        temp_params = [*params, ('offset', offset)]
        result = __request('/volumes', params=temp_params)
        if result:
            if start_year:
                results.extend([x for x in result['results'] if x['start_year'] == start_year])
            else:
                results.extend(result['results'])
    if results:
        results = [x for x in results if x['publisher'] and x['publisher']['id'] == publisher]
    if len(results) >= 1:
        results = sorted(results, key=lambda x: (x['name'] is None, x['name'], x['start_year'] is None, x['start_year']))
        index = Console.display_menu(items=[f"{item['id']} | {item['name']} [{item['start_year']}] - {item['site_detail_url']}" for item in results], exit_text='None of the Above',
                                     prompt='Select Volume')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif start_year:
        return search_volumes(publisher=publisher, name=name)
    return None


def select_volume(volume_id: int) -> Dict[str, Any]:
    params = [('field_list', 'id,name,api_detail_url,start_year,deck,image,site_detail_url,publisher')]
    result = __request(f"/volume/4050-{volume_id}", params=params)
    if result and result['results']:
        return result['results']
    return {}


def search_issues(volume: int, issue_number: str) -> Optional[int]:
    results = []
    offset = 0
    params = [('filter', f"volume:{volume},issue_number:{issue_number}"), ('field_list', 'id,name,site_detail_url,volume,issue_number')]
    result = __request('/issues', params=params)
    if result:
        results.extend(result['results'])
    while result and (result['offset'] + result['limit']) <= result['number_of_total_results']:
        offset += result['limit']
        temp_params = [*params, ('offset', offset)]
        result = __request('/issues', params=temp_params)
        if result:
            results.extend(result['results'])
    if len(results) >= 1:
        results = sorted(results, key=lambda x: (x['issue_number'] is None, x['issue_number'], x['name'] is None, x['name']))
        index = Console.display_menu(items=[f"{item['id']} - #{item['issue_number']} {item['name']} - {item['site_detail_url']}" for item in results],
                                     exit_text='None of the Above', prompt='Select Issue')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    return None


def select_issue(issue_id: int) -> Dict[str, Any]:
    params = [('field_list', 'id,name,api_detail_url,issue_number,deck,image,site_detail_url,volume,cover_date,person_credits')]
    result = __request(f"/issue/4000-{issue_id}", params=params)
    if result and result['results']:
        return result['results']
    return {}


def __request(endpoint: str, params: List[Tuple[str, str]] = None) -> Dict[str, Any]:
    if not params:
        params = []
    temp = [*params, ('format', 'json'), ('api_key', COMICVINE_API_KEY)]
    try:
        response = get(url=f"https://comicvine.gamespot.com/api{endpoint}", headers={
            'User-Agent': 'Comic-Organizer',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }, params=temp)
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
