#!/bin/bash

export KEYCLOAK_COMMAND="start-dev --hostname-debug=true --http-relative-path=/keycloak"
#export KEYCLOAK_COMMAND="start --proxy edge --hostname=localhost --hostname-debug=true --hostname-strict=true --http-relative-path=/keycloak"
docker compose up -d
