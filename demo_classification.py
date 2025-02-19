import asyncio
import cv2
import websockets
import json
import argparse

async def stream_video(game_id, player_id, uri):
    uri += f"socket/video/{game_id}/{player_id}"

    # connect to web socket
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

                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    print("Error: Failed to encode frame")
                    continue

                frame_bytes = buffer.tobytes()

                await websocket.send(frame_bytes)

                response = await websocket.recv()
                data = json.loads(response)

                if data:
                    print("Detected card:", data)

                cv2.imshow("Video Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print("Exception occurred:", e)
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream video over websockets")
    parser.add_argument("--remote", action="store_true", help="Use remote server")
    args = parser.parse_args()

    game_id = "dummy"
    player_id = "dummy"

    if args.remote:
        uri = "wss://mastermind-server-146524160112.us-central1.run.app"
        print("Connecting to remote server")
    else:
        uri = "ws://0.0.0.0:8080/"
        print("Connecting to local server")

    # run async
    asyncio.get_event_loop().run_until_complete(
        stream_video(game_id, player_id, uri)
    )
