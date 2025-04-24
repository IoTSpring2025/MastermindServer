#!/usr/bin/env python3
"""
Poker Advice Demo - Demonstrates the ChatGPT integration for poker advice

This script shows how to use the ChatGPT API integration to get poker advice
at different stages of a poker game, using the existing game infrastructure.

Prerequisites:
1. Set the OPENAI_API_KEY environment variable with your API key
   export OPENAI_API_KEY="your-api-key-here"

2. Run this script:
   python poker_advice_demo.py
"""

import os
import sys
from game import Game
from model import Model
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def check_api_key():
    """Check if the OpenAI API key is set"""
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key with:")
        print("  export OPENAI_API_KEY=\"your-api-key-here\"")
        print("Or create a .env file with OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    else:
        print("✓ OpenAI API key found")

def setup_game():
    """Set up a poker game with two players and a model"""
    print("\nSetting up poker game with two players...")
    model = Model()  # Create a model instance
    game = Game(game_id="advice-demo", model=model)
    
    # Add two players
    player1_id = "player1"
    player2_id = "player2"
    game.add_player(player1_id)
    game.add_player(player2_id)
    
    print(f"✓ Created game with players: {player1_id} and {player2_id}")
    
    return game, player1_id, player2_id

def demo_preflop_advice(game, player1_id, player2_id):
    """Demonstrate pre-flop advice"""
    print("\n=============================================")
    print("STAGE: PRE-FLOP")
    print("=============================================")
    
    # Set player hands
    game.set_player_hand(player1_id, ["AS", "KH"])  # Ace of Spades, King of Hearts
    game.set_player_hand(player2_id, ["JD", "QC"])  # Jack of Diamonds, Queen of Clubs
    
    print(f"Player 1 hand: {game.get_player_hand(player1_id)}")
    print(f"Player 2 hand: {game.get_player_hand(player2_id)}")
    
    # Get basic advice
    print("\nGetting basic pre-flop advice...")
    advice = game.get_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=10,
        player_stack=500,
        opponent_stack=500
    )
    print(f"Basic advice: {advice}")
    
    # Get detailed advice
    print("\nGetting detailed pre-flop advice...")
    detailed_advice = game.get_detailed_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=10,
        player_stack=500,
        opponent_stack=500
    )
    print(f"Action: {detailed_advice.get('action', 'unknown')}")
    print(f"Explanation: {detailed_advice.get('explanation', 'No explanation')}")
    print(f"Confidence: {detailed_advice.get('confidence', 0)}%")

def demo_flop_advice(game, player1_id, player2_id):
    """Demonstrate flop advice"""
    print("\n=============================================")
    print("STAGE: FLOP")
    print("=============================================")
    
    # Set flop cards
    game.set_flop(["7H", "2C", "5S"])
    
    print(f"Flop cards: {game.get_flop()}")
    
    # Get basic advice
    print("\nGetting basic flop advice...")
    advice = game.get_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=30,
        player_stack=480,
        opponent_stack=480
    )
    print(f"Basic advice: {advice}")
    
    # Get detailed advice
    print("\nGetting detailed flop advice...")
    detailed_advice = game.get_detailed_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=30,
        player_stack=480,
        opponent_stack=480
    )
    print(f"Action: {detailed_advice.get('action', 'unknown')}")
    print(f"Explanation: {detailed_advice.get('explanation', 'No explanation')}")
    print(f"Confidence: {detailed_advice.get('confidence', 0)}%")

def demo_turn_advice(game, player1_id, player2_id):
    """Demonstrate turn advice"""
    print("\n=============================================")
    print("STAGE: TURN")
    print("=============================================")
    
    # Set turn card
    game.set_turn("10D")
    
    print(f"Turn card: {game.get_turn()}")
    print(f"Board cards: {game.get_board_cards()}")
    
    # Get basic advice
    print("\nGetting basic turn advice...")
    advice = game.get_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=60,
        player_stack=450,
        opponent_stack=450
    )
    print(f"Basic advice: {advice}")
    
    # Get detailed advice
    print("\nGetting detailed turn advice...")
    detailed_advice = game.get_detailed_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=60,
        player_stack=450,
        opponent_stack=450
    )
    print(f"Action: {detailed_advice.get('action', 'unknown')}")
    print(f"Explanation: {detailed_advice.get('explanation', 'No explanation')}")
    print(f"Confidence: {detailed_advice.get('confidence', 0)}%")

def demo_river_advice(game, player1_id, player2_id):
    """Demonstrate river advice"""
    print("\n=============================================")
    print("STAGE: RIVER")
    print("=============================================")
    
    # Set river card
    game.set_river("3H")
    
    print(f"River card: {game.get_river()}")
    print(f"Board cards: {game.get_board_cards()}")
    
    # Get basic advice
    print("\nGetting basic river advice...")
    advice = game.get_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=100,
        player_stack=430,
        opponent_stack=430
    )
    print(f"Basic advice: {advice}")
    
    # Get detailed advice
    print("\nGetting detailed river advice...")
    detailed_advice = game.get_detailed_poker_advice(
        player_id=player1_id,
        opponent_id=player2_id,
        pot_size=100,
        player_stack=430,
        opponent_stack=430
    )
    print(f"Action: {detailed_advice.get('action', 'unknown')}")
    print(f"Explanation: {detailed_advice.get('explanation', 'No explanation')}")
    print(f"Confidence: {detailed_advice.get('confidence', 0)}%")

def main():
    """Main function to run the demo"""
    print("Poker Advice Demo - ChatGPT Integration")
    
    # Check if API key is set
    check_api_key()
    
    # Set up game and players
    game, player1_id, player2_id = setup_game()
    
    # Demonstrate advice at different stages
    demo_preflop_advice(game, player1_id, player2_id)
    demo_flop_advice(game, player1_id, player2_id)
    demo_turn_advice(game, player1_id, player2_id)
    demo_river_advice(game, player1_id, player2_id)
    
    print("\n=============================================")
    print("Demo completed successfully!")
    print("=============================================")

if __name__ == "__main__":
    main()