from player import Player
from model import Model
import requests
import json
import os
from typing import Dict, Any, List, Optional


class Game:
    def __init__(self, game_id: str, model: Model):
        self.game_id: str = game_id
        self.model: Model = model
        self.players: dict[str, Player] = {}
        self.flop: set[str] = []
        self.turn: str = None
        self.river: str = None
        self.turn_detection_lock = False  # Prevent concurrent turn detection
        self.river_detection_lock = False  # Prevent concurrent river detection
        self.recently_assigned_cards = set()  # Track recently assigned cards
        self.CONFIDENCE_THRESHOLD = 90.0  # Minimum confidence percentage for card detection
        self.game_stage = "hand"  # Track current game stage: hand, flop, turn, river

    # =============================================================================
    # Card Management Helpers
    # =============================================================================
    def is_card_already_assigned(self, card: str) -> bool:
        """Check if a card is already assigned to any player's hand, flop, turn, or river"""
        if card is None:
            print("Warning: Trying to check if None card is assigned")
            return False
            
        # Check if card is in any player's hand
        for player_id, player in self.players.items():
            if card in player.get_hand():
                print(f"Card {card} already in player {player_id}'s hand")
                return True
                
        # Check if card is in flop
        if card in self.flop:
            print(f"Card {card} already in flop")
            return True
            
        # Check if card is the turn
        if self.turn == card:
            print(f"Card {card} already assigned as turn")
            return True
            
        # Check if card is the river
        if self.river == card:
            print(f"Card {card} already assigned as river")
            return True
            
        return False

    # =============================================================================
    # Hand Management
    # =============================================================================
    def attempt_hand_detection(self, player_id: str, predictions: dict[str, str]) -> bool:
        try:
            # ensure player exists
            if player_id not in self.players:
                print(f"Player {player_id} not found")
                return False
                
            # Filter out cards with confidence values below the threshold
            high_confidence_cards = []
            for card, confidence in predictions.items():
                try:
                    if float(confidence) >= self.CONFIDENCE_THRESHOLD:
                        high_confidence_cards.append(card)
                    else:
                        print(f"Rejecting {card} with low confidence: {confidence}%")
                except (ValueError, TypeError):
                    print(f"Invalid confidence value for {card}: {confidence}")
                    
            if not high_confidence_cards:
                print("No cards with confidence above threshold")
                return False

            # Filter out cards that are already assigned elsewhere
            valid_predictions = [card for card in high_confidence_cards if not self.is_card_already_assigned(card)]
            
            # must have 2 cards
            if len(valid_predictions) == 2 and self.players[player_id].get_hand() == set():
                print(
                    f"Setting hand for player {player_id}: {valid_predictions}"
                )  # Debug log
                self.players[player_id].set_hand(set(valid_predictions))
                return True
            else:
                print(
                    f"Wrong number of valid cards detected: {len(valid_predictions)}"
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
            
        # Filter out cards with confidence values below the threshold
        high_confidence_cards = {}
        for card, confidence in predictions.items():
            try:
                if float(confidence) >= self.CONFIDENCE_THRESHOLD:
                    high_confidence_cards[card] = confidence
                else:
                    print(f"Rejecting {card} with low confidence: {confidence}%")
            except (ValueError, TypeError):
                print(f"Invalid confidence value for {card}: {confidence}")
                
        if not high_confidence_cards:
            print("No cards with confidence above threshold")
            return False

        output_cards = set(high_confidence_cards.keys())
        player_cards = self.players[player_id].get_hand()

        # the flop will be any card in the output that is not in the player's hand
        # and not already assigned to another collection
        diff = output_cards.difference(player_cards)
        valid_cards = [card for card in diff if not self.is_card_already_assigned(card)]

        # flop must be 3 cards
        if len(valid_cards) == 3:
            self.flop.extend(valid_cards)
            return True
        else:
            print(f"Wrong number of valid flop cards: {len(valid_cards)}")
            return False

    def attempt_turn_detection(
        self, player_id: str, predictions: dict[str, str]
    ) -> bool:
        # Skip if lock is active to prevent double detection
        if self.turn_detection_lock:
            print("Turn detection locked - preventing double assignment")
            return False
            
        if len(predictions) == 0:
            return False
            
        try:
            # Lock to prevent other concurrent calls
            self.turn_detection_lock = True
            
            # Check if we already have a turn card
            if self.turn is not None:
                print("Turn already assigned - duplicate detection prevented")
                return False
                
            # Update game stage and clear recently assigned cards if needed
            self._update_game_stage("turn")
                
            # Filter out cards with confidence values below the threshold
            high_confidence_cards = {}
            for card, confidence in predictions.items():
                try:
                    if float(confidence) >= self.CONFIDENCE_THRESHOLD:
                        high_confidence_cards[card] = confidence
                    else:
                        print(f"Rejecting {card} with low confidence: {confidence}%")
                except (ValueError, TypeError):
                    print(f"Invalid confidence value for {card}: {confidence}")
                    
            if not high_confidence_cards:
                print("No cards with confidence above threshold")
                return False
            
            output_cards = set(high_confidence_cards.keys())
            player_cards = self.players[player_id].get_hand()

            # Filter out any cards already in various collections
            diff = output_cards.difference(player_cards)
            diff = diff.difference(set(self.flop))
            # Also filter out recently assigned cards
            diff = diff.difference(self.recently_assigned_cards)
            
            # Further filter to make sure no card is already assigned elsewhere
            valid_cards = [card for card in diff if not self.is_card_already_assigned(card)]

            # turn must be 1 card
            if len(valid_cards) == 1:
                turn_card = valid_cards[0]
                # Double check the card isn't already assigned
                if not self.is_card_already_assigned(turn_card):
                    self.turn = turn_card
                    # Remember this card to avoid using it again soon
                    self.recently_assigned_cards.add(turn_card)
                    return True
                else:
                    print(f"Card {turn_card} already assigned elsewhere")
                    return False
            else:
                print(f"Wrong number of valid turn cards: {len(valid_cards)}")
                return False
        finally:
            # Always release the lock when done
            self.turn_detection_lock = False

    def attempt_river_detection(
        self, player_id: str, predictions: dict[str, str]
    ) -> bool:
        # Skip if lock is active to prevent double detection
        if self.river_detection_lock:
            print("River detection locked - preventing double assignment")
            return False
            
        if len(predictions) == 0:
            return False
            
        try:
            # Lock to prevent other concurrent calls
            self.river_detection_lock = True
            
            # Check if we already have a river card
            if self.river is not None:
                print("River already assigned - duplicate detection prevented")
                return False
                
            # Make sure turn card is assigned first
            if self.turn is None:
                print("Turn card must be assigned before river")
                return False
                
            # Debug the current state
            print(f"Current turn card: {self.turn}")
            print(f"Attempting river detection with predictions: {predictions}")
                
            # Update game stage and clear recently assigned cards if needed
            self._update_game_stage("river")
                
            # Filter out cards with confidence values below the threshold
            high_confidence_cards = {}
            for card, confidence in predictions.items():
                try:
                    if float(confidence) >= self.CONFIDENCE_THRESHOLD:
                        high_confidence_cards[card] = confidence
                    else:
                        print(f"Rejecting {card} with low confidence: {confidence}%")
                except (ValueError, TypeError):
                    print(f"Invalid confidence value for {card}: {confidence}")
                    
            if not high_confidence_cards:
                print("No cards with confidence above threshold")
                return False
            
            output_cards = set(high_confidence_cards.keys())
            player_cards = self.players[player_id].get_hand()

            # Filter out cards from player hand, flop and turn
            diff = output_cards.difference(player_cards)
            diff = diff.difference(set(self.flop))
            
            # Ensure turn card is filtered out
            if self.turn in diff:
                print(f"Removing turn card {self.turn} from river candidates")
                diff.remove(self.turn)
            
            # Also filter out recently assigned cards
            diff = diff.difference(self.recently_assigned_cards)
                
            # Further filter to make sure no card is already assigned elsewhere
            valid_cards = [card for card in diff if not self.is_card_already_assigned(card)]
            
            # Debug valid cards
            print(f"Valid river card candidates after filtering: {valid_cards}")

            # river must be 1 card
            if len(valid_cards) == 1:
                river_card = valid_cards[0]
                
                # TRIPLE check the card isn't already assigned and isn't the turn card
                if self.turn == river_card:
                    print(f"ERROR: River card {river_card} is the same as turn card {self.turn}! Rejecting.")
                    return False
                    
                if not self.is_card_already_assigned(river_card):
                    self.river = river_card
                    print(f"Successfully assigned river card: {river_card}, turn is: {self.turn}")
                    # Remember this card to avoid using it again soon
                    self.recently_assigned_cards.add(river_card)
                    return True
                else:
                    print(f"Card {river_card} already assigned elsewhere")
                    return False
            else:
                print(f"Wrong number of valid river cards: {len(valid_cards)}")
                return False
        finally:
            # Always release the lock when done
            self.river_detection_lock = False

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
        # Double-check the card isn't already assigned somewhere else
        if not self.is_card_already_assigned(turn):
            self.turn = turn
            print(f"Successfully set turn to {turn}")
        else:
            print(f"Cannot set turn to {turn} as it is already assigned elsewhere")

    def get_turn(self) -> str | dict[str, str]:
        return self.turn

    def set_river(self, river: str) -> None:
        # Double-check the card isn't already assigned somewhere else
        if not self.is_card_already_assigned(river):
            # Extra check to ensure river isn't the same as turn
            if self.turn == river:
                print(f"ERROR: Cannot set river to {river} as it is the same as turn card")
                return
            self.river = river
            print(f"Successfully set river to {river}")
        else:
            print(f"Cannot set river to {river} as it is already assigned elsewhere")

    def get_river(self) -> str | dict[str, str]:
        return self.river

    def _update_game_stage(self, new_stage: str) -> None:
        """Update the game stage and clear recently assigned cards when moving to a new stage"""
        if self.game_stage != new_stage:
            self.game_stage = new_stage
            self.recently_assigned_cards.clear()
            print(f"Game stage updated to {new_stage}, cleared recently assigned cards")
            
    # =============================================================================
    # ChatGPT Integration for Poker Advice
    # =============================================================================
    
    def get_game_stage(self) -> str:
        """
        Determine the current poker game stage based on community cards.
        
        Returns:
            str: The game stage ('pre-flop', 'flop', 'turn', or 'river')
        """
        if not self.flop:
            return "pre-flop"
        elif self.flop and self.turn is None:
            return "flop"
        elif self.flop and self.turn and self.river is None:
            return "turn"
        elif self.flop and self.turn and self.river:
            return "river"
        else:
            return "unknown"
    
    def get_board_cards(self) -> List[str]:
        """
        Get all community cards currently on the board.
        
        Returns:
            List[str]: List of all community cards
        """
        board_cards = []
        
        # Add flop cards if they exist
        if self.flop:
            board_cards.extend(self.flop)
        
        # Add turn card if it exists
        if self.turn:
            board_cards.append(self.turn)
            
        # Add river card if it exists
        if self.river:
            board_cards.append(self.river)
            
        return board_cards
    
    def get_poker_advice(self, player_id: str, opponent_id: str, pot_size: int = 0, 
                        player_stack: int = 0, opponent_stack: int = 0) -> str:
        """
        Query ChatGPT API to get poker advice for the current game state
        
        Args:
            player_id: ID of the player requesting advice
            opponent_id: ID of the opponent player
            pot_size: Current pot size 
            player_stack: Player's remaining chips
            opponent_stack: Opponent's remaining chips
            
        Returns:
            str: Recommended action ('raise', 'check', or 'fold') and explanation
        """
        # Ensure both players exist
        if player_id not in self.players or opponent_id not in self.players:
            return "Error: One or both players not found in the game"
        
        # Get player hands
        player_hand = list(self.players[player_id].get_hand())
        opponent_hand = list(self.players[opponent_id].get_hand())
        
        # Get board cards
        board_cards = self.get_board_cards()
        
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set"
        
        # Determine game stage
        game_stage = self.get_game_stage()
        
        # Create the prompt
        board_info = f"- Board cards: {', '.join(board_cards)}" if board_cards else "- Board cards: none (pre-flop)"
        
        prompt = f"""
In a heads-up poker game with both hands face up, currently at the {game_stage} stage:
- My cards: {', '.join(player_hand)}
- Opponent's cards: {', '.join(opponent_hand)}
{board_info}
- Pot size: {pot_size}
- My stack: {player_stack}
- Opponent's stack: {opponent_stack}

Given this scenario, what is the best poker action? Answer with only one word: 'raise', 'check', or 'fold'.
"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4",  # You can change this to a different model
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a poker strategy expert. Respond with only one word: 'raise', 'check', or 'fold'."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 10,
            "temperature": 0.2,
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions", 
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Extract the decision
            result = response.json()
            decision = result["choices"][0]["message"]["content"].strip().lower()
            
            # Ensure we get only one of the expected responses
            valid_responses = ["raise", "check", "fold"]
            if any(valid in decision for valid in valid_responses):
                for valid in valid_responses:
                    if valid in decision:
                        return valid
            return "check"  # Default if we can't parse a clear answer
        
        except Exception as e:
            print(f"Error querying ChatGPT: {str(e)}")
            return f"Error: {str(e)}"
            
    def get_detailed_poker_advice(self, player_id: str, opponent_id: str, pot_size: int = 0, 
                                player_stack: int = 0, opponent_stack: int = 0) -> Dict[str, Any]:
        """
        Get detailed poker advice including explanation and confidence level
        
        Args:
            player_id: ID of the player requesting advice
            opponent_id: ID of the opponent player
            pot_size: Current pot size 
            player_stack: Player's remaining chips
            opponent_stack: Opponent's remaining chips
            
        Returns:
            Dict with action, explanation, and confidence level
        """
        # Ensure both players exist
        if player_id not in self.players or opponent_id not in self.players:
            return {"action": "error", "explanation": "One or both players not found in the game", "confidence": 0}
        
        # Get player hands
        player_hand = list(self.players[player_id].get_hand())
        opponent_hand = list(self.players[opponent_id].get_hand())
        
        # Get board cards
        board_cards = self.get_board_cards()
        
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"action": "error", "explanation": "OPENAI_API_KEY environment variable not set", "confidence": 0}
        
        # Determine game stage
        game_stage = self.get_game_stage()
        
        # Create the prompt
        board_info = f"- Board cards: {', '.join(board_cards)}" if board_cards else "- Board cards: none (pre-flop)"
        
        prompt = f"""
In a heads-up poker game with both hands face up, currently at the {game_stage} stage:
- My cards: {', '.join(player_hand)}
- Opponent's cards: {', '.join(opponent_hand)}
{board_info}
- Pot size: {pot_size}
- My stack: {player_stack}
- Opponent's stack: {opponent_stack}

Given this scenario:
1. What is the best poker action? Choose one: 'raise', 'check', or 'fold'.
2. Provide a brief explanation (1-2 sentences) for why this is the best action.
3. Give a confidence level between 0-100% for your recommendation.

Format your response as JSON: {{"action": "chosen_action", "explanation": "your brief explanation", "confidence": confidence_number}}
"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4",  # You can change this to a different model
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a poker strategy expert. Respond with JSON containing action, explanation and confidence level."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 150,
            "temperature": 0.2,
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions", 
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Extract the response
            result = response.json()
            response_content = result["choices"][0]["message"]["content"].strip()
            
            # Parse the JSON response
            try:
                advice_data = json.loads(response_content)
                # Validate required fields
                if "action" not in advice_data:
                    advice_data["action"] = "check"
                if "explanation" not in advice_data:
                    advice_data["explanation"] = "No explanation provided"
                if "confidence" not in advice_data:
                    advice_data["confidence"] = 50
                
                # Ensure action is valid
                valid_actions = ["raise", "check", "fold"]
                if advice_data["action"].lower() not in valid_actions:
                    advice_data["action"] = "check"
                
                return advice_data
                
            except json.JSONDecodeError:
                # Fallback in case of parsing error
                default_response = {"action": "check", "explanation": "Could not parse AI response", "confidence": 50}
                return default_response
        
        except Exception as e:
            print(f"Error querying ChatGPT: {str(e)}")
            return {"action": "error", "explanation": f"Error: {str(e)}", "confidence": 0}
