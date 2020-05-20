from captain_mode_draft import Draft
from tensorflow import keras

model = keras.models.load_model('models_win_rate/130_50_relu')
game = Draft(env=model, p0_model_str='random', p1_model_str='mcts')
print("s")