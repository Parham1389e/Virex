from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import TopUp
from services.wallet import WalletService
class AdminService:
    def __init__(self, session: AsyncSession): self.session=session
    async def pending_topups(self): return (await self.session.execute(select(TopUp).where(TopUp.status=="pending").order_by(TopUp.id).limit(100))).scalars().all()
    async def approve_topup(self, topup_id:int): return await WalletService(self.session).approve_topup(topup_id, f"admin-approve:{topup_id}")
    async def reject_topup(self, topup_id:int, reason:str):
        topup=(await self.session.execute(select(TopUp).where(TopUp.id==topup_id).with_for_update())).scalar_one()
        if topup.status=="pending": topup.status="rejected"; topup.decision_key=f"admin-reject:{topup_id}"; topup.rejection_reason=reason[:500]
        return topup
