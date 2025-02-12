class Game():
    def __init__(self, game_id, model):
        self.game_id = game_id
        self.model = model
        self.players = {}
        self.board = None
    
    def add_player(self, player_id):
        if len(self.players) >= 2:
            return "Max player limit (2) already reached"
        elif player_id in self.players:
            return f"Player {player_id} is already in the game"
        else:
            self.players[player_id] = Player(player_id=player_id)
            return f"Player {player_id} joined {self.game_id}"

    def remove_player(self, player_id):
        if player_id in self.players:
            self.players.pop(player_id, None)
        
    def set_board(self, board):
        self.board = board

    def get_board(self):
        return self.board

    def set_player_hand(self, player_id, image_path):
        player_hand = self.model.read_hand(image_path)
        self.players[player_id].set_hand(player_hand)

    def get_player_hand(self, player_id):
        return self.players[player_id].get_hand()
    


class Player():
    def __init__(self, player_id):
        self.player_id = player_id
        self.hand = None
    
    def set_hand(self, hand):
        self.hand = hand

    def get_hand(self):
        if self.hand:
            return self.hand
        return "No hand detected."
