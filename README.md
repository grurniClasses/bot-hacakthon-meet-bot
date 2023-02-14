# 🚧 MEET BOT

## The Team

- Marina Lobanov
- Neta Kleman
- Hagar Laks

## About this bot

With this bot you can easily schedule event with multiple guesses.

https://t.me/BotMeetBot

Start a new meeting-
<br>
<img src="https://user-images.githubusercontent.com/59369034/218679042-340575c2-006d-4fb0-9fa3-23377b684009.png"  width=300>
<br>
inviter selected dates-
<br>
<img src="https://user-images.githubusercontent.com/59369034/218679538-8650ceb1-d956-410b-a5bb-281021b39516.png" width=300>
<br>
Inviter submitted-
<br>
<img src="https://user-images.githubusercontent.com/59369034/218679791-1aa3fb55-1980-4c21-b36e-98e59caf6d24.png"  width=300>
<br>
Guess enter the link and press start-
<br>
<img src="https://user-images.githubusercontent.com/59369034/218679921-22093eeb-919f-4529-a8fd-b8c393b7a037.png"  width=300>
<br>
Guess selected the dates he can-
<br>
<img src="https://user-images.githubusercontent.com/59369034/218680028-0f9a94d4-e2ad-4eac-8936-489b5b45ed50.png"  width=300>
<br>
Guess submitted-
<br>
<img src="https://user-images.githubusercontent.com/59369034/218680982-db95c8b9-f059-4416-96c0-e8a6a29f0fd1.png"  width=300>
<br>
Guess\Inviter send /status-
<br>
<img src="https://user-images.githubusercontent.com/59369034/218680147-f02a2fdc-a3c1-4791-8081-9df50421e22a.png"  width=300>

## Instructions for Developers

### Prerequisites

- Python 3.10
- Poetry
- python-telegram-bot 13.15
- requests 2.28.2
- pymongo 4.3.3

### Setup

- git clone this repository
- cd into the project directory
- Install dependencies:

      poetry install


- Get an API Token for a bot via the [BotFather](https://telegram.me/BotFather)
- Create a `bot_settings.py` file with your bot token:

      BOT_TOKEN = 'xxxxxxx'
      BOT_NAME = 'xxxxxxx'

### Running the bot

- Run the bot:

      poetry run python bot.py
