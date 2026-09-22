# Virex

Production-oriented Telegram shop with an async PostgreSQL wallet ledger, top-up moderation, products, orders, configs, refunds, and Railway deployment support.

## Setup
```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python main.py
```

Set all values in `.env`; never commit secrets. Use one Railway polling worker only. See `.env.example` and `railway.toml` for deployment configuration.

Financial mutations are centralized in `WalletService`, use `Decimal`, idempotency keys, and PostgreSQL row locks. Prices are copied into orders at payment time from the database product row.
