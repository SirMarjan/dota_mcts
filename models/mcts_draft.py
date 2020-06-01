from typing import Set, Optional, FrozenSet, List

import logging
from copy import deepcopy

from models.constants import HEROES
from models.win_rate_models import WinRateModel


class AllPickDraft:

    def __init__(self,
                 model_win_rate: WinRateModel,
                 is_radiant_player: bool = True,
                 bans: Optional[Set[int]] = None,
                 radiant_pick: Optional[Set[int]] = None,
                 dire_pick: Optional[Set[int]] = None):
        self.model_win_rate = model_win_rate
        self.is_radiant_player = is_radiant_player

        self.bans = frozenset(bans) if bans is not None else frozenset()
        self.radiant_pick = radiant_pick.copy() if radiant_pick is not None else set()
        self.dire_pick = dire_pick.copy() if dire_pick is not None else set()

        self.current_player = 1
        self.possible_pick = HEROES

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)

        result.model_win_rate = self.model_win_rate
        result.is_radiant_player = self.is_radiant_player
        result.current_player = self.current_player

        result.bans = self.bans
        result.radiant_pick = self.radiant_pick.copy()
        result.dire_pick = self.dire_pick.copy()
        result.possible_pick = self.possible_pick
        return result

    def _get_unpick_heroes(self) -> Set[int]:
        return self.possible_pick - self.radiant_pick - self.dire_pick - self.bans

    def _get_ref(self):
        return f'{"R" if self.is_radiant_player else "D"} | {1 if self.current_player == 1 else 0} |'

    def getCurrentPlayer(self) -> int:
        logging.debug(f'{self._get_ref()} getCurrentPlayer: {self.current_player}')
        return self.current_player

    def getPossibleActions(self) -> List[int]:
        logging.debug(f'{self._get_ref()} getPossibleActions: {len(self._get_unpick_heroes())}')
        return list(self._get_unpick_heroes())

    def takeAction(self, action):
        logging.debug(f'{self._get_ref()} takeAction: {action}')
        new_state = deepcopy(self)
        if self.is_radiant_player:
            new_state.radiant_pick.add(action)
        else:
            new_state.dire_pick.add(action)
        new_state.current_player *= -1
        new_state.is_radiant_player = not self.is_radiant_player
        return new_state

    def isTerminal(self) -> bool:
        if self.is_radiant_player:
            is_terminal = len(self.radiant_pick) == 5
        else:
            is_terminal = len(self.dire_pick) == 5

        logging.debug(f'{self._get_ref()} isTerminal: {is_terminal}')
        return is_terminal

    def getReward(self) -> int:
        picks = list(self.radiant_pick), list(self.dire_pick)
        input_vector = self.model_win_rate.prepare_input_vector(picks)
        radiant_win = self.model_win_rate.predict_radiant_win(input_vector)
        if self.is_radiant_player and radiant_win == 1 or not self.is_radiant_player and radiant_win == 0:
            reward = 1
        else:
            reward = 0

        logging.debug(f'{self._get_ref()} getReward: {reward}')
        return reward


class CaptainsModeDraft:
    _PHASE = {
        0: (True, False),
        1: (False, False),
        2: (True, False),
        3: (False, False),
        4: (True, False),
        5: (False, False),
        6: (True, True),
        7: (False, True),
        8: (False, True),
        9: (True, True),
        10: (True, False),
        11: (False, False),
        12: (False, True),
        13: (True, True),
        14: (False, True),
        15: (True, True),
        16: (False, False),
        17: (True, False),
        18: (True, True),
        19: (False, True)
    }

    def __init__(self,
                 model_win_rate: WinRateModel,
                 phase: int = 0,
                 bans: Optional[Set[int]] = None,
                 radiant_pick: Optional[Set[int]] = None,
                 dire_pick: Optional[Set[int]] = None):
        self.model_win_rate = model_win_rate
        self.phase = phase

        self.bans = set(bans) if bans is not None else set()
        self.radiant_pick = radiant_pick.copy() if radiant_pick is not None else set()
        self.dire_pick = dire_pick.copy() if dire_pick is not None else set()

        self.current_player = 1
        self.possible_pick = HEROES

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)

        result.model_win_rate = self.model_win_rate
        result.phase = self.phase
        result.current_player = self.current_player

        result.bans = self.bans.copy()
        result.radiant_pick = self.radiant_pick.copy()
        result.dire_pick = self.dire_pick.copy()
        result.possible_pick = self.possible_pick
        return result

    def _get_unpick_heroes(self) -> Set[int]:
        return self.possible_pick - self.radiant_pick - self.dire_pick - self.bans

    def _get_ref(self):
        return f'{self.phase} | {self.__class__._PHASE[self.phase]} |'

    def getCurrentPlayer(self) -> int:
        logging.debug(f'{self._get_ref()} getCurrentPlayer: {self.current_player}')
        return self.current_player

    def getPossibleActions(self) -> List[int]:
        logging.debug(f'{self._get_ref()} getPossibleActions: {len(self._get_unpick_heroes())}')
        return list(self._get_unpick_heroes())

    def takeAction(self, action):
        logging.debug(f'{self._get_ref()} takeAction: {action}')
        new_state = deepcopy(self)
        is_radiant_player, is_pick = self.__class__._PHASE[self.phase]
        if not is_pick:
            new_state.bans.add(action)
        else:
            if is_radiant_player:
                new_state.radiant_pick.add(action)
            else:
                new_state.dire_pick.add(action)
        if self.__class__._PHASE[self.phase][0] != self.__class__._PHASE[self.phase + 1][0]:
            new_state.current_player *= -1
        new_state.phase += 1
        return new_state

    def isTerminal(self) -> bool:
        is_terminal = self.phase == 19

        logging.debug(f'{self._get_ref()} isTerminal: {is_terminal}')
        return is_terminal

    def getReward(self) -> int:
        picks = list(self.radiant_pick), list(self.dire_pick)
        input_vector = self.model_win_rate.prepare_input_vector(picks)
        radiant_win = self.model_win_rate.predict_radiant_win(input_vector)

        is_radiant_player, _ = self.__class__._PHASE[self.phase]
        if is_radiant_player and radiant_win == 1 or not is_radiant_player and radiant_win == 0:
            reward = 1
        else:
            reward = 0

        logging.debug(f'{self._get_ref()} getReward: {reward}')
        return reward
