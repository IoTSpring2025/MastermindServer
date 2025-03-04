from player import Player
from model import Model


class Game:
    def __init__(self, game_id: str, model: Model):
        self.game_id: str = game_id
        self.model: Model = model
        self.players: dict[str, Player] = {}
        self.flop: set[str] = []
        self.turn: str = None
        self.river: str = None

    # =============================================================================
    # Hand Management
    # =============================================================================
    def attempt_hand_detection(self, player_id: str, predictions: list[str]) -> bool:
        try:
            # ensure player exists
            if player_id not in self.players:
                print(f"Player {player_id} not found")
                return False

            # must have 2 cards
            if len(predictions) == 2 and self.players[player_id].get_hand() == set():
                print(
                    f"Setting hand for player {player_id}: {predictions}"
                )  # Debug log
                self.players[player_id].set_hand(set(predictions))
                return True
            else:
                print(
                    f"Wrong number of cards detected: {len(predictions)}"
                )  # Debug log
                return False
        except Exception as e:
            print(f"Error in hand detection: {e}")
            return False

    def attempt_flop_detection(
        self, player_id: str, predictions: dict[str, str]
    ) -> bool:
        # check if the flop can be detected and set it
        if len(predictions) == 0:
            return False

        output_cards = set(predictions.keys())
        player_cards = self.players[player_id].get_hand()

        # the flop will be any card in the output that is not in the player's hand
        diff = output_cards.difference(player_cards)

        # flop must be 3 cards
        if len(diff) == 3:
            self.flop.extend(diff)
            return True
        else:
            return False

    def attempt_turn_detection(
        self, player_id: str, predictions: dict[str, str]
    ) -> bool:
        # check if the turn can be detected and set it
        if len(predictions) == 0:
            return False
        output_cards = set(predictions.keys())
        player_cards = self.players[player_id].get_hand()

        # the turn will be any card in the output that is not in the player's hand or flop
        diff = output_cards.difference(player_cards)
        diff = diff.difference(set(self.flop))

        # turn must be 1 card
        if len(diff) == 1:
            self.set_turn(diff.pop())
            return True
        else:
            return False

    def attempt_river_detection(
        self, player_id: str, predictions: dict[str, str]
    ) -> bool:
        # check if the river can be detected and set it
        if len(predictions) == 0:
            return False

        output_cards = set(predictions.keys())
        player_cards = self.players[player_id].get_hand()

        # the turn will be any card in the output that is not in the player's hand or flop
        diff = output_cards.difference(player_cards)
        diff = diff.difference(set(self.flop))
        diff = diff.difference(set(self.turn))

        # turn must be 1 card
        if len(diff) == 1:
            self.set_river(diff.pop())
            return True
        else:
            return False

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
        if player_id not in self.players:
            print(f"Cannot set hand: Player {player_id} not found")
            return

        print(f"Setting hand for {player_id}: {hand}")
        self.players[player_id].set_hand(set(hand))

    def get_player_hand(self, player_id: str) -> set[str]:
        if player_id not in self.players:
            print(f"Cannot get hand: Player {player_id} not found")
            return set()

        hand = self.players[player_id].get_hand()
        print(f"Getting hand for {player_id}: {hand}")
        return hand

    # =============================================================================
    # Board Management
    # =============================================================================

    def set_flop(self, flop: list[str]) -> None:
        self.flop = flop

    def get_flop(self) -> list[str] | dict[str, str]:
        return self.flop

    def set_turn(self, turn: str) -> None:
        self.turn = turn

    def get_turn(self) -> str | dict[str, str]:
        return self.turn

    def set_river(self, river: str) -> None:
        self.river = river

    def get_river(self) -> str | dict[str, str]:
        return self.river
