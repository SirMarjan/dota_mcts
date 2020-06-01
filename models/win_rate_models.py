from typing import List

import numpy as np

from models.feature_extractor import FeatureExtractor

HEROES_NUM = 130


class WinRateModel:

    def prepare_input_vector(self, picks: [List[int], List[int]]) -> np.ndarray:
        pass

    def predict_radiant_win(self, input_vector) -> int:
        pass


class WinRateSciKitModel(WinRateModel):

    def __init__(self, feature_extractor: FeatureExtractor, model):
        self.f_e = feature_extractor
        self.model = model

    def prepare_input_vector(self, picks: [List[int], List[int]]) -> np.ndarray:
        radiant = np.zeros(HEROES_NUM)
        radiant[picks[0]] = 1

        dire = np.zeros(HEROES_NUM)
        dire[picks[0]] = 1

        synergy = self.f_e.getSynergyValue(picks[0], True) - self.f_e.getSynergyValue(picks[1], False)
        countering = self.f_e.getCounterValue(picks[0], picks[1], True)
        return np.hstack([radiant, dire, synergy, countering]).reshape(1, -1)

    def predict_radiant_win(self, input_vector) -> int:
        return int(self.model.predict(input_vector))
