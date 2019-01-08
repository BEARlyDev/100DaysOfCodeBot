#!/usr/bin/env bash

# Set env vars
# https://stackoverflow.com/a/20909045/1372424
export $(grep -v '^#' .env | xargs -d '\n')

python3 telegram_bot.py 
