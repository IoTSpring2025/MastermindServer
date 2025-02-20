## Mastermind Web Server
This is the source code for the Mastermind web server. This server will handle most of the data processing, including real-time streaming and classification.

The server runs inside of a Docker container, and is deployed using Google Cloud Functions. This exposes a public API that you can stream video to through Web Sockets and make API calls to using HTTP.

The server runs on `mastermindserver-146524160112.us-central1.run.app`

___
### Web Socket for Streaming
Endpoint: `socket/video?game_id={game_id}&player_id={player_id}`

___
### API Endpoints

**Create Game**: `/create`  
*Method:* POST  
*Parameters:*  
- `game_id`: The unique identifier for the game  
- `player_id`: The unique identifier for the player  

**Join Game**: `/join`  
*Method:* POST  
*Parameters:*  
- `game_id`: The unique identifier for the game  
- `player_id`: The unique identifier for the player  

**Get Hand**: `/get_hand`  
*Method:* GET  
*Parameters:*  
- `game_id`: The unique identifier for the game  
- `player_id`: The unique identifier for the player  

**Get Games**: `/get_games`  
*Method:* GET  
*Parameters:*  
- None

**Get Players**: `/get_players`  
*Method:* GET  
*Parameters:*  
- `game_id`: The unique identifier for the game  

___
### Building + Running Locally

**Environment Setup**

To set up your environment, first run:  
`python -m venv venv`  
and  
`source venv/bin/activate`  
and  
`pip install -r requirements.txt`

___
**Running the server**

You can run the server locally by running  
`./local_run.sh`

This will build and run the docker container specified in the Dockerfile.

___
**Streaming to the server**

You can test out the streaming and classification by running  
`python demo.py`  
in a new terminal, which will act as the client. This should enable the camera. To test classification, hold a playing card to the camera. The server will give a response with the predicted card(s).

___
**Running demo with remote server**

To run the demo with the remote server, run:  
`python demo.py --remote`

___
### Cloud Deployment
New cloud deployments happen on any commit to `main`, and are automatically handled by Google Cloud Platform behind the scenes. Note: We might want to set up terraform for this in case we want to strictly set the cloud environment in code.
