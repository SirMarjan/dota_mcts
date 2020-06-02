from typing import Union, Optional, List

import requests

from dota2_rs.model.api_models import Game
from dota2_rs.utils import subset_of_dict, load_key

__MATCH_HISTORY_URL = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/'
__PUBLIC_MATCHES_URL = 'https://api.opendota.com/api/publicMatches'
__MATCH_DETAILS_URL = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/'
__STEAM_API_KEY = load_key('private/api_key.txt')


def get_match_history_steam_api(start_at_match_id: Optional[int] = None) -> List[int]:
    response = requests.get(__MATCH_HISTORY_URL,
                            params={'key': __STEAM_API_KEY, 'start_at_match_id': start_at_match_id},
                            timeout=2)
    matches_id = []
    if response.ok:
        matches_id = _steam_api_parse_matches_id(response.json())

    return matches_id


def get_match_history_odota_api(less_than_match_id: Optional[int] = None) -> List[int]:
    response = requests.get(__PUBLIC_MATCHES_URL,
                            params={'less_than_match_id': less_than_match_id},
                            timeout=2)
    matches_ids = []
    if response.ok:
        matches_ids = _odota_api_parse_matches_id(response.json())

    return matches_ids


def get_match_details(match_id) -> Union[int, Game]:
    response = requests.get(__MATCH_DETAILS_URL,
                            params={'key': __STEAM_API_KEY, 'match_id': match_id},
                            timeout=2)
    match = -1
    if response.ok:
        match = _parse_match_details(response.json())
        if match is None:
            match = 0

    return match


def _parse_match_details(json_body: dict) -> Optional[Game]:
    result = None
    if 'error' not in json_body['result'].keys():
        game_dict = json_body['result']
        if game_dict['game_mode'] == 22:
            clear_game_dict = subset_of_dict(game_dict, Game.__slots__)
            result = Game(**clear_game_dict)
    return result


def _steam_api_parse_matches_id(json_body: dict) -> List[int]:
    matches_id = []
    matches = json_body['result']['matches']
    for match in matches:
        match_id = match['match_id']
        matches_id.append(match_id)
    return matches_id


def _odota_api_parse_matches_id(json_body: dict) -> List[int]:
    matches_id = []
    matches = json_body
    for match in matches:
        match_id = match['match_id']
        matches_id.append(match_id)
    return matches_id
