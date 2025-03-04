## Mastermind Web Server
This is the source code for the Mastermind web server. This server handles real-time poker hand detection, including player hands and community cards (flop, turn, and river) through video streaming and classification.

The server runs inside of a Docker container and is deployed using Google Cloud Functions. This exposes a public API that you can stream video to through Web Sockets and make API calls to using HTTP.

The server runs on `mastermindserver-146524160112.us-central1.run.app`

___
### Web Socket for Streaming
Endpoint: `socket/video?game_id={game_id}&player_id={player_id}`

The websocket stream will return detection results in the following format:
```json
{
    "detected_cards": ["card1", "card2", ...],
}
```

___
### API Endpoints

**Create Game**: `/create`  
*Method:* POST  
*Parameters:*  
- `game_id`: The unique identifier for the game  
- `player_id`: The unique identifier for the player  
*Returns:* Confirmation message

**Join Game**: `/join`  
*Method:* POST  
*Parameters:*  
- `game_id`: The unique identifier for the game  
- `player_id`: The unique identifier for the player  
*Returns:* Confirmation message

**Get Hand**: `/get_hand`  
*Method:* GET  
*Parameters:*  
- `game_id`: The unique identifier for the game  
- `player_id`: The unique identifier for the player  
*Returns:* List of cards or message if no hand detected

**Get Flop**: `/get_flop`  
*Method:* GET  
*Parameters:*  
- `game_id`: The unique identifier for the game  
*Returns:* List of three cards or message if no flop detected

**Get Turn**: `/get_turn`  
*Method:* GET  
*Parameters:*  
- `game_id`: The unique identifier for the game  
*Returns:* Single card or message if no turn detected

**Get River**: `/get_river`  
*Method:* GET  
*Parameters:*  
- `game_id`: The unique identifier for the game  
*Returns:* Single card or message if no river detected

**Get Games**: `/get_games`  
*Method:* GET  
*Parameters:* None  
*Returns:* List of active game IDs

**Get Players**: `/get_players`  
*Method:* GET  
*Parameters:*  
- `game_id`: The unique identifier for the game  
*Returns:* List of players in the specified game

___
### Building + Running Locally

**Environment Setup**

To set up your environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

___
**Running the server**

Run the server locally with:  
`./local_run.sh`

This will build and run the docker container specified in the Dockerfile.

___
**Testing with Demo Client**

Run the demo client with:
```bash
# Local server with display
python demo.py --display

# Local server without display
python demo.py

# Remote server with display
python demo.py --remote --display

# Remote server without display
python demo.py --remote
```

The demo client will:
1. Connect to the specified server
2. Stream video from your camera
3. Display detection results in real-time
4. Optionally show the camera feed with `--display`

___
### Game State Flow
1. Player Hand Detection: First 2 cards detected for each player
2. Flop Detection: Next 3 community cards
3. Turn Detection: Fourth community card
4. River Detection: Final community card

The server maintains this state for each game and updates it based on the cards detected in the video stream.

___
### Cloud Deployment
New cloud deployments happen on any commit to `main`, and are automatically handled by Google Cloud Platform behind the scenes.
