#!/bin/bash

# shellcheck disable=SC2164
cd documentdb
docker compose down

cd ../weaviate
docker compose down

cd ../keycloak
docker compose down

# shellcheck disable=SC2103
cd ..
