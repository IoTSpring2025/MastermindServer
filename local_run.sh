#!/bin/bash -e 

docker build . -t mastermind
docker run -e ROBOFLOW_API_KEY=$ROBOFLOW_API_KEY -e ROBOFLOW_PROJECT=$ROBOFLOW_PROJECT -p 8080:8080 mastermind
