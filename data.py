from game import Game
from model import Model
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Initialize Firebase with error handling
load_dotenv()
try:
    cred_path = os.getenv('FIREBASE_CREDENTIALS')
    print(f"Loading Firebase credentials from: {cred_path}")
    if not cred_path:
        raise ValueError("FIREBASE_CREDENTIALS not found in .env file")
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")
        
    cred = credentials.Certificate(cred_path)
    # Initialize with the database URL
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://mastermond-8816a-default-rtdb.firebaseio.com'
    })
    database = db.reference()
    print("✅ Firebase Realtime Database initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing Firebase: {e}")
    import traceback
    traceback.print_exc()
    database = None

class MastermindData:
    def __init__(self):
        self.games: dict[str, Game] = {}
        self.model = Model(version=7)
        self.connections: dict[str, dict[str, str]] = {}
        self.db = database
        if not self.db:
            print("⚠️ Warning: Firebase database not initialized!")

    def update_firebase(self, game_id: str, player_id: str, detected_cards: dict) -> None:
        """Update Firebase Realtime Database with the current game state and detected cards."""
        if not self.db:
            print("⚠️ Cannot update Firebase: database not initialized")
            return
            
        try:
            # Get current game state
            game = self.games[game_id]
            
            # Create game state data
            game_state = {
                'timestamp': {'.sv': 'timestamp'},
                'detected_cards': detected_cards,
                'player_id': player_id,
                'game_state': {
                    'hand': list(game.players[player_id].get_hand()) if player_id in game.players else [],
                    'flop': list(game.flop) if game.flop else [],
                    'turn': game.turn if game.turn else None,
                    'river': game.river if game.river else None
                }
            }

            print(f"Attempting to update Firebase with data: {game_state}")

            # Get references to the paths we want to update
            game_ref = self.db.child(f'poker_games/{game_id}')
            
            # Update the game state
            game_ref.update({
                'last_updated': {'.sv': 'timestamp'},
                'status': 'active',
                'current_state': game_state['game_state']
            })

            # Add new detection to the detections list
            detections_ref = self.db.child(f'poker_games/{game_id}/players/{player_id}/detections')
            new_detection_ref = detections_ref.push(game_state)
            
            print(f"✅ Firebase updated for game {game_id}, player {player_id}")
            print(f"Detection ID: {new_detection_ref.key}")
        except Exception as e:
            print(f"❌ Error updating Firebase: {e}")
            import traceback
            traceback.print_exc()

    def add_game(self, game_id: str) -> None:
        self.games[game_id] = Game(game_id, model=self.model)
        # Create game in Firebase RTDB
        try:
            game_ref = self.db.child('poker_games').child(game_id)
            game_ref.set({
                'created_at': {'.sv': 'timestamp'},
                'status': 'created',
                'current_state': {
                    'hand': [],
                    'flop': [],
                    'turn': None,
                    'river': None
                }
            })
            print(f"✅ Created new game in Firebase: {game_id}")
        except Exception as e:
            print(f"❌ Error creating game in Firebase: {e}")
            import traceback
            traceback.print_exc()

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
            game = self.games[game_id]
            detection_occurred = False

            if game.players[player_id].get_hand() == set():
                if game.attempt_hand_detection(player_id, predictions):
                    detection_occurred = True
            elif game.flop == []:
                if game.attempt_flop_detection(player_id, predictions):
                    detection_occurred = True
            elif game.turn == None:
                if game.attempt_turn_detection(player_id, predictions):
                    detection_occurred = True
            elif game.river == None:
                if game.attempt_river_detection(player_id, predictions):
                    detection_occurred = True

            # Update Firebase if a new detection occurred
            if detection_occurred:
                self.update_firebase(game_id, player_id, predictions)

            return {
                "detected cards": predictions,
            }

        except Exception as e:
            return {"error": f"Inference error: {str(e)}"}
