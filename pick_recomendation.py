from captain_mode_draft import Draft
from models_win_rate.model_win_rate import ModelWinRate
HEROES_NUM = 130


class PicksRecommendation():
    def __init__(self, model_win_rate: ModelWinRate, p0_model_str, p1_model_str):
        self.draft = Draft(model_win_rate, p0_model_str, p1_model_str)

    def recommend_pick(self, state_pick, state_bans, k=3):
        self.draft.state = state_pick
        self.draft.avail_moves = set(range(130))
        for pick in state_pick[0]:
            self.draft.avail_moves.remove(pick)
        for pick in state_pick[1]:
            self.draft.avail_moves.remove(pick)
        for ban in state_bans[0]:
            self.draft.avail_moves.remove(ban)
        for ban in state_bans[1]:
            self.draft.avail_moves.remove(ban)
        self.draft.move_cnt = [len(state_pick[0]) + len(state_bans[0]), len(state_pick[1]) + len(state_bans[1])]
        #print(self.draft.move_cnt)
        move_cnt = self.draft.move_cnt[0]+self.draft.move_cnt[1]
        if move_cnt in [0, 1, 2, 3, 4, 5,            10, 11, 12, 13,                18, 19]:
            current_move = 'ban'
        elif move_cnt in [                6, 7, 8, 9,                14, 15, 16, 17,        20, 21]:
            current_move = 'pick'
        else:
            raise NameError("Error: sum(move_cnt) >= 22")

        if move_cnt in [0, 2, 4, 6, 9, 11, 13, 15, 17, 19, 20 ]:
            next_player = 0
        else:
            next_player = 1
        self.draft.next_player = next_player
        #print("next_player: ", next_player)
        return current_move, next_player, self.draft.player_models[next_player].get_moves(current_move, k)





