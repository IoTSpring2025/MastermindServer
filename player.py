class Player:
    def __init__(self, player_id):
        self.player_id: str = player_id
        self.hand: list[str] = None

    def set_hand(self, hand: list[str]) -> None:
        self.hand = hand

    def get_hand(self) -> list[str]:
        if self.hand:
            return self.hand
        return "No hand detected."
