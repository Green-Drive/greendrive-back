#!/bin/bash

docker compose -f docker-compose.yml up --build
docker compose -f docker-compose.yml down -v
