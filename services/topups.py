from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import TopUp

class TopUpService:
    def __init__(self, session: AsyncSession): self.session = session
    async def create(self, user_id: int, amount: Decimal, receipt_file_id: str):
        if amount <= 0 or amount > Decimal("1000000000"): raise ValueError("invalid amount")
        topup = TopUp(user_id=user_id, amount=amount, receipt_file_id=receipt_file_id); self.session.add(topup); await self.session.flush(); return topup
