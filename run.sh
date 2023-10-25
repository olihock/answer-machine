#!/bin/bash

./documentdb/run.sh
./weaviate/run.sh
./keycloak/run.sh

docker compose build
docker compose up -d
