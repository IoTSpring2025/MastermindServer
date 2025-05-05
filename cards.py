import asyncio
import cv2
import websockets
import json
import argparse
import requests
import time

# Try to import Picamera2; if it fails, we'll use cv2.VideoCapture(0)
try:
    from picamera2 import Picamera2, Preview
    HAS_PICAMERA = True
    print("✅ Picamera2 module found, will use libcamera backend")
except ImportError:
    HAS_PICAMERA = False
    print("❌ Picamera2 (libcamera) not found, falling back to OpenCV VideoCapture(/dev/video0)")

async def stream_video(game_id, player_id, base_url, display):
    global HAS_PICAMERA
    ws_url = f"{base_url}socket/video?game_id={game_id}&player_id={player_id}"
    http_url = base_url.replace('ws://', 'http://').replace('wss://', 'https://')

    # Initialize camera
    cap = None
    picam2 = None
    if HAS_PICAMERA:
        try:
            picam2 = Picamera2()
            preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
            picam2.configure(preview_config)
            picam2.start()
            print("✅ Picamera2 started")
            time.sleep(2)  # allow sensor to warm up
        except Exception as e:
            print(f"❌ Failed to start Picamera2: {e}")
            print("ℹ️ Will try OpenCV VideoCapture instead")
            HAS_PICAMERA = False

    # connect to websocket
    async with websockets.connect(ws_url) as websocket:
        try:
            while True:
                # grab a frame
                if HAS_PICAMERA and picam2 is not None:
                    try:
                        frame = picam2.capture_array()
                    except Exception as e:
                        print(f"Error capturing from Picamera2: {e}")
                        continue
                else:
                    ret, frame = cap.read()
                    if not ret:
                        print("Error: Failed to capture frame")
                        continue

                # encode as JPEG
                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    print("Error: Failed to encode frame")
                    continue

                # send frame and get detection
                frame_bytes = buffer.tobytes()
                await websocket.send(frame_bytes)
                response = await websocket.recv()
                data = json.loads(response)

                # Check game status and print results
                print("--------------------------------")
                if isinstance(data, dict) and "error" in data:
                    print("Error:", data["error"])
                else:
                    print("Detected cards:", data)
                    # If we detect exactly 2 cards, update the hand
                    if len(data) == 2:
                        # Update the hand with detected cards
                        requests.post(f"{http_url}update_hand?game_id={game_id}&player_id={player_id}&cards={','.join(data)}")

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

                if display:
                    cv2.imshow("Video Stream", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

        except Exception as e:
            print("Exception occurred:", e)
        finally:
            if picam2 is not None:
                picam2.stop()
            if cap is not None:
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
