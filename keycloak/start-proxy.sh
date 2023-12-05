#!/bin/bash

export KEYCLOAK_COMMAND="start --proxy edge --hostname=integ.dynv6.net --hostname-debug=true --hostname-strict=true --http-relative-path=/keycloak"
docker compose up -d
