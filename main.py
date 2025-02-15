from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from data import MastermindData
import uvicorn 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


data = MastermindData()

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

# api for game state
@app.post("/create/{game_id}/{player_id}")
async def create_game(game_id: str, player_id: str):
    data.add_game(game_id=game_id)
    data.add_player(game_id=game_id, player_id=player_id)
    return f"Game {game_id} created"

@app.post("/join/{game_id}/{player_id}")
async def join_game(game_id: str, player_id: str):
    return data.add_player(game_id=game_id, player_id=player_id)

@app.get("/get_hand/{game_id}/{player_id}")
async def get_hand(game_id: str, player_id: str):
    return data.get_hand(game_id=game_id, player_id=player_id)

@app.get("/get_games")
async def get_games():
    return data.get_game_list()

@app.get("/get_players/{game_id}")
async def get_players(game_id: str):
    return data.get_game_players(game_id=game_id)
