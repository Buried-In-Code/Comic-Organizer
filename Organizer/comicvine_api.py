import logging
import time
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple

from requests import get
from requests.exceptions import HTTPError, ConnectionError

from .comic_info import ComicInfo
from .console import Console
from .utils import COMICVINE_API_KEY

LOGGER = logging.getLogger(__name__)


def add_info(comic_info: ComicInfo, show_variants: bool = False) -> ComicInfo:
    # TODO: Work in Progress
    if 'comicvine' in [x.website.lower() for x in comic_info.identifiers]:
        return parse_issue_result(
            result=select_issue(issue_id=[x.id for x in comic_info.identifiers if x.website.lower() == 'comicvine'][0]),
            comic_info=comic_info)
    elif 'comicvine' in [x.website.lower() for x in comic_info.series.identifiers]:
        comic_id = search_issues(
            volume=[x.id for x in comic_info.series.identifiers if x.website.lower() == 'comicvine'][0],
            issue_number=comic_info.number)
        if not comic_id:
            return comic_info
        return parse_issue_result(result=select_issue(issue_id=comic_id), comic_info=comic_info)
    elif 'comicvine' in [x.website.lower() for x in comic_info.series.publisher.identifiers]:
        series_id = search_volumes(
            publisher=[x.id for x in comic_info.series.publisher.identifiers if x.website.lower() == 'comicvine'][0],
            name=comic_info.series.title, start_year=comic_info.series.start_year)
        if not series_id:
            return comic_info
        comic_id = search_issues(volume=series_id, issue_number=comic_info.number)
        if not comic_id:
            return comic_info
        return parse_issue_result(result=select_issue(issue_id=comic_id), comic_info=comic_info)
    else:
        publisher_id = search_publishers(name=comic_info.series.publisher.title)
        if not publisher_id:
            return comic_info
        series_id = search_volumes(publisher=publisher_id, name=comic_info.series.title,
                                   start_year=comic_info.series.start_year)
        if not series_id:
            return comic_info
        comic_id = search_issues(volume=series_id, issue_number=comic_info.number)
        if not comic_id:
            return comic_info
        return parse_issue_result(result=select_issue(issue_id=comic_id), comic_info=comic_info)


def parse_issue_result(result: Dict[str, Any], comic_info: ComicInfo) -> ComicInfo:
    return comic_info


def search_publishers(name: str) -> Optional[int]:
    results = []
    offset = 0
    params = [('filter', f"name:{name}"), ('field_list', 'id,name,api_detail_url')]
    result = __request('/publishers', params=params)
    if result:
        results.extend(result['results'])
    while result and result['offset'] + result['limit'] > result['number_of_total_results']:
        offset += result['limit']
        temp_params = [*params, ('offset', offset)]
        result = __request('/publishers', params=temp_params)
        if result:
            results.extend(result['results'])
    if len(results) > 1:
        index = Console.display_menu(
            items=[f"{item['id']} | {item['name']} - {item['api_detail_url']}" for item in results],
            exit_text='None of the Above', prompt='Select Publisher')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif len(results) == 1:
        return results[0]['id']
    return None


def select_publisher(publisher_id: int) -> Dict[str, Any]:
    params = [('field_list', 'id,name,api_detail_url,deck,image,site_detail_url')]
    result = __request(f"/publisher/{publisher_id}", params=params)
    if result and result['results']:
        return result['results']
    return {}


def search_volumes(publisher: int, name: str, start_year: Optional[int] = None) -> Optional[int]:
    results = []
    offset = 0
    params = [('filter', f"publisher:{publisher},name:{name}"), ('field_list', 'id,name,api_detail_url,start_year')]
    result = __request('/volumes', params=params)
    if result:
        if start_year:
            results.extend([x for x in result['results'] if x['start_year'] == start_year])
        else:
            results.extend(result['results'])
    while result and result['offset'] + result['limit'] > result['number_of_total_results']:
        offset += result['limit']
        temp_params = [*params, ('offset', offset)]
        result = __request('/volumes', params=temp_params)
        if result:
            if start_year:
                results.extend([x for x in result['results'] if x['start_year'] == start_year])
            else:
                results.extend(result['results'])
    if len(results) > 1:
        index = Console.display_menu(
            items=[f"{item['id']} | {item['name']} [{item['start_year']}] - {item['api_detail_url']}"
                   for item in results],
            exit_text='None of the Above', prompt='Select Volume')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif len(results) == 1:
        return results[0]['id']
    return None


def select_volume(volume_id: int) -> Dict[str, Any]:
    params = [('field_list', 'id,name,api_detail_url,deck,image,site_detail_url,start_year,publisher')]
    result = __request(f"/volume/{volume_id}", params=params)
    if result and result['results']:
        return result['results']
    return {}


def search_issues(volume: int, issue_number: str) -> Optional[int]:
    results = []
    offset = 0
    # TODO
    params = [('filter', f"volume:{volume},issue_number:{issue_number}"),
              ('field_list', 'id,name,api_detail_url,issue_number')]
    result = __request('/issues', params=params)
    if result:
        results.extend(result['results'])
    while result and result['offset'] + result['limit'] > result['number_of_total_results']:
        offset += result['limit']
        temp_params = [*params, ('offset', offset)]
        result = __request('/issues', params=temp_params)
        if result:
            results.extend(result['results'])
    if len(results) > 1:
        index = Console.display_menu(
            items=[f"{item['id']} - #{item['issue_number']} {item['name']} - {item['api_detail_url']}"
                   for item in results],
            exit_text='None of the Above', prompt='Select Issue')
        if 1 <= index <= len(results):
            return results[index - 1]['id']
    elif len(results) == 1:
        return results[0]['id']
    return None


def select_issue(issue_id: int) -> Dict[str, Any]:
    # TODO
    params = [('field_list', 'id,name,api_detail_url,deck,image,site_detail_url,volume')]
    result = __request(f"/issue/{issue_id}", params=params)
    if result and result['results']:
        return result['results']
    return {}


def __request(endpoint: str, params: List[Tuple[str, str]] = None) -> Dict[str, Any]:
    if not params:
        params = []
    params.extend([('format', 'json'), ('api_key', COMICVINE_API_KEY)])
    try:
        response = get(url=f"https://comicvine.gamespot.com/api{endpoint}", headers={}, params=params)
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
