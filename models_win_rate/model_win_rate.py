from typing import List
from tensorflow import keras
import numpy as np
HEROES_NUM = 130


class ModelWinRate():
    model = None

    def load(self, path: str):
        pass

    # pred probability of win - second team
    def predict_win(self, input) -> float:
        pass

    # input examp;e- [[1,2, 60, 30, 34], [3, 45, 70, 90, 111]] - pick
    # output: input vector to model
    def prepare_input_vector(self, picks: [List[int], List[int]]) -> List[float]:
        pass


class ModelWinRateKeras130(ModelWinRate):

    def prepare_input_vector(self, picks: [List[int], List[int]]) -> List[float]:
        x = np.zeros((1, HEROES_NUM))
        x[0, picks[0]] = 1
        x[0, picks[1]] = -1
        return x

    def predict_win(self, input) -> float:
        return self.model.predict(input)[0, 1]
        #y = self.model.predict(input)[0]
        #if y[0]> y[1]:
        #return 0
        #return 1


    def load(self, path):
        self.model = keras.models.load_model(path)
