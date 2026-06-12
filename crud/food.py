from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.food import Food


async def get_food_db(db: AsyncSession):
    stmt = select(Food)
    result = await db.execute(stmt)
    return result.scalars().all()