"""
Example script demonstrating how to use the poker advice feature with camera-based card detection.

This script creates a game with two players, captures video from the camera to detect cards,
and then requests poker advice for the current game state.

Make sure to set your OPENAI_API_KEY in the .env file before running.
"""

import os
import requests
import json
import asyncio
import cv2
import websockets
import argparse
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Check if OPENAI_API_KEY is set
if not os.environ.get("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Add OPENAI_API_KEY=your_openai_api_key to your .env file")
    exit(1)

# API endpoint (update with your actual server URL if different)
API_BASE = "http://localhost:8080"
WS_BASE = "ws://0.0.0.0:8080/"

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

async def detect_cards_with_camera(game_id, player_id, duration=30, display=True):
    """
    Use camera to detect cards for a specified duration.
    
    Args:
        game_id: The ID of the game
        player_id: The ID of the player
        duration: How long to run the detection (in seconds)
        display: Whether to display the camera feed
    """
    uri = WS_BASE + f"socket/video?game_id={game_id}&player_id={player_id}"
    print(f"\nStarting card detection with camera for {duration} seconds...")
    print("Show your cards to the camera. Press 'q' to stop early.")

    # connect to web socket
    async with websockets.connect(uri) as websocket:
        # open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open video capture device.")
            return False

        start_time = time.time()
        detected_cards = set()
        
        try:
            while time.time() - start_time < duration:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break

                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    print("Error: Failed to encode frame")
                    continue

                # Send frame to server for detection
                frame_bytes = buffer.tobytes()
                await websocket.send(frame_bytes)
                response = await websocket.recv()
                data = json.loads(response)
                
                # Print detection results
                if isinstance(data, dict):
                    if "error" in data:
                        print("Error:", data["error"])
                    else:
                        if "detected cards" in data:
                            detected_data = data["detected cards"]
                            
                            # Handle both dictionary and list formats for detected cards
                            if isinstance(detected_data, dict):
                                for card, confidence in detected_data.items():
                                    detected_cards.add(card)
                                print(f"Detected cards (with confidence): {detected_data}")
                            elif isinstance(detected_data, list):
                                for card in detected_data:
                                    detected_cards.add(card)
                                print(f"Detected cards: {detected_data}")
                            
                        if "status" in data:
                            print(f"Status: {data['status']}")
                
                # Display detection results on frame if requested
                if display:
                    # Display detected card names on the frame
                    if isinstance(data, dict) and "detected cards" in data:
                        detected_data = data["detected cards"]
                        y_pos = 30
                        
                        # Handle both dictionary and list formats for detected cards
                        if isinstance(detected_data, dict):
                            for card, confidence in detected_data.items():
                                text = f"{card}: {confidence}%"
                                cv2.putText(frame, text, (10, y_pos), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                y_pos += 30
                        elif isinstance(detected_data, list):
                            for card in detected_data:
                                text = f"{card}"
                                cv2.putText(frame, text, (10, y_pos), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                y_pos += 30
                    
                    cv2.imshow("Card Detection", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                # Check current game state
                print("--------------------------------")
                response = requests.get(
                    f"{API_BASE}/get_hand?game_id={game_id}&player_id={player_id}"
                )
                hand = response.json()
                if not isinstance(hand, dict):
                    print("Hand detected:", hand)
                
                # Check flop
                response = requests.get(
                    f"{API_BASE}/get_flop?game_id={game_id}"
                )
                flop = response.json()
                if not isinstance(flop, dict):
                    print("Flop detected:", flop)
                
                # Check turn
                response = requests.get(
                    f"{API_BASE}/get_turn?game_id={game_id}"
                )
                turn = response.json()
                if not isinstance(turn, dict):
                    print("Turn detected:", turn)
                
                # Check river
                response = requests.get(
                    f"{API_BASE}/get_river?game_id={game_id}"
                )
                river = response.json()
                if not isinstance(river, dict):
                    print("River detected:", river)

                # Brief pause to avoid flooding the server
                await asyncio.sleep(0.1)

        except Exception as e:
            print("Exception occurred:", e)
            return False
        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()

        print("\nCard detection completed.")
        print(f"Cards detected during the session: {list(detected_cards)}")
        return True

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

async def main_async(use_camera, display):
    """Async main function to run the example"""
    print("Poker Advice Example")
    print("====================")
    print("This example demonstrates how to use the poker advice feature.")
    print("Make sure your server is running and OPENAI_API_KEY is set in your .env file.")
    
    # Create game and players
    game_id, player1_id, player2_id = create_game()
    print(f"\nCreated game {game_id} with players {player1_id} and {player2_id}")
    
    # Set up cards (either with camera or simulated)
    if use_camera:
        detection_success = await detect_cards_with_camera(game_id, player1_id, duration=30, display=display)
        if not detection_success:
            print("Card detection failed or was incomplete.")
            return
    else:
        manually_set_cards(game_id, player1_id, player2_id)
    
    # Get poker advice
    print("\nRequesting poker advice...")
    get_simple_advice(game_id, player1_id, player2_id)
    get_detailed_advice(game_id, player1_id, player2_id)
    
    print("\nNote: If you see error messages, make sure that:")
    print("1. Your server is running")
    print("2. OPENAI_API_KEY is set in your .env file")
    print("3. The cards have been properly detected through the video stream")

def main():
    """Main function to parse args and run the example"""
    parser = argparse.ArgumentParser(description="Run poker advice example")
    parser.add_argument("--no-camera", action="store_true", help="Don't use camera, simulate detection")
    parser.add_argument("--no-display", action="store_true", help="Don't display camera feed")
    args = parser.parse_args()
    
    use_camera = not args.no_camera
    display = not args.no_display
    
    asyncio.run(main_async(use_camera, display))

if __name__ == "__main__":
    main()