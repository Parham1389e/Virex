from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Config, Product

class CatalogService:
    def __init__(self, session: AsyncSession): self.session = session
    async def create_product(self, name: str, volume: str, duration: str, price: Decimal, available=True):
        if not name.strip() or price <= 0: raise ValueError("invalid product")
        item = Product(name=name.strip(), volume=volume.strip(), duration=duration.strip(), price=price, available=available); self.session.add(item); await self.session.flush(); return item
    async def update_product(self, product_id: int, **changes):
        item = (await self.session.execute(select(Product).where(Product.id == product_id).with_for_update())).scalar_one()
        if "price" in changes and changes["price"] <= 0: raise ValueError("invalid price")
        for key in ("name", "volume", "duration", "price", "available"):
            if key in changes: setattr(item, key, changes[key])
        return item
    async def delete_product(self, product_id: int):
        item = (await self.session.execute(select(Product).where(Product.id == product_id).with_for_update())).scalar_one(); await self.session.delete(item)
    async def add_config(self, product_id: int, value: str):
        if not value.strip(): raise ValueError("empty config")
        item = Config(product_id=product_id, value=value.strip()); self.session.add(item); await self.session.flush(); return item
    async def delete_config(self, config_id: int):
        item = (await self.session.execute(select(Config).where(Config.id == config_id, Config.assigned.is_(False)).with_for_update())).scalar_one(); await self.session.delete(item)
