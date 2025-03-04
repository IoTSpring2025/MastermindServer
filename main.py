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
async def video_stream(web_socket: WebSocket, game_id: str, player_id: str):
    await web_socket.accept()

    # TODO: update db with this stuff
    try:
        while True:
            # receive video frame from client
            frame = await web_socket.receive_bytes()

            try:
                detected_objects = data.run_inference(frame, game_id, player_id)
                await web_socket.send_json(detected_objects)
            except Exception as e:
                await web_socket.send_json({"error": str(e)})
                continue

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
    hand: set[str] = data.get_hand(game_id=game_id, player_id=player_id)
    if hand:
        return list(hand)
    else:
        return {"message": "No hand detected."}


# API endpoint for getting the flop
@app.get("/get_flop")
async def get_flop(game_id: str):
    flop: set[str] = data.get_flop(game_id=game_id)
    if flop:
        return list(flop)
    else:
        return {"message": "No flop detected."}


# API endpoint for getting the turn
@app.get("/get_turn")
async def get_turn(game_id: str):
    turn = data.get_turn(game_id=game_id)
    if turn:
        return turn
    else:
        return {"message": "No turn detected."}


# API endpoint for getting the river
@app.get("/get_river")
async def get_river(game_id: str):
    river = data.get_river(game_id=game_id)
    if river:
        return river
    else:
        return {"message": "No river detected."}


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
