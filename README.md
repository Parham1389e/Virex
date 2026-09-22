# Virex

## Railway
Create a Railway PostgreSQL service, set the variables from `.env.example`, and deploy from `main`. The release command runs `alembic upgrade head` before the single Telegram polling worker starts. Do not horizontally scale polling workers.

## Operations
All money changes go through `WalletService.apply`, which locks the wallet with PostgreSQL `SELECT FOR UPDATE`, writes an idempotent ledger entry, and enforces non-negative balance both in code and with a database constraint. Top-ups, purchases, and refunds are idempotent. Config values are unique and assignment is locked with `FOR UPDATE SKIP LOCKED`.

Run locally with Python 3.11+, PostgreSQL, `pip install -r requirements.txt`, `alembic upgrade head`, then `python main.py`. Run tests with `pytest -q`.
