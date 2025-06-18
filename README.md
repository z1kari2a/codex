# codex

Skeleton project for Telegram store bot.

## Bot Setup

1. Install dependencies:
   ```bash
   pip install python-telegram-bot
   ```
2. Set the environment variable `TELEGRAM_TOKEN` with your bot token.
3. (Optional) set `ADMIN_ID` with your Telegram numeric ID to receive order notifications and access the `/admin` command.
4. Run the bot:
   ```bash
   python bot/main.py
   ```
5. Orders will be stored in `bot/orders.json`.
6. As admin you can add products via `/admin` → "إضافة منتج".

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
