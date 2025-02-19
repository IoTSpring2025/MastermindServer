#!/bin/bash -e

docker build . -f Dockerfile.mqtt -t mastermind_mqtt
docker run -p 1883:1883 mastermind_mqtt