import asyncio
import cv2
import websockets
import json
import argparse
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def stream_video(game_id, player_id, opponent_id, uri, display):
    uri += f"socket/video?game_id={game_id}&player_id={player_id}"
    
    # Track when we last requested advice to avoid spamming
    last_advice_time = 0
    advice_cooldown = 5  # seconds between advice requests
    
    # Connect to web socket
    async with websockets.connect(uri) as websocket:
        # open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open video capture device.")
            return

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break

                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    print("Error: Failed to encode frame")
                    continue

                # check hand
                print("--------------------------------")
                response = requests.get(
                    f"http://0.0.0.0:8080/get_hand?game_id={game_id}&player_id={player_id}"
                )
                player_hand = response.json()
                print("Hand: ", player_hand)

                # check opponent's hand
                response = requests.get(
                    f"http://0.0.0.0:8080/get_hand?game_id={game_id}&player_id={opponent_id}"
                )
                opponent_hand = response.json()
                print("Opponent Hand: ", opponent_hand)

                # check flop
                response = requests.get(
                    f"http://0.0.0.0:8080/get_flop?game_id={game_id}"
                )
                flop = response.json()
                print("Flop: ", flop)

                # check turn
                response = requests.get(
                    f"http://0.0.0.0:8080/get_turn?game_id={game_id}"
                )
                turn = response.json()
                print("Turn: ", turn)

                # check river
                response = requests.get(
                    f"http://0.0.0.0:8080/get_river?game_id={game_id}"
                )
                river = response.json()
                print("River: ", river)
                
                # Get poker advice if we have enough cards and cooldown has passed
                current_time = time.time()
                has_player_hand = isinstance(player_hand, list) and len(player_hand) == 2
                has_opponent_hand = isinstance(opponent_hand, list) and len(opponent_hand) == 2
                
                if has_player_hand and has_opponent_hand and (current_time - last_advice_time > advice_cooldown):
                    print("\n🔮 Getting poker advice...")
                    last_advice_time = current_time
                    
                    try:
                        # Get detailed advice
                        response = requests.get(
                            f"http://0.0.0.0:8080/get_detailed_poker_advice",
                            params={
                                "game_id": game_id,
                                "player_id": player_id,
                                "opponent_id": opponent_id,
                                "pot_size": 100,  # Example values
                                "player_stack": 500,
                                "opponent_stack": 450
                            }
                        )
                        
                        if response.status_code == 200:
                            advice = response.json()
                            print("\n🎲🎲🎲 POKER ADVICE 🎲🎲🎲")
                            print(f"Recommended action: {advice['action'].upper()}")
                            print(f"Explanation: {advice['explanation']}")
                            print(f"Confidence: {advice['confidence']}%")
                            print("🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲\n")
                        else:
                            print(f"Error getting advice: {response.text}")
                    except Exception as e:
                        print(f"Failed to get poker advice: {str(e)}")

                # Send frame for card detection
                frame_bytes = buffer.tobytes()
                await websocket.send(frame_bytes)
                response = await websocket.recv()
                data = json.loads(response)

                if isinstance(data, dict) and "error" in data:
                    print("Error:", data["error"])
                else:
                    print("Detected cards:", data)

                if display:
                    # Show detected cards on the frame
                    if isinstance(data, dict) and "detected cards" in data:
                        detected_data = data["detected cards"]
                        y_pos = 30
                        
                        # Handle both dictionary and list formats for detected cards
                        if isinstance(detected_data, dict):
                            for card, confidence in detected_data.items():
                                text = f"{card}: {confidence}%"
                                cv2.putText(frame, text, (10, y_pos), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                                y_pos += 25
                        elif isinstance(detected_data, list):
                            for card in detected_data:
                                text = f"{card}"
                                cv2.putText(frame, text, (10, y_pos), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                                y_pos += 25
                    
                    cv2.imshow("Video Stream", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

        except Exception as e:
            print("Exception occurred:", e)
        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream video over websockets")
    parser.add_argument("--remote", action="store_true", help="Use remote server")
    parser.add_argument("--display", action="store_true", help="Display camera feed")
    args = parser.parse_args()

    game_id = "demo_game"
    player_id = "player1"
    opponent_id = "player2"  # Second player for advice comparison

    if args.remote:
        uri = "wss://mastermindserver-146524160112.us-central1.run.app/"
        print("Connecting to remote server")
    else:
        uri = "ws://0.0.0.0:8080/"
        print("Connecting to local server")

    # Create dummy game with 2 players
    requests.post(f"http://0.0.0.0:8080/create?game_id={game_id}&player_id={player_id}")
    requests.post(f"http://0.0.0.0:8080/join?game_id={game_id}&player_id={opponent_id}")

    # Run async
    asyncio.get_event_loop().run_until_complete(
        stream_video(game_id, player_id, opponent_id, uri, args.display)
    )
