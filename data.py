from game import Game
from model import Model


class MastermindData:
    def __init__(self):
        self.games: dict[str, Game] = {}
        self.model = Model(version=7)
        self.connections: dict[str, dict[str, str]] = {}

    def add_game(self, game_id: str) -> None:
        self.games[game_id] = Game(game_id, model=self.model)

    def remove_game(self, game_id: str) -> None:
        self.games.pop(game_id, None)

    def add_player(self, game_id: str, player_id: str) -> str:
        # check if game exists
        if not game_id in self.games:
            return f"No game with {game_id} exists"
        else:
            self.games[game_id].add_player(player_id)
            return f"Joined {game_id}"

    def remove_player(self, game_id: str, player_id: str) -> None:
        self.games[game_id].players.pop(player_id, None)

    def get_game_list(self) -> list[str]:
        return list(self.games.keys())

    def get_game_players(self, game_id: str) -> list[str]:
        if game_id not in self.games:
            return f"Game {game_id} does not exist."
        return self.games[game_id].players

    def run_inference(self, frame: bytes) -> dict[str, str]:
        output = self.model.detect(frame)
        return output
