# Virex

## Railway deployment
Create a Railway PostgreSQL service and deploy the `main` branch. Set exactly these Variables:

- `BOT_TOKEN`: Telegram bot token
- `ADMIN_IDS`: comma-separated Telegram numeric user IDs. Set the numeric ID of `@Parham88e` here; the username itself is never used for authorization.
- `DATABASE_URL`: Railway PostgreSQL connection URL
- `CARD_NUMBER`: destination card number
- `CARD_OWNER`: card holder name
- `SUPPORT_CONTACT`: support username or contact text
- `RECEIPT_MAX_BYTES`: optional, default 5242880
- `ENVIRONMENT`: `production`
- `LOG_LEVEL`: `INFO`

`@Parham88e` is the intended primary administrator, but the repository does not infer Telegram IDs from usernames. Resolve that account's numeric Telegram User ID and put it in `ADMIN_IDS`, for example:

```text
ADMIN_IDS=123456789
```

Only numeric IDs listed in `ADMIN_IDS` can use administrator callbacks or Wallet approval/rejection actions. Changing a Telegram username does not change authorization, and a username matching `@Parham88e` without its ID in `ADMIN_IDS` has no privileges. Never put a bot token, database password, or populated `.env` file in the repository.

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

Receipt uploads are downloaded through Telegram, size-checked, MIME-checked, persisted by Telegram file ID, and forwarded to every configured admin. Top-up decisions lock the row and are idempotent.
