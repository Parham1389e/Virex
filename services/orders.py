from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Config, Order, Product
from services.wallet import WalletService

class OrderService:
    def __init__(self, session: AsyncSession): self.session = session
    async def purchase(self, user_id: int, product_id: int, key: str):
        old = await self.session.scalar(select(Order).where(Order.payment_key == key))
        if old: return old
        product = (await self.session.execute(select(Product).where(Product.id == product_id).with_for_update())).scalar_one()
        if not product.available: raise ValueError("product unavailable")
        config = (await self.session.execute(select(Config).where(Config.product_id == product_id, Config.assigned.is_(False)).with_for_update(skip_locked=True))).scalars().first()
        if not config: raise ValueError("no config available")
        await WalletService(self.session).apply(user_id, -Decimal(product.price), "purchase", key, str(product_id))
        config.assigned = True
        order = Order(user_id=user_id, product_id=product_id, amount=product.price, status="paid", payment_key=key, config_id=config.id)
        self.session.add(order); await self.session.flush(); return order
    async def refund(self, order_id: int, key: str):
        order = (await self.session.execute(select(Order).where(Order.id == order_id).with_for_update())).scalar_one()
        if order.status == "refunded": return order
        if order.status != "paid": raise ValueError("order is not refundable")
        await WalletService(self.session).apply(order.user_id, Decimal(order.amount), "refund", key, str(order.id))
        order.status = "refunded"; return order
