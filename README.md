# 100DaysOfCodeBot

A telegram bot for [#100DaysOfCode challenge](https://www.100daysofcode.com/) !

Add this bot to a group

## Features

* [x] Tasks
    * [x] Add/mark complete task
    * [x] Only group members can do this
* [ ] Leaderboard
    * [x] Count points by task completed
    * [ ] Count points by GitHub activity

## Development

* Set bot token as an environment variable in `.env` file :
  ```bash
  TG_BOT_TOKEN=token_here
  ```
* Build docker image named as `hdoc` :
  ```
  docker build -t hdoc .
  ```
* Run in docker :
  ```bash
  docker run -it -v /$(`echo realpath .`):/app --env-file .env hdoc:latest bash
  ```
  The local changes in the folder will be reflected in the container cause it is mounted as a volume at `/app` in container.
* Run bot :
  ```
  python telegram_bot.py
  ```