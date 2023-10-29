#!/bin/bash

# shellcheck disable=SC2164
cd documentdb
./run.sh

cd ../weaviate
./run.sh

cd ../keycloak
./start-dev.sh

# shellcheck disable=SC2103
cd ..
