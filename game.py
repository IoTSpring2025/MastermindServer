from player import Player
from model import Model


class Game:
    def __init__(self, game_id: str, model: Model):
        self.game_id: str = game_id
        self.model: Model = model
        self.players: dict[str, Player] = {}
        self.flop: list[str] = None
        self.turn: str = None
        self.river: str = None

    # =============================================================================
    # Hand Management
    # =============================================================================
    def attempt_hand_detection(self, player_id: str, frame_bytes: bytes) -> bool:
        # check if the player hand can be detected and set it
        try:
            output: dict[str, str] = self.model.detect(frame_bytes)

            # player cards must be 2 cards
            if len(output.keys()) == 2:
                self.players[player_id].set_hand(output["cards"])
                return True
            else:
                return False
        except Exception as e:
            return {"error": f"Failed to process image: {e}"}

    def attempt_flop_detection(self, frame_bytes: bytes) -> bool:
        # check if the flop can be detected and set it
        try:
            output: dict[str, str] = self.model.detect(frame_bytes)
            output_cards = set(output["cards"])
            all_player_cards = set()

            for player in self.players.values():
                all_player_cards.update(player.get_hand())

            # the flop will be any card in the output that is not in the player's hand
            diff = output_cards.difference(all_player_cards)

            # flop must be 3 cards
            if len(diff) == 3:
                self.flop.extend(output_cards.difference(all_player_cards))
                return True
            else:
                return False
        except Exception as e:
            return {"error": f"Failed to process image: {e}"}

    def attempt_turn_detection(self, frame_bytes: bytes) -> bool:
        # check if the turn can be detected and set it
        try:
            output: dict[str, str] = self.model.detect(frame_bytes)
            output_cards = set(output["cards"])
            all_player_cards = set()

            for player in self.players.values():
                all_player_cards.update(player.get_hand())

            # the turn will be any card in the output that is not in the player's hand or flop
            diff = output_cards.difference(all_player_cards)
            diff = diff.difference(set(self.flop))

            # turn must be 1 card
            if len(diff) == 1:
                self.turn = diff.pop()
                return True
            else:
                return False
        except Exception as e:
            return {"error": f"Failed to process image: {e}"}

    def attempt_river_detection(self, frame_bytes: bytes) -> bool:
        # check if the river can be detected and set it
        try:
            output: dict[str, str] = self.model.detect(frame_bytes)
            output_cards = set(output["cards"])
            all_player_cards = set()

            for player in self.players.values():
                all_player_cards.update(player.get_hand())

            # the river will be any card in the output that is not in the player's hand or flop or turn
            diff = output_cards.difference(all_player_cards)
            diff = diff.difference(set(self.flop))
            diff = diff.difference(set(self.turn))

            # river must be 1 card
            if len(diff) == 1:
                self.river = diff.pop()
                return True
            else:
                return False
        except Exception as e:
            return {"error": f"Failed to process image: {e}"}

    # =============================================================================
    # Player Management
    # =============================================================================

    def add_player(self, player_id: str) -> str:
        if len(self.players) >= 2:
            return "Max player limit (2) already reached"
        elif player_id in self.players:
            return f"Player {player_id} is already in the game"
        else:
            self.players[player_id] = Player(player_id=player_id)
            return f"Player {player_id} joined {self.game_id}"

    def remove_player(self, player_id: str) -> None:
        if player_id in self.players:
            self.players.pop(player_id, None)

    def set_player_hand(self, player_id: str, hand: list[str]) -> None:
        self.players[player_id].set_hand(hand)

    def get_player_hand(self, player_id: str) -> list[str]:
        return self.players[player_id].get_hand()

    # =============================================================================
    # Board Management
    # =============================================================================
    def set_board(self, board: list[str]) -> None:
        self.board = board

    def get_board(self) -> list[str]:
        return self.board
