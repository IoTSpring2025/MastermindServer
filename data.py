from game import Game, Player
import sys
import os
from model import Model

class MastermindData:
    def __init__(self):
        self.games = {}
        self.model = Model(version=7)
        self.connections = {}
            
    def add_game(self, game_id):
        self.games[game_id] = Game(game_id, model=self.model)
    
    def remove_game(self, game_id):
        self.games.pop(game_id, None)

    def add_player(self, game_id, player_id):
        # check if game exists
        if not game_id in self.games:
            return f"No game with {game_id} exists"
        else:
            self.games[game_id].add_player(player_id)
            return f"Joined {game_id}"

    def remove_player(self, game_id, player_id):
        self.games[game_id].players.pop(player_id, None)

    def get_game_list(self):
        return list(self.games.keys())

    def get_game_players(self, game_id):
        if game_id not in self.games:
            return f"Game {game_id} does not exist."
        return self.games[game_id].players

    def run_inference(self, frame_bytes):
        try:
            return self.model.read_hand(frame_bytes)
        except Exception as e:
            return {"error": f"Failed to process image: {e}"}