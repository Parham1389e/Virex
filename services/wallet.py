from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import LedgerEntry, TopUp, Wallet
class WalletError(Exception): pass
class WalletService:
    def __init__(self, session: AsyncSession): self.session = session
    async def apply(self, user_id: int, amount: Decimal, kind: str, key: str, reference: str | None = None):
        if amount == 0: raise WalletError("zero amount is not a transaction")
        existing = await self.session.scalar(select(LedgerEntry).where(LedgerEntry.idempotency_key == key))
        if existing: return existing
        wallet = (await self.session.execute(select(Wallet).where(Wallet.user_id == user_id).with_for_update())).scalar_one()
        new_balance = wallet.balance + amount
        if new_balance < 0: raise WalletError("insufficient balance")
        wallet.balance = new_balance
        entry = LedgerEntry(wallet_id=wallet.id, amount=amount, balance_after=new_balance, kind=kind, idempotency_key=key, reference=reference); self.session.add(entry); await self.session.flush(); return entry
    async def approve_topup(self, topup_id: int, decision_key: str):
        topup = (await self.session.execute(select(TopUp).where(TopUp.id == topup_id).with_for_update())).scalar_one()
        if topup.status != "pending": return topup
        await self.apply(topup.user_id, topup.amount, "topup", f"topup:{topup.id}", str(topup.id)); topup.status = "approved"; topup.decision_key = decision_key; return topup
    async def reject_topup(self, topup_id: int, decision_key: str):
        topup = (await self.session.execute(select(TopUp).where(TopUp.id == topup_id).with_for_update())).scalar_one()
        if topup.status == "pending": topup.status = "rejected"; topup.decision_key = decision_key
        return topup
    async def history(self, user_id: int, limit: int = 20):
        wallet = await self.session.scalar(select(Wallet).where(Wallet.user_id == user_id)); return (await self.session.execute(select(LedgerEntry).where(LedgerEntry.wallet_id == wallet.id).order_by(LedgerEntry.id.desc()).limit(limit))).scalars().all()
