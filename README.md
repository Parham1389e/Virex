# Virex

## Deploy on Railway
Create a PostgreSQL service, deploy this repository, and configure every variable in `.env.example` in Railway Variables. The start command runs `alembic upgrade head && python main.py`. Run exactly one polling worker; horizontal scaling causes duplicate Telegram updates.

## Guarantees
All balance mutations use `WalletService.apply`, PostgreSQL `SELECT FOR UPDATE`, an idempotency key, `Decimal`, and a database non-negative constraint. Top-up approval/rejection locks the request and ignores already-decided requests. Purchases lock the product and reserve one unassigned config with `FOR UPDATE SKIP LOCKED`; product price is read from the database in the same transaction. Refunds are idempotent through the ledger key.

Run: `pip install -r requirements.txt`, `alembic upgrade head`, `python main.py`. Tests: `pytest -q`.
