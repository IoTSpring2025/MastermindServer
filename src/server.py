from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data import MastermindData

app = FastAPI()
data = MastermindData()

@app.post("/create/{game_id}/{player_id}")
async def create_game(game_id, player_id):
    data.add_game(game_id=game_id)
    data.add_player(game_id=game_id, player_id=player_id)
    return f"Game {game_id} created"

@app.post("/join/{game_id}/{player_id}")
async def join_game(game_id, player_id):
    return data.add_player(game_id=game_id, player_id=player_id)

@app.get("/get_hand/{game_id}/{player_id}")
async def get_hand(game_id, player_id):
    return data.get_hand(game_id=game_id, player_id=player_id)

@app.get("/get_board/{game_id}")
async def get_board(game_id):
    return data.get_board(game_id=game_id)

@app.get("/get_games")
async def get_games():
    return data.get_game_list()

@app.get("/get_players/{game_id}")
async def get_players(game_id):
    return data.get_game_players(game_id=game_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)