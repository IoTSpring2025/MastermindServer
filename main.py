from fastapi import FastAPI, HTTPException, WebSocket, Query
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
@app.websocket("/socket/video")
async def video_stream(web_socket: WebSocket):
    await web_socket.accept()
    game_id = web_socket.query_params.get("game_id")
    player_id = web_socket.query_params.get("player_id")
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

# API endpoint for creating a game
@app.post("/create")
async def create_game(game_id: str, player_id: str):
    data.add_game(game_id=game_id)
    data.add_player(game_id=game_id, player_id=player_id)
    return f"Game {game_id} created"

# API endpoint for joining a game
@app.post("/join")
async def join_game(game_id: str, player_id: str):
    return data.add_player(game_id=game_id, player_id=player_id)

# API endpoint for getting a hand
@app.get("/get_hand")
async def get_hand(game_id: str, player_id: str):
    return data.get_hand(game_id=game_id, player_id=player_id)

# API endpoint to get the list of game
@app.get("/get_games")
async def get_games():
    return data.get_game_list()

# API endpoint for getting players in a game 
@app.get("/get_players")
async def get_players(game_id: str):
    return data.get_game_players(game_id=game_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)