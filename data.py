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

            # detect stages of game - with clear status returns
            detection_status = None
            
            if self.games[game_id].players[player_id].get_hand() == set():
                success = self.games[game_id].attempt_hand_detection(player_id, predictions)
                if success:
                    detection_status = "Hand detected"
            elif self.games[game_id].flop == []:
                success = self.games[game_id].attempt_flop_detection(player_id, predictions)
                if success:
                    detection_status = "Flop detected"
            elif self.games[game_id].turn == None:
                success = self.games[game_id].attempt_turn_detection(player_id, predictions)
                if success:
                    detection_status = "Turn detected"
            elif self.games[game_id].river == None:
                success = self.games[game_id].attempt_river_detection(player_id, predictions)
                if success:
                    detection_status = "River detected"

            response = {
                "detected cards": predictions,
            }
            
            if detection_status:
                response["status"] = detection_status
                
            return response

        except Exception as e:
            return {"error": f"Inference error: {str(e)}"}

    def get_poker_advice(self, game_id: str, player_id: str, opponent_id: str, 
                         pot_size: int = 0, player_stack: int = 0, opponent_stack: int = 0) -> str:
        """
        Get poker advice for a player in a game
        
        Args:
            game_id: ID of the game
            player_id: ID of the player requesting advice
            opponent_id: ID of the opponent player
            pot_size: Current pot size
            player_stack: Player's remaining chips
            opponent_stack: Opponent's remaining chips
            
        Returns:
            str: Recommended action ('raise', 'check', or 'fold')
        """
        if game_id not in self.games:
            return f"Error: Game {game_id} not found"
            
        return self.games[game_id].get_poker_advice(
            player_id=player_id,
            opponent_id=opponent_id,
            pot_size=pot_size,
            player_stack=player_stack,
            opponent_stack=opponent_stack
        )
        
    def get_detailed_poker_advice(self, game_id: str, player_id: str, opponent_id: str, 
                                 pot_size: int = 0, player_stack: int = 0, opponent_stack: int = 0) -> dict:
        """
        Get detailed poker advice including explanation and confidence level
        
        Args:
            game_id: ID of the game
            player_id: ID of the player requesting advice
            opponent_id: ID of the opponent player
            pot_size: Current pot size
            player_stack: Player's remaining chips
            opponent_stack: Opponent's remaining chips
            
        Returns:
            dict: Dictionary with action, explanation, and confidence level
        """
        if game_id not in self.games:
            return {"action": "error", "explanation": f"Game {game_id} not found", "confidence": 0}
            
        return self.games[game_id].get_detailed_poker_advice(
            player_id=player_id,
            opponent_id=opponent_id,
            pot_size=pot_size,
            player_stack=player_stack,
            opponent_stack=opponent_stack
        )
