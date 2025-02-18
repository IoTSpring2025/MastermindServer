from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from data import MastermindData
import uvicorn 
import paho.mqtt.client as mqtt
import threading 
import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data = MastermindData()

client = mqtt.Client(client_id="webserver-subscriber", callback_api_version=1)

# =======================================================
# Web Server
# =======================================================

# web socket for video stream
@app.websocket("/socket/video/{game_id}/{player_id}")
async def video_stream(web_socket: WebSocket, game_id: str, player_id: str):
    await web_socket.accept()
    try:
        while True:
            video = await web_socket.receive_bytes()
            
            try:
                detected_objects = data.run_inference(video)
            except Exception as e:
                await web_socket.send_json({"error": str(e)})
                continue

            await web_socket.send_json(detected_objects)
            
    except Exception as e:
        print(f"Socket closed: {e}")
    finally:
        pass

# endpoint for game state
@app.post("/create/{game_id}/{player_id}")
async def create_game(game_id: str, player_id: str):
    data.add_game(game_id=game_id)
    data.add_player(game_id=game_id, player_id=player_id)
    return f"Game {game_id} created"

# endpoint to join game
@app.post("/join/{game_id}/{player_id}")
async def join_game(game_id: str, player_id: str):
    return data.add_player(game_id=game_id, player_id=player_id)

# endpoint to get hand
@app.get("/get_hand/{game_id}/{player_id}")
async def get_hand(game_id: str, player_id: str):
    return data.get_hand(game_id=game_id, player_id=player_id)

# endpoint to get games
@app.get("/get_games")
async def get_games():
    return data.get_game_list()

# endpoint to get players
@app.get("/get_players/{game_id}")
async def get_players(game_id: str):
    return data.get_game_players(game_id=game_id)

# endpoint to remove device
@app.get("/remove_device/{device_id}")
async def remove_device(device_id: str):
    data.remove_device(device_id)

# =======================================================
# MQTT Client
# =======================================================

def _on_mqtt_connection_msg(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")

        # payload form: "cam1: 1" or "cam1: 0"
        device, status = payload.split(":")
        device = device.strip()
        status = status.strip()

        print(f"Received payload for device: {device} and status: {status}")

        # encode connection state as true/false
        data.add_device(device, status=="1")
        print(f"Updated device {device}: {data.get_devices[device]}")
    except Exception as e:
        print("Error processing MQTT message:", e)

def start_mqtt_subscriber():
    # docker service name
    mqtt_broker = "mqtt"
    BROKER_PORT = 1883

    client.on_message = _on_mqtt_connection_msg

    while True:
        print("Attempting connection...")
        try:
            client.connect(mqtt_broker, BROKER_PORT, 60)
            break  # Exit loop if connection succeeds
        except Exception as e:
            print(f"MQTT connection failed: {e}. Retrying in 3 seconds...")
            time.sleep(3)

    # subscribe to connection channel
    print("Subscribed to mqtt broker")
    client.subscribe("connected")
    client.loop_forever()

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=start_mqtt_subscriber)
    thread.daemon = True
    thread.start()

# endpoint for connected devices
@app.get("/mqtt/connected")
async def get_connected_devices():
    return data.get_devices()

