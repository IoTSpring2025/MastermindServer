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

    def get_hand(self, game_id: str, player_id: str) -> str:
        return self.games[game_id].get_player_hand(player_id)

    def get_flop(self, game_id: str) -> str:
        return self.games[game_id].get_flop()

    def get_turn(self, game_id: str) -> str:
        return self.games[game_id].get_turn()

    def get_river(self, game_id: str) -> str:
        return self.games[game_id].get_river()

    def remove_player(self, game_id: str, player_id: str) -> None:
        self.games[game_id].players.pop(player_id, None)

    def get_game_list(self) -> list[str]:
        return list(self.games.keys())

    def get_game_players(self, game_id: str) -> list[str]:
        if game_id not in self.games:
            return f"Game {game_id} does not exist."
        return self.games[game_id].players

    def run_inference(self, frame: bytes, game_id: str, player_id: str) -> dict:
        try:
            # make sure game exists
            if game_id not in self.games:
                return {"error": f"Game {game_id} not found"}

            # run inference
            predictions = self.model.detect(frame)
            if isinstance(predictions, str) and "Error" in predictions:
                return {"error": predictions}

            # detect stages of game
            if self.games[game_id].players[player_id].get_hand() == set():
                self.games[game_id].attempt_hand_detection(player_id, predictions)
            elif self.games[game_id].flop == []:
                self.games[game_id].attempt_flop_detection(player_id, predictions)
            elif self.games[game_id].turn == None:
                self.games[game_id].attempt_turn_detection(player_id, predictions)
            elif self.games[game_id].river == None:
                self.games[game_id].attempt_river_detection(player_id, predictions)

            return {
                "detected cards": predictions,
            }

        except Exception as e:
            return {"error": f"Inference error: {str(e)}"}
