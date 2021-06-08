import logging
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple, Union

from requests import get

from .config import CONFIG
from .console import Console
from .utils import safe_dict_get, safe_list_get

LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://comicvine.gamespot.com/api'
TIMEOUT = 100


def add_comicvine_info(comic_info: Dict[str, Any], show_variants: bool = False) -> Dict[str, Any]:
    comicvine_id = safe_dict_get(safe_dict_get(comic_info['Identifiers'], 'Comicvine'), 'Id')
    if comicvine_id:
        response = select_comic(comicvine_id)
    else:
        series_id = search_series(comic_info['Series']['Title'], show_variants)
        if series_id:
            response = search_comic(series_id, comic_info['Comic']['Number'], show_variants)
        else:
            response = None
    if not response:
        return comic_info
    # TODO: Parse Comicvine response


def search_comic(series_id: int, comic_number: str, show_variants: bool = False) -> Dict[str, Any]:
    def __generate_name_options(options: List[Dict[str, Any]]) -> List[str]:
        str_options = []
        for item in options:
            series_title = item['name']
            if item['aliases']:
                series_title += f" [{item['aliases']}]"
            if item['start_year']:
                series_title += f" ({item['start_year']})"
            str_options.append(f"{item['id']}|{item['publisher']['name']}|{series_title}")
        return str_options

    response = __get_request(f"issues/", params=[('filter', f"issue_number:{comic_number},volume:{series_id}")])
    results = response['results']
    while response['offset'] + response['limit'] > response['number_of_total_results']:
        params = [('filter', f"issue_number:{comic_number},volume:{series_id}"),
                  ('offset', str(response['offset'] + response['limit']))]
        response = __get_request(f"issues/", params=params)
        results.extend(response['results'])

    comic_id = None
    if results:
        str_results = __generate_name_options(results)
        selected = Console.display_menu(str_results, 'None of the Above')
        if selected:
            selected_result = safe_list_get(results, selected - 1)
            if selected_result:
                comic_id = int(selected_result['id'])
            else:
                try:
                    comic_id = int(Console.display_prompt('Comic Id'))
                except ValueError:
                    pass
        else:
            try:
                comic_id = int(Console.display_prompt('Comic Id'))
            except ValueError:
                pass
    return comic_id


def search_series(series_title: str, show_variants: bool = False) -> Optional[int]:
    def __generate_name_options(options: List[Dict[str, Any]]) -> List[str]:
        str_options = []
        for item in options:
            series_title = item['name']
            if item['aliases']:
                series_title += f" [{item['aliases']}]"
            if item['start_year']:
                series_title += f" ({item['start_year']})"
            str_options.append(f"{item['id']}|{item['publisher']['name']}|{series_title}")
        return str_options

    response = __get_request(f"volumes/", params=[('filter', f"name:{series_title}"),
                                                  ('field_list', 'aliases,id,name,publisher,start_year')])
    results = response['results']
    while response['offset'] + response['limit'] > response['number_of_total_results']:
        params = [('filter', f"name:{series_title}"), ('field_list', 'aliases,id,name,publisher,start_year'),
                  ('offset', str(response['offset'] + response['limit']))]
        response = __get_request(f"volumes/", params=params)
        results.extend(response['results'])

    series_id = None
    if results:
        str_results = __generate_name_options(results)
        selected = Console.display_menu(str_results, 'None of the Above')
        if selected:
            selected_result = safe_list_get(results, selected - 1)
            if selected_result:
                series_id = int(selected_result['id'])
            else:
                try:
                    series_id = int(Console.display_prompt('Series Id'))
                except ValueError:
                    pass
        else:
            try:
                series_id = int(Console.display_prompt('Series Id'))
            except ValueError:
                pass
    return series_id


def select_comic(comic_id: int) -> Dict[str, Any]:
    return {}


def __get_request(url: str, params: List[Tuple[str, str]] = None) -> Optional[
    Union[Dict[str, Any], List[Dict[str, Any]]]]:
    if not CONFIG['Comicvine Key']:
        LOGGER.warning('Unable to access Comicvine check the `config.yaml`')
        return None
    if not params:
        params = []
    params.extend([('format', 'json'), ('api_key', CONFIG['Comicvine Key'])])
    response = get(url=BASE_URL + url, timeout=TIMEOUT, params=params)
    LOGGER.info(f"{response.status_code}: GET - {response.url}")
    if response.status_code == 200:
        try:
            return response.json()
        except (JSONDecodeError, KeyError):
            LOGGER.critical(f'Unable to parse the response message: `{response.text}`')
            return {}
    else:
        LOGGER.warning(f"Received unexpected error code: {response.status_code} => {response.text}")
        return None

