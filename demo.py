import asyncio
import cv2
import websockets
import json
import argparse
import requests


async def stream_video(game_id, player_id, base_url, display):
    ws_url = f"{base_url}socket/video?game_id={game_id}&player_id={player_id}"
    http_url = base_url.replace('ws://', 'http://').replace('wss://', 'https://')

    # connect to web socket
    async with websockets.connect(ws_url) as websocket:
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
                    f"{http_url}get_hand?game_id={game_id}&player_id={player_id}"
                )
                print("Hand: ", response.json())

                # check flop
                response = requests.get(
                    f"{http_url}get_flop?game_id={game_id}"
                )
                print("Flop: ", response.json())

                # check turn
                response = requests.get(
                    f"{http_url}get_turn?game_id={game_id}"
                )
                print("Turn: ", response.json())

                # check river
                response = requests.get(
                    f"{http_url}get_river?game_id={game_id}"
                )
                print("River: ", response.json())

                frame_bytes = buffer.tobytes()
                await websocket.send(frame_bytes)
                response = await websocket.recv()
                data = json.loads(response)

                if isinstance(data, dict) and "error" in data:
                    print("Error:", data["error"])
                else:
                    print("Detected cards:", data)

                if display:
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

    game_id = "dummy"
    player_id = "dummy"

    if args.remote:
        base_url = "wss://mastermindserver-146524160112.us-central1.run.app/"
        http_url = "https://mastermindserver-146524160112.us-central1.run.app/"
        print("Connecting to remote server")
    else:
        base_url = "ws://localhost:8080/"
        http_url = "http://localhost:8080/"
        print("Connecting to local server")

    # create dummy game
    requests.post(f"{http_url}create?game_id={game_id}&player_id={player_id}")

    # run async
    asyncio.get_event_loop().run_until_complete(
        stream_video(game_id, player_id, base_url, args.display)
    )
