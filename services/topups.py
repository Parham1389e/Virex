from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import TopUp
from config.settings import settings

class TopUpService:
    def __init__(self, session: AsyncSession): self.session = session
    async def create(self, user_id: int, amount: Decimal, receipt_file_id: str, mime_type: str, size: int):
        if amount <= 0 or amount > Decimal("1000000000"): raise ValueError("invalid amount")
        if mime_type not in settings.receipt_mime_types: raise ValueError("unsupported receipt type")
        if not receipt_file_id or len(receipt_file_id) > 256 or size <= 0 or size > settings.receipt_max_bytes: raise ValueError("invalid receipt")
        item = TopUp(user_id=user_id, amount=amount, receipt_file_id=receipt_file_id, receipt_mime_type=mime_type, receipt_size=size)
        self.session.add(item); await self.session.flush(); return item