# def _calculate_search_term(comic_info: Dict[str, Any]) -> str:
#     search_series = comic_info['Series']['Title']
#     if comic_info['Comic']['Number'] and comic_info['Comic']['Number'] != '1':
#         if comic_info['Format'] == ComicFormat.TRADE_PAPERBACK:
#             return f"{search_series} Vol. {comic_info['Comic']['Number']} TP"
#         if comic_info['Format'] == ComicFormat.HARDCOVER:
#             return f"{search_series} Vol. {comic_info['Comic']['Number']} HC"
#         if comic_info['Format'] == ComicFormat.ANNUAL:
#             return f"{search_series} Annual #{comic_info['Comic']['Number']}"
#         if comic_info['Format'] == ComicFormat.DIGITAL_CHAPTER:
#             return f"{search_series} Chapter #{comic_info['Comic']['Number']}"
#         return f"{search_series} #{comic_info['Comic']['Number']}"
#     return search_series
#
#
# def __generate_name_options(results: List[Dict[str, Any]]) -> List[str]:
#     options = []
#     for item in results:
#         series_title = item['series_name']
#         if item['series_volume'] and item['series_volume'] != '0' and item['series_volume'] != '1':
#             series_title += f" v{item['series_volume']}"
#         try:
#             series_begin = int(item['series_begin'])
#             if not series_begin:
#                 series_begin = 'Present'
#         except ValueError:
#             series_begin = 'Present'
#         try:
#             series_end = int(item['series_end'])
#             if not series_end:
#                 series_end = 'Present'
#         except ValueError:
#             series_end = 'Present'
#         if series_begin != series_end:
#             series_title += f" ({series_begin}-{series_end or 'Present'})"
#         else:
#             series_title += f" ({series_begin})"
#         options.append(f"{item['id']}|{item['publisher_name']}|{series_title} - {item['title']} - {item['format']}")
#     return options
#
#
# def search_comic(search_title: str, show_variants: bool = False) -> Dict[str, Any]:
#     comic_id = None
#     results = __get_request('/search/format/json', params=[('query', search_title)]) or []
#     if results:
#         results = sorted(
#             results if show_variants else filter(lambda x: x['variant'] == '0', results),
#             key=lambda x: (x['publisher_name'], x['series_name'], x['series_volume'], x['title'])
#         )
#         str_results = __generate_name_options(results)
#         selected = Console.display_menu(str_results, 'None of the Above')
#         if selected:
#             selected_result = safe_list_get(results, selected - 1)
#             if selected_result:
#                 comic_id = int(selected_result['id'])
#     if not comic_id:
#         try:
#             comic_id = int(Console.display_prompt('Input League of Comic Geeks ID'))
#         except ValueError as err:
#             return {}
#     if comic_id:
#         return select_comic(comic_id=comic_id)
#     return {}
#
#
# def select_comic(comic_id: int) -> Dict[str, Any]:
#     result = __get_request('/comic/format/json', params=[('comic_id', str(comic_id))]) or {}
#     if not result:
#         return {}
#     return result
#
#
# def __get_request(url: str, params: List[Tuple[str, str]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
#     if not CONFIG['League of Comic Geeks']['Client']:
#         LOGGER.warning('Unable to access League of Comics without the `League of Comics - Client Config`')
#         return {}
#     if not CONFIG['League of Comic Geeks']['Key']:
#         LOGGER.warning('Unable to access League of Comics without the `League of Comics - Key Config`')
#         return {}
#     if not params:
#         params = []
#     try:
#         response = get(url=BASE_URL + url, headers={
#             'X-API-KEY': CONFIG['League of Comic Geeks']['Key'],
#             'X-API-CLIENT': CONFIG['League of Comic Geeks']['Client']
#         }, timeout=TIMEOUT, params=params)
#         response.raise_for_status()
#         LOGGER.info(f"{response.status_code}: GET - {response.url}")
#         try:
#             return response.json()
#         except (JSONDecodeError, KeyError):
#             LOGGER.critical(f'Unable to parse the response message: {response.text}')
#             return {}
#     except (HTTPError, ConnectionError) as err:
#         LOGGER.error(err)
#         return {}
