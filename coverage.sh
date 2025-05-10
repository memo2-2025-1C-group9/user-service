#!/bin/bash

sudo docker-compose down


sudo docker-compose up -d db


sudo docker-compose --profile test run --rm test bash -c "coverage run -m pytest tests/ && coverage report -m" 