from dataclasses import dataclass, asdict
from typing import Any, List
import joblib
import pathlib
import msgpack
import gzip


@dataclass
class Player:
    __slots__ = ['account_id',
                 'team',
                 'assists',
                 'deaths',
                 'gold_per_min',
                 'hero_id',
                 'kills',
                 'level',
                 'xp_per_min']

    account_id: Any
    team: Any
    assists: Any
    deaths: Any
    gold_per_min: Any
    hero_id: Any
    kills: Any
    level: Any
    xp_per_min: Any


@dataclass
class PickBan:
    __slots__ = ['hero_id',
                 'is_pick',
                 'order',
                 'team']

    hero_id: Any
    is_pick: Any
    order: Any
    team: Any


@dataclass
class Game:
    __slots__ = ['cluster',
                 'dire_score',
                 'duration',
                 'first_blood_time',
                 'game_mode',
                 'human_players',
                 'lobby_type',
                 'match_id',
                 'match_seq_num',
                 'negative_votes',
                 'picks_bans',
                 'players',
                 'positive_votes',
                 'radiant_score',
                 'radiant_win',
                 'start_time']

    cluster: Any
    dire_score: Any
    duration: Any
    first_blood_time: Any
    game_mode: Any
    human_players: Any
    lobby_type: Any
    match_id: Any
    match_seq_num: Any
    negative_votes: Any
    picks_bans: Any
    players: Any
    positive_votes: Any
    radiant_score: Any
    radiant_win: Any
    start_time: Any

    def __post_init__(self):
        picks_bans = self.picks_bans
        players = self.players

        pb_list = []
        if picks_bans is not None:
            for pb in picks_bans:
                pb_clear = subset_of_dict(pb, PickBan.__slots__)
                pb_list.append(PickBan(**pb_clear))
        pb_list.sort(key=lambda x_pb: x_pb.order)
        self.picks_bans = pb_list

        pl_list = []
        for pl in players:
            if 'team' not in pl.keys():
                pl['team'] = 1 if pl['player_slot'] < 128 else 0
            pl_clear = subset_of_dict(pl, Player.__slots__)
            pl_list.append(Player(**pl_clear))
        self.players = pl_list


def subset_of_dict(dictionary: dict, keys: List[str]) -> dict:
    return {key: dictionary[key] for key in keys if key in dictionary}


def load_games(path: str) -> List[Game]:
    return joblib.load(path)


def dump_games(games: List[Game], path: str) -> None:
    joblib.dump(games, path)


def game_to_dict(game: Game) -> dict:
    return asdict(game)


def dict_to_game(dictionary: dict) -> Game:
    try:
        dictionary_clear = subset_of_dict(dictionary, Game.__slots__)
        new_game = Game(**dictionary_clear)
        return new_game
    except Exception as ex:
        print(dictionary)
        raise ex


def save_to_msgpack(games_list: List[Game], path: str) -> None:
    if not pathlib.Path(path).suffixes:
        path = path + '.msgpack.gz'

    def encode_game(obj):
        if isinstance(obj, Game):
            return {'__game': True, '__data': game_to_dict(obj)}
        return obj

    with gzip.open(path, 'wb') as gz_file:
        msgpack.dump(games_list, gz_file, default=encode_game)


def load_from_msgpack(path: str) -> List[Game]:
    if not pathlib.Path(path).suffixes:
        path = path + '.msgpack.gz'

    def decode_game(obj):
        if '__game' in obj:
            obj = dict_to_game(obj['__data'])
        return obj

    with gzip.open(path, 'rb') as gz_file:
        result = msgpack.load(gz_file, object_hook=decode_game)

    return result