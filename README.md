# codex

Skeleton project for Telegram store bot.

## Bot Setup

1. Install dependencies:
   ```bash
   pip install python-telegram-bot
   ```
2. Set the environment variable `TELEGRAM_TOKEN` with your bot token.
3. Run the bot:
   ```bash
   python bot/main.py
   ```
4. Orders will be stored in `bot/orders.json`.

## Web App

1. Install dependencies:
   ```bash
   pip install flask
   ```
2. Optionally set the environment variable `BOT_USERNAME` with your bot's username for order links.
3. Run the web server:
   ```bash
   python web/app.py
   ```
