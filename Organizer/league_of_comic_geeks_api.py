import logging
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Tuple, Union

from requests import get
from requests.exceptions import ConnectionError, HTTPError

from .comic_format import ComicFormat
from .console import Console
from .utils import get_enum_title, remove_annoying_chars, safe_dict_get, safe_list_get, CONFIG

LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://leagueofcomicgeeks.com/api'
TIMEOUT = 100


def _calculate_search_terms(comic_info: Dict[str, Any]) -> Tuple[str, str]:
    search_series = comic_info['Series']['Title']
    if comic_info['Comic']['Number'] and comic_info['Comic']['Number'] != '1':
        item_1 = f"{search_series} #{comic_info['Comic']['Number']}"
    else:
        item_1 = search_series
    if comic_info['Comic']['Number'] and comic_info['Comic']['Number'] != '1':
        if comic_info['Format'] == ComicFormat.TRADE_PAPERBACK:
            item_2 = f"{search_series} Vol. {comic_info['Comic']['Number']} TP"
        elif comic_info['Format'] == ComicFormat.HARDCOVER:
            item_2 = f"{search_series} Vol. {comic_info['Comic']['Number']} HC"
        elif comic_info['Format'] == ComicFormat.ANNUAL:
            item_2 = f"{search_series} Annual #{comic_info['Comic']['Number']}"
        elif comic_info['Format'] == ComicFormat.DIGITAL_CHAPTER:
            item_2 = f"{search_series} Chapter #{comic_info['Comic']['Number']}"
        else:
            item_2 = f"{search_series} #{comic_info['Comic']['Number']}"
    else:
        item_2 = search_series
    return item_1, item_2


def add_info(comic_info: Dict[str, Any], show_variants: bool = False) -> Dict[str, Any]:
    league_id = safe_dict_get(safe_dict_get(comic_info['Identifiers'], 'League of Comic Geeks'), 'Id')
    if league_id:
        response = select_comic(league_id)
    else:
        response = search_comic(_calculate_search_terms(comic_info), comic_info['Format'], show_variants)
    if not response:
        return comic_info
    if 'details' in response and 'publisher_name' in response['details'] and response['details']['publisher_name']:
        comic_info['Publisher'] = response['details']['publisher_name']
    if 'series' in response and 'title' in response['series'] and response['series']['title']:
        comic_info['Series']['Title'] = response['series']['title']
    if 'series' in response and 'volume' in response['series'] and response['series']['volume']:
        try:
            comic_info['Series']['Volume'] = int(response['series']['volume']) or 1
        except ValueError:
            pass
    if 'details' in response and 'title' in response['details'] and response['details']['title']:
        pass  # TODO Regex out the Comic Number from the response
    if 'details' in response and 'title' in response['details'] and response['details']['title']:
        comic_info['Comic']['Title'] = response['details']['title']
    if 'details' in response and 'date_release' in response['details'] and response['details']['date_release']:
        comic_info['Cover Date'] = response['details']['date_release']
    if 'details' in response and 'description' in response['details'] and response['details']['description']:
        comic_info['Summary'] = remove_annoying_chars(response['details']['description'])
    if 'details' in response and 'pages' in response['details'] and response['details']['pages']:
        try:
            comic_info['Page Count'] = int(response['details']['pages']) or 1
        except ValueError:
            pass
    if 'Genres' in response and response['Genres']:
        pass  # TODO Check if Genres is valid in response
    if 'Language' in response and response['Language']:
        pass  # TODO Check if Language is valid in response
    if 'details' in response and 'id' in response['details'] and response['details']['id']:
        try:
            comic_info['Identifiers']['League of Comic Geeks'] = {
                'Id': int(response['details']['id']),
                'Url': None
            }
        except ValueError:
            pass
    if 'details' in response and 'format' in response['details'] and response['details']['format']:
        comic_info['Format'] = ComicFormat.from_string(response['details']['format'])
    if 'creators' in response and response['creators']:
        for creator in response['creators']:
            for role in [x.strip() for x in creator['role'].split(',')]:
                if role in comic_info['Creators']:
                    comic_info['Creators'][role].append(creator['name'])
                else:
                    comic_info['Creators'][role] = [creator['name']]
    for role, names in comic_info['Creators'].items():
        comic_info['Creators'][role] = list(set(names))
    return comic_info


def search_comic(search_titles: Tuple[str, str], comic_format: ComicFormat, show_variants: bool = False) -> Dict[
    str, Any]:
    def __generate_name_options(options: List[Dict[str, Any]]) -> List[str]:
        str_options = []
        for item in options:
            series_title = item['series_name']
            if item['series_volume'] and item['series_volume'] != '0' and item['series_volume'] != '1':
                series_title += f" v{item['series_volume']}"
            try:
                series_begin = int(item['series_begin'])
                if not series_begin:
                    series_begin = 'Present'
            except ValueError:
                series_begin = 'Present'
            try:
                series_end = int(item['series_end'])
                if not series_end:
                    series_end = 'Present'
            except ValueError:
                series_end = 'Present'
            if series_begin != series_end:
                series_title += f" ({series_begin}-{series_end or 'Present'})"
            else:
                series_title += f" ({series_begin})"
            str_options.append(
                f"{item['id']}|{item['publisher_name']}|{series_title} - {item['title']} - {item['format']}")
        return str_options

    comic_id = None
    results_1 = __get_request('/search/format/json', params=[('query', search_titles[0])]) or []
    if search_titles[0] != search_titles[1]:
        results_2 = __get_request('/search/format/json', params=[('query', search_titles[1])]) or []
    else:
        results_2 = []
    results = results_1 + results_2
    if results:
        results = filter(lambda x: x['format'] == get_enum_title(comic_format), results)
        results = sorted(
            results if show_variants else filter(lambda x: x['variant'] == '0', results),
            key=lambda x: (x['publisher_name'], x['series_name'], x['series_volume'], x['title'])
        )
        str_results = __generate_name_options(results)
        selected = Console.display_menu(str_results, 'None of the Above')
        if selected:
            selected_result = safe_list_get(results, selected - 1)
            if selected_result:
                comic_id = int(selected_result['id'])
    if not comic_id:
        try:
            comic_id = int(Console.display_prompt('Input League of Comic Geeks ID'))
        except ValueError as err:
            return {}
    if comic_id:
        return select_comic(comic_id=comic_id)
    return {}


def select_comic(comic_id: int) -> Dict[str, Any]:
    result = __get_request('/comic/format/json', params=[('comic_id', str(comic_id))]) or {}
    if not result:
        return {}
    return result


def __get_request(url: str, params: List[Tuple[str, str]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    if not CONFIG['League of Comic Geeks']['API Key']:
        LOGGER.warning('Unable to access League of Comics without an `API Key`')
        return {}
    if not CONFIG['League of Comic Geeks']['Client ID']:
        LOGGER.warning('Unable to access League of Comics without a `Client ID`')
        return {}
    if not params:
        params = []
    try:
        response = get(url=BASE_URL + url, headers={
            'X-API-KEY': CONFIG['League of Comic Geeks']['API Key'],
            'X-API-CLIENT': CONFIG['League of Comic Geeks']['Client ID']
        }, timeout=TIMEOUT, params=params)
        response.raise_for_status()
        LOGGER.info(f"{response.status_code}: GET - {response.url}")
        try:
            return response.json()
        except (JSONDecodeError, KeyError):
            if response.text:
                LOGGER.critical(f'Unable to parse the response message: {response.text}')
            return {}
    except (HTTPError, ConnectionError) as err:
        LOGGER.error(err)
        return {}
