class Player:
    def __init__(self, player_id):
        self.player_id: str = player_id
        self.hand: set[str] = set()

    def set_hand(self, hand: set[str]) -> None:
        self.hand = hand

    def get_hand(self) -> set[str] | dict[str, str]:
        return self.hand
