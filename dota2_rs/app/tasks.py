import logging
import time
from typing import List, Union, Optional

from huey import crontab
from huey.exceptions import TaskException, HueyException

from dota2_rs.app.config import huey_match_details, huey_match_history_scheduler, huey_match_details_scheduler, \
    huey_sqlite
from dota2_rs.model.api_models import Game
from dota2_rs.model.api_scrapp import get_match_history_odota_api, get_match_details, __STEAM_API_KEY
from dota2_rs.model.persistence_mongo import insert_matches_details
import dota2_rs.model.persistence_sqlite as sqlite


@huey_sqlite.on_startup()
def huey_sqlite_on_startup():
    sqlite.init()
    sqlite.restore_matches_form_progress()


@huey_sqlite.on_shutdown()
def huey_sqlite_on_shutdown():
    sqlite.close()


@huey_sqlite.task()
def get_smallest_match_id() -> Union[int, bool]:
    result = sqlite.get_smallest_match_id()
    if result is None:
        result = False
    return result


@huey_sqlite.task()
def insert_matches_ids(matches_ids: List[int]) -> bool:
    sqlite.insert_matches_ids(matches_ids)
    return True


@huey_sqlite.task()
def get_new_matches_ids() -> List[int]:
    return sqlite.get_new_matches_ids()


@huey_sqlite.task()
def set_matches_ids_statuses(matches_ids: List[int], states: List[int]) -> bool:
    sqlite.set_matches_ids_statuses(matches_ids, states)
    return True


@huey_sqlite.task()
def get_new_match_id_size() -> int:
    return sqlite.get_new_match_id_size()


@huey_match_history_scheduler.task(retries=2, retry_delay=1)
def pull_match_history(start_at_match_id: Optional[int]) -> List[int]:
    logging.info(f'load_match_history: {start_at_match_id}')
    return get_match_history_odota_api(start_at_match_id)


@huey_match_history_scheduler.periodic_task(crontab(minute='*/2'))
def start_match_history() -> None:
    logging.info(f'start_match_history')

    new_match_id_size = get_new_match_id_size()(blocking=True, timeout=5)
    if new_match_id_size < 500:
        for i in range(6):
            logging.info(f'start_match_history: {i + 1}/4')

            smallest_match_id = get_smallest_match_id()(blocking=True, timeout=5)

            matches_ids_result = pull_match_history(smallest_match_id)
            try:
                matches_ids = matches_ids_result.get(blocking=True, timeout=10)
            except HueyException:
                matches_ids = []
            logging.info(f'start_match_history: insert {len(matches_ids)}')
            insert_matches_ids(matches_ids)(blocking=True, timeout=5)
            time.sleep(1.1)


@huey_match_details.on_startup()
def huey_match_details_on_startup():
    print(__STEAM_API_KEY)


@huey_match_details.task(retries=2, retry_delay=1)
def pull_match_details(match_id: int) -> Union[int, Game]:
    logging.info(f'load_match_details: {match_id}')

    time_start = time.time()
    match_details = get_match_details(match_id)
    wait = 1.05 - (time.time() - time_start)
    if wait > 0.0:
        time.sleep(wait)
    return match_details


@huey_match_details_scheduler.periodic_task(crontab(minute='*/1'))
def start_matches_details() -> None:
    logging.info(f'start_matches_details')

    matches_ids = get_new_matches_ids()(blocking=True, timeout=5)

    matches_details_results = []
    for match_id in matches_ids:
        matches_details_results.append(pull_match_details(match_id))

    matches_details = []
    matches_statuses = []

    logging.info(f'start_matches_details: pull {len(matches_ids)}')
    print(f'start_matches_details: pull {len(matches_ids)}')
    time.sleep(55)
    print(f'start_matches_details: pull end sleep')
    unresolved = 0
    complete_not_rank = 0
    error = 0
    terror = 0
    for match_details_result in matches_details_results:
        try:
            match_details = match_details_result.get()
            if match_details is None:
                unresolved += 1
                match_details_result.revoke()
                match_status = sqlite.STATE['new']
            elif isinstance(match_details, Game):
                match_status = sqlite.STATE['complete_rank']
                matches_details.append(match_details)
            elif match_details == 0:
                match_status = sqlite.STATE['complete_not_rank']
                complete_not_rank += 1
            else:
                match_status = sqlite.STATE['error']
                error += 1
        except TaskException:
            terror += 1
            match_status = sqlite.STATE['error']

        matches_statuses.append(match_status)

    print(f'start_matches_details: in {len(matches_details)},'
          f' ur: {unresolved}, nr:{complete_not_rank}, er: {error}, te:{terror}')
    logging.info(f'start_matches_details: insert {len(matches_details)}')
    insert_matches_details(matches_details)
    set_matches_ids_statuses(matches_ids, matches_statuses)(blocking=True, timeout=5)
