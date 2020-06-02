from typing import List, Optional

from peewee import Model, SqliteDatabase, IntegerField, fn

_DB = SqliteDatabase('private/matches_ids.db')

STATE = {
    'new': 0,
    'process': 1,
    'complete_rank': 2,
    'complete_not_rank': 3,
    'error': 4

}


class MatchId(Model):
    match_id = IntegerField(unique=True)
    state_id = IntegerField(default=0)

    class Meta:
        database = _DB


def init():
    if not _DB.is_closed():
        _DB.close()
    _DB.connect()
    _DB.create_tables([MatchId])


def close():
    _DB.close()


def get_smallest_match_id() -> Optional[int]:
    subq = (MatchId
            .select(fn.MIN(MatchId.match_id)))
    try:
        match_id = (MatchId
                    .select()
                    .where(MatchId.match_id == subq)).get().match_id
    except MatchId.DoesNotExist:
        match_id = None

    return match_id


def get_new_match_id_size() -> int:
    query = (MatchId
             .select()
             .where(MatchId.state_id == STATE['new'])
             .count())

    return int(query)


def insert_matches_ids(matches_ids: List[int]) -> None:
    matches_ids = [(match_id,) for match_id in matches_ids]
    with _DB.atomic():
        MatchId.insert_many(matches_ids, fields=['match_id']).execute()


@_DB.atomic()
def get_new_matches_ids(change_state: bool = True) -> List[int]:
    matches_ids_query = (MatchId
                         .select()
                         .where(MatchId.state_id == STATE['new'])
                         .limit(240))
    matches_ids = []
    match_id_models = []
    for match_id_model in matches_ids_query:
        if change_state:
            match_id_model.state_id = STATE['process']
            match_id_models.append(match_id_model)
        matches_ids.append(match_id_model.match_id)
    if match_id_models:
        MatchId.bulk_update(match_id_models, [MatchId.state_id], batch_size=30)

    return matches_ids


@_DB.atomic()
def set_matches_ids_statuses(matches_ids: List[int], states: List[int]) -> None:
    match_id_models = []
    for match_id, state in zip(matches_ids, states):
        match_id_model = MatchId.get(MatchId.match_id == match_id)
        match_id_model.state_id = state
        match_id_models.append(match_id_model)
    if match_id_models:
        MatchId.bulk_update(match_id_models, [MatchId.state_id], batch_size=30)


@_DB.atomic()
def restore_matches_form_progress():
    matches_ids_query = (MatchId
                         .select()
                         .where(MatchId.state_id == STATE['process']))
    matches_ids = []
    match_id_models = []
    for match_id_model in matches_ids_query:
        match_id_model.state_id = STATE['new']
        match_id_models.append(match_id_model)
        matches_ids.append(match_id_model.match_id)
    if match_id_models:
        MatchId.bulk_update(match_id_models, [MatchId.state_id], batch_size=30)
