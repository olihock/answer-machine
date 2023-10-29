#!/bin/bash

export KEYCLOAK_COMMAND="start-dev --hostname-debug=true --http-relative-path=/keycloak"
docker compose up -d
