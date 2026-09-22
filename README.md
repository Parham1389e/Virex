# Virex

## Railway deployment
Create a Railway PostgreSQL service and deploy the `main` branch. Set exactly these Variables:

- `BOT_TOKEN`: Telegram bot token
- `ADMIN_IDS`: comma-separated Telegram numeric IDs
- `DATABASE_URL`: Railway PostgreSQL connection URL
- `CARD_NUMBER`: destination card number
- `CARD_OWNER`: card holder name
- `SUPPORT_CONTACT`: support username or contact text
- `RECEIPT_MAX_BYTES`: optional, default 5242880
- `ENVIRONMENT`: `production`
- `LOG_LEVEL`: `INFO`

Railway runs `alembic upgrade head && python main.py`. Run one polling worker only; do not horizontally scale it. Never commit `.env` or secrets.

## Local commands
```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python main.py
pytest -q
```

Receipt uploads are downloaded through Telegram, size-checked, MIME-checked, persisted by Telegram file ID, and forwarded to every configured admin. Top-up decisions lock the row and are idempotent. Purchases lock wallet/product/config rows and refund the transaction on failure. Telegram delivery is only marked after send succeeds.
