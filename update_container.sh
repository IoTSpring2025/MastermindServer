#!/bin/bash -e

docker build -t gcr.io/mastermind-451022/mastermind-server .
docker push gcr.io/mastermind-451022/mastermind-server