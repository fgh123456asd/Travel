from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.cities import Cities
#async with db.begin() 是开启事务用的，只给增、删、改使用

async def get_cities_cache(db: AsyncSession):
        stmt = select(Cities)
        result=await db.execute(stmt)
        return result.scalars().all()



