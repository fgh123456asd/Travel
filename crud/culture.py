from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.culture import Culture


async def get_culture_db(db: AsyncSession):
    stmt = select(Culture)
    result = await db.execute(stmt)
    return result.scalars().all()
