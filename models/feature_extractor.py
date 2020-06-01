import itertools
from collections import Counter
from typing import List

from tqdm import tqdm


class FeatureExtractor:
    def __init__(self):
        self.radiant_synergy_data = {'win': [], 'lose': []}
        self.dire_synergy_data = {'win': [], 'lose': []}
        self.radiant_synergy = {'win': None, 'lose': None}
        self.dire_synergy = {'win': None, 'lose': None}

        self.radiant_counter_data = {'win': [], 'lose': []}
        self.dire_counter_data = {'win': [], 'lose': []}
        self.radiant_counter = {'win': None, 'lose': None}
        self.dire_counter = {'win': None, 'lose': None}

        self.radiant = 1
        self.dire = 0

    def loadAndBuild(self, games):
        for game in tqdm(games):
            self.addSynergyFromGame(game)
        self._buildSynergy()
        self._deleteSynergyData()
        for game in tqdm(games):
            self.addCounterFromGame(game)
        self._buildCounter()
        self._deleteCounterData()

    # Synergy

    def addSynergyFromGame(self, game):
        pairs_radiant_heroes, pairs_dire_heroes, radiant_win = self.getPairSynergyPerTeam(game)
        self.addSynergyFromTeams(pairs_radiant_heroes, pairs_dire_heroes, radiant_win)

    def getPairSynergyPerTeam(self, game) -> (List[int], List[int], bool):
        dire_heroes = [p.hero_id for p in game.players if p.team == self.dire]
        radiant_heroes = [p.hero_id for p in game.players if p.team == self.radiant]
        pairs_dire_heroes = self.getPairFromTeam(dire_heroes)
        pairs_radiant_heroes = self.getPairFromTeam(radiant_heroes)
        return pairs_radiant_heroes, pairs_dire_heroes, game.radiant_win

    @staticmethod
    def getPairFromTeam(team):
        team.sort()
        return list(itertools.combinations(team, 2))

    def addSynergyFromTeams(self, pairs_radiant_heroes, pairs_dire_heroes, radiant_win):
        if radiant_win:
            self.radiant_synergy_data['win'].extend(pairs_radiant_heroes)
            self.dire_synergy_data['lose'].extend(pairs_dire_heroes)
        else:
            self.radiant_synergy_data['lose'].extend(pairs_radiant_heroes)
            self.dire_synergy_data['win'].extend(pairs_dire_heroes)

    # Counter

    def addCounterFromGame(self, game):
        pairs_radiant_heroes, pairs_dire_heroes, radiant_win = self.getPairCounterPerTeam(game)
        self.addCounterFromTeams(pairs_radiant_heroes, pairs_dire_heroes, radiant_win)

    def getPairCounterPerTeam(self, game):
        dire_heroes = [p.hero_id for p in game.players if p.team == self.dire]
        radiant_heroes = [p.hero_id for p in game.players if p.team == self.radiant]
        pairs_dire_heroes = self.getCounterPairs(dire_heroes, radiant_heroes)
        pairs_radiant_heroes = self.getCounterPairs(dire_heroes, radiant_heroes)
        return pairs_radiant_heroes, pairs_dire_heroes, game.radiant_win

    @staticmethod
    def getCounterPairs(current_team, enemy_team):
        return list(itertools.product(current_team, enemy_team))

    def addCounterFromTeams(self, pairs_radiant_heroes, pairs_dire_heroes, radiant_win):
        if radiant_win:
            self.radiant_counter_data['win'].extend(pairs_radiant_heroes)
            self.dire_counter_data['lose'].extend(pairs_dire_heroes)
        else:
            self.radiant_counter_data['lose'].extend(pairs_radiant_heroes)
            self.dire_counter_data['win'].extend(pairs_dire_heroes)

    # Calculations

    def getSynergyValuePerPair(self, pair_id: (int, int), is_radiant):
        if is_radiant:
            return self.radiant_synergy['win'][pair_id] / \
                   (self.radiant_synergy['win'][pair_id] + self.radiant_synergy['lose'][pair_id])
        else:
            return self.dire_synergy['win'][pair_id] / \
                   (self.dire_synergy['win'][pair_id] + self.dire_synergy['lose'][pair_id])

    def getSynergyValue(self, team, is_radiant):
        team.sort()
        pairs = list(itertools.combinations(team, 2))
        return sum([self.getSynergyValuePerPair(pair, is_radiant) for pair in pairs])

    def getCounterValue(self, current_team, enemy_team, is_radiant_current_team):
        return sum([self.getWinRatioCounterPerHero(hero_id, enemy_team, is_radiant_current_team)
                    for hero_id in current_team])

    def getWinRatioCounterPerHero(self, hero_id, enemy_team, is_radiant):
        pairs = list(itertools.product([hero_id], enemy_team))
        return sum([self.getWinRatioCounterPerPair(pair, is_radiant) for pair in pairs])

    def getWinRatioCounterPerPair(self, pair: (int, int), is_radiant):
        if is_radiant:
            return self.radiant_counter['win'][pair] / \
                   (self.radiant_counter['win'][pair] + self.radiant_counter['lose'][pair])
        else:
            return self.dire_counter['win'][pair] / \
                   (self.dire_counter['win'][pair] + self.dire_counter['lose'][pair])

    # Utils

    def _deleteSynergyData(self):
        del self.radiant_synergy_data['win'][:]
        del self.dire_synergy_data['win'][:]
        del self.radiant_synergy_data['lose'][:]
        del self.dire_synergy_data['lose'][:]

    def _deleteCounterData(self):
        del self.radiant_counter_data['win'][:]
        del self.dire_counter_data['win'][:]
        del self.radiant_counter_data['lose'][:]
        del self.dire_counter_data['lose'][:]

    def _buildSynergy(self):
        self.radiant_synergy['win'] = Counter(self.radiant_synergy_data['win'])
        self.radiant_synergy['lose'] = Counter(self.radiant_synergy_data['lose'])
        self.dire_synergy['win'] = Counter(self.dire_synergy_data['win'])
        self.dire_synergy['lose'] = Counter(self.dire_synergy_data['lose'])

    def _buildCounter(self):
        self.radiant_counter['win'] = Counter(self.radiant_counter_data['win'])
        self.radiant_counter['lose'] = Counter(self.radiant_counter_data['lose'])
        self.dire_counter['win'] = Counter(self.dire_counter_data['win'])
        self.dire_counter['lose'] = Counter(self.dire_counter_data['lose'])

    def getRadianSynergy(self):
        return self.radiant_synergy

    def getDireSynergy(self):
        return self.dire_synergy

    def getRadianCounter(self):
        return self.dire_counter

    def getDireCounter(self):
        return self.radiant_counter
