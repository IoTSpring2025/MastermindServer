"""
Example script demonstrating how to use the poker advice feature.

This script creates a game with two players, sets up some sample cards, 
and then requests poker advice for the current game state.

Make sure to set your OPENAI_API_KEY in the .env file before running.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if OPENAI_API_KEY is set
if not os.environ.get("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Add OPENAI_API_KEY=your_openai_api_key to your .env file")
    exit(1)

# API endpoint (update with your actual server URL if different)
API_BASE = "http://localhost:8080"

def create_game():
    """Create a new game with two players"""
    game_id = "test_game"
    player1_id = "player1"
    player2_id = "player2"
    
    # Create game
    requests.post(f"{API_BASE}/create?game_id={game_id}&player_id={player1_id}")
    
    # Add second player
    requests.post(f"{API_BASE}/join?game_id={game_id}&player_id={player2_id}")
    
    return game_id, player1_id, player2_id

def manually_set_cards(game_id, player1_id, player2_id):
    """
    For this example, we'll simulate that cards have been detected.
    In a real application, cards would be detected through the video stream.
    """
    # This is a simplified example - in a real app, you would detect cards through the 
    # video stream and the API, not by direct variable setting
    print("Note: In a real application, cards would be detected through the video stream.")
    print("This example simulates that cards have already been detected.")
    
    # For demonstration purposes, print what the game state should be
    print("\nSimulated game state:")
    print(f"Player 1 hand: Ace of Spades, King of Hearts")
    print(f"Player 2 hand: Jack of Diamonds, Queen of Clubs")
    print(f"Flop: 7 of Hearts, 2 of Clubs, 5 of Spades")
    print(f"Turn: 10 of Diamonds")
    print(f"River: 3 of Hearts")
    
    print("\nIn a real application, these cards would be detected through the camera.\n")

def get_simple_advice(game_id, player1_id, player2_id):
    """Get simple poker advice (just the action)"""
    response = requests.get(
        f"{API_BASE}/get_poker_advice",
        params={
            "game_id": game_id,
            "player_id": player1_id,
            "opponent_id": player2_id,
            "pot_size": 100,
            "player_stack": 500,
            "opponent_stack": 450
        }
    )
    
    if response.status_code == 200:
        print("Simple Advice:")
        print(f"Recommended action: {response.json()['action']}")
    else:
        print(f"Error getting simple advice: {response.text}")

def get_detailed_advice(game_id, player1_id, player2_id):
    """Get detailed poker advice (action, explanation, confidence)"""
    response = requests.get(
        f"{API_BASE}/get_detailed_poker_advice",
        params={
            "game_id": game_id,
            "player_id": player1_id,
            "opponent_id": player2_id,
            "pot_size": 100,
            "player_stack": 500,
            "opponent_stack": 450
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\nDetailed Advice:")
        print(f"Recommended action: {result['action']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Confidence: {result['confidence']}%")
    else:
        print(f"Error getting detailed advice: {response.text}")

def main():
    """Main function to run the example"""
    print("Poker Advice Example")
    print("====================")
    print("This example demonstrates how to use the poker advice feature.")
    print("Make sure your server is running and OPENAI_API_KEY is set in your .env file.")
    
    # Create game and players
    game_id, player1_id, player2_id = create_game()
    print(f"\nCreated game {game_id} with players {player1_id} and {player2_id}")
    
    # Set up cards (simulated)
    manually_set_cards(game_id, player1_id, player2_id)
    
    # Get poker advice
    print("\nRequesting poker advice...")
    get_simple_advice(game_id, player1_id, player2_id)
    get_detailed_advice(game_id, player1_id, player2_id)
    
    print("\nNote: If you see error messages, make sure that:")
    print("1. Your server is running")
    print("2. OPENAI_API_KEY is set in your .env file")
    print("3. The cards have been properly detected through the video stream")

if __name__ == "__main__":
    main() 