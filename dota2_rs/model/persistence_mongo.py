from typing import List

import pymongo

from dota2_rs.model.api_models import Game, game_to_dict
from dota2_rs.utils import load_key

__CONNECTION_STRING = None
__MONGO_KEY = load_key('private/mongo_key.txt')

_DB = pymongo.MongoClient(__CONNECTION_STRING.format(__MONGO_KEY))


def insert_matches_details(matches_details: List[Game]):
    if matches_details:
        documents = [game_to_dict(md) for md in matches_details]
        _DB.dota.matches_details.insert_many(documents, ordered=False)
