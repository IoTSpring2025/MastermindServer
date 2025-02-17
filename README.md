## Mastermind Web Server
This is the source code for the Mastermind web server. This server will handle most of the data processing, including real-time streaming and classification. 

The server runs inside of a Docker container, and is deployed using Google Cloud Functions. This exposes a public API that you can stream video to through Web Sockets and make API calls to using HTTP.

### Building + Running Locally

<b>Environment Setup</b>

To set up your environment, first run:
`python -m venv venv`
and 
`source venv/bin/activate`
and 
`pip install -r requirements.txt`

If you are running locally, you will need to set the following environment variables:

1. ROBOFLOW_API_KEY: `export ROBOFLOW_API_KEY=<your_api_key_here>`
2. ROBOFLOW_PROJECT: `export ROBOFLOW_PROJECT=<your_api_key_here>`

You can find these on your Roboflow Account. Reach out to @jkrue242 if you don't have an account.

<b>Running the server</b>

You can run the server locally by running 
`./local_run.sh`

This will build and run the docker container specified in the Dockerfile.

<b>Streaming to the server</b>

You can test out the streaming and classification by running 
`python demo.py` 
in a new terminal, which will act as the client. This should enable the camera. To test classification, hold a playing card to the camera. The server will give a response with the predicted card(s).

### Cloud Deployment
New cloud deployments happen on any commit to `main`, and are automatically handled by Google Cloud Platform behind the scenes. Note: We might want to set up terraform for this in case we want to strictly set the cloud environment in code. 
