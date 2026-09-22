from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Order, Product, TopUp, User, Wallet
from services.wallet import WalletService

class AdminService:
    def __init__(self, session: AsyncSession): self.session = session
    async def pending_topups(self): return (await self.session.execute(select(TopUp).where(TopUp.status == "pending").order_by(TopUp.id).limit(100))).scalars().all()
    async def approve_topup(self, topup_id: int): return await WalletService(self.session).approve_topup(topup_id, f"admin-approve:{topup_id}")
    async def reject_topup(self, topup_id: int): return await WalletService(self.session).reject_topup(topup_id, f"admin-reject:{topup_id}")
    async def stats(self):
        return {"users": await self.session.scalar(select(func.count(User.id))), "orders": await self.session.scalar(select(func.count(Order.id))), "products": await self.session.scalar(select(func.count(Product.id))), "pending_topups": await self.session.scalar(select(func.count(TopUp.id)).where(TopUp.status == "pending"))}
    async def users_with_balances(self): return (await self.session.execute(select(User, Wallet).join(Wallet, Wallet.user_id == User.id).order_by(User.id.desc()).limit(100))).all()
