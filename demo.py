import asyncio
import cv2
import websockets
import json
import argparse
import requests
import time
from picamera2 import Picamera2


async def stream_video(game_id, player_id, uri, display):
    uri += f"socket/video?game_id={game_id}&player_id={player_id}"

    # Initialize PiCamera2
    try:
        picam2 = Picamera2()
        preview_config = picam2.create_preview_configuration()
        picam2.configure(preview_config)
        picam2.start()
        print("✅ Camera initialized successfully")
        # Give camera time to warm up
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error initializing camera: {e}")
        return

    # connect to web socket
    async with websockets.connect(uri) as websocket:
        try:
            while True:
                try:
                    # Capture frame using PiCamera2
                    frame = picam2.capture_array()
                    # Convert from BGR to RGB if needed
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                except Exception as e:
                    print(f"Error capturing frame: {e}")
                    continue

                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    print("Error: Failed to encode frame")
                    continue

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
            print(f"Exception occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            picam2.stop()
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
        uri = "wss://mastermindserver-146524160112.us-central1.run.app/"
        print("Connecting to remote server")
    else:
        uri = "ws://0.0.0.0:8080/"
        print("Connecting to local server")

    # create dummy game
    requests.post(f"http://0.0.0.0:8080/create?game_id={game_id}&player_id={player_id}")

    # run async
    asyncio.get_event_loop().run_until_complete(
        stream_video(game_id, player_id, uri, args.display)
    )
