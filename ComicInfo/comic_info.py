import copy
import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from ruamel.yaml import YAML

from Common import ComicFormat, ComicGenre, remove_annoying_chars

LOGGER = logging.getLogger(__name__)
DEFAULT_INFO = {
    'Publisher': None,
    'Series': {
        'Title': None,
        'Volume': 1
    },
    'Comic': {
        'Number': None,
        'Title': None
    },
    'Variant': False,
    'Summary': None,
    'Cover Date': None,
    'Language': 'EN',
    'Format': ComicFormat.COMIC,
    'Genres': [],
    'Page Count': 1,
    'Creators': {},
    'Alternative Series': [],
    'Identifiers': {},
    'Notes': None
}


def load_comic_info(folder: Path, include_xml: bool = False) -> Dict[str, Any]:
    comic_info = None
    json_file = folder.joinpath('ComicInfo.json')
    yaml_file = folder.joinpath('ComicInfo.yaml')
    xml_file = folder.joinpath('ComicInfo.xml')
    if json_file.exists():
        comic_info = __load_json_comic_info(json_file)
    elif yaml_file.exists():
        comic_info = __load_yaml_comic_info(yaml_file)
    elif xml_file.exists():
        comic_info = __load_xml_comic_info(xml_file)
        if not include_xml:
            xml_file.unlink(missing_ok=True)
    return comic_info or copy.deepcopy(DEFAULT_INFO)


def __load_xml_comic_info(xml_file: Path) -> Dict[str, Any]:
    def str_to_list(soup, key: str) -> List[str]:
        return [x for x in (str(soup.find(key).string) if soup.find(key) else '').split(',') if x]

    comic_info = copy.deepcopy(DEFAULT_INFO)
    with open(xml_file, 'r', encoding='UTF-8') as xml_info:
        soup = BeautifulSoup(xml_info, 'xml')
        info = soup.find_all('ComicInfo')[0]
        LOGGER.debug(f"Loaded `{xml_file.name}`")

        comic_info['Publisher'] = str(info.find('Publisher').string) if info.find('Publisher') else None
        comic_info['Series']['Title'] = str(info.find('Series').string) if info.find('Series') else None
        comic_info['Series']['Volume'] = str(info.find('Volume').string) if info.find('Volume') else None
        comic_info['Comic']['Number'] = str(info.find('Number').string) if info.find('Number') else None
        # Comic Title
        # region Alternative Series
        # Alternative Series - Title
        # Alternative Series - Volume
        # Alternative Series - Number
        # endregion
        comic_info['Summary'] = remove_annoying_chars(str(info.find('Summary').string)) if info.find(
            'Summary') else None
        year = int(info.find('Year').string) if info.find('Year') else None
        month = int(info.find('Month').string) if info.find('Month') else 1 if year else None
        day = int(info.find('Day').string) if info.find('Day') else 1 if month else None
        comic_info['Cover Date'] = date(year, month, day).isoformat() if year else None
        # region Creators
        roles = ['Artist', 'Writer', 'Penciller', 'Inker', 'Colourist', 'Colorist', 'Letterer', 'CoverArtist', 'Editor']
        for role in roles:
            creators = str_to_list(info, role)
            if creators:
                comic_info['Creators'][role] = creators
        # endregion
        comic_info['Genres'] = [x for x in [ComicGenre.from_string(x) for x in str_to_list(info, 'Genre')] if x]
        comic_info['Language'] = str(info.find('LanguageISO').string).upper() if info.find('LanguageISO') else None
        # Format
        comic_info['Page Count'] = int(info.find('PageCount').string) if info.find('PageCount') else 0
        # Variant
        # region Identifiers
        if info.find('Web') and 'comixology' in str(info.find('Web').string).lower():
            comic_info['Identifiers']['Comixology'] = {
                'Url': str(info.find('Web').string),
                'Id': None
            }
        # endregion
        comic_info['Notes'] = remove_annoying_chars(str(info.find('Notes').string)) if info.find('Notes') else None

    return comic_info


def __load_json_comic_info(json_file: Path) -> Dict[str, Any]:
    with open(json_file, 'r', encoding='UTF-8') as json_info:
        comic_info = json.load(json_info)
        comic_info['Format'] = ComicFormat.from_string(comic_info['Format']) or ComicFormat.COMIC
        comic_info['Genres'] = [x for x in [ComicGenre.from_string(x) for x in comic_info['Genres'].copy()] if x]
        return __validate_dict(comic_info)


def __load_yaml_comic_info(yaml_file: Path) -> Dict[str, Any]:
    def yaml_setup() -> YAML:
        def null_representer(self, data):
            return self.represent_scalar(u'tag:yaml.org,2002:null', u'~')

        yaml = YAML(pure=True)
        yaml.default_flow_style = False
        yaml.width = 2147483647
        yaml.representer.add_representer(type(None), null_representer)
        # yaml.emitter.alt_null = '~'
        yaml.version = (1, 2)
        return yaml

    with open(yaml_file, 'r', encoding='UTF-8') as yaml_info:
        comic_info = yaml_setup().load(yaml_info)['Comic Info']
        comic_info['Series']['Volume'] = comic_info['Series']['Volume'] or 1
        comic_info['Series']['Title'] = comic_info['Series']['Name']
        del comic_info['Series']['Name']
        comic_info['Comic']['Number'] = comic_info['Comic']['Number'] or '1'
        comic_info['Format'] = ComicFormat.from_string(comic_info['Format']) or ComicFormat.COMIC
        comic_info['Genres'] = [x for x in [ComicGenre.from_string(x) for x in comic_info['Genres'].copy()] if x]
        comic_info['Cover Date'] = comic_info['Comic']['Release Date']
        del comic_info['Comic']['Release Date']
        comic_info['Language'] = comic_info['Language ISO'] or 'EN'
        del comic_info['Language ISO']
        for web, _id in comic_info['Identifiers'].copy().items():
            del comic_info['Identifiers'][web]
            if _id:
                comic_info['Identifiers'][web] = {
                    'Id': str(_id),
                    'Url': None
                }
        creators_dict = {}
        for creator in comic_info['Creators']:
            for role in creator['Role']:
                if role in creators_dict:
                    creators_dict[role].append(creator['Name'])
                else:
                    creators_dict[role] = [creator['Name']]
        del comic_info['Creators']
        comic_info['Creators'] = creators_dict
        return __validate_dict(comic_info)


def __validate_dict(mapping: Dict[str, Any]) -> Dict[str, Any]:
    temp_dict = copy.deepcopy(DEFAULT_INFO)
    for key, value in temp_dict.items():
        if key not in mapping:
            mapping[key] = value
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if sub_key not in mapping[key]:
                    mapping[key][sub_key] = sub_value
    temp_dict = copy.deepcopy(mapping)
    for key, value in temp_dict.items():
        if key not in DEFAULT_INFO:
            mapping.pop(key, None)
        elif isinstance(value, dict) and key not in ['Identifiers', 'Creators']:
            for sub_key, sub_value in value.items():
                if sub_key not in DEFAULT_INFO[key]:
                    mapping[key].pop(sub_key, None)
    return mapping


def save_comic_info(folder: Path, comic_info: Dict):
    json_file = folder.joinpath('ComicInfo.json')
    if not json_file.exists():
        json_file.touch()
    with open(json_file, 'w', encoding='UTF-8') as file_stream:
        json.dump(comic_info, file_stream, default=str, indent=2)
