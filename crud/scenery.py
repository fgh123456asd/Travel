from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.cities import Cities
from models.scenery import Scenery, SceneryImage


async def get_scenery(db: AsyncSession):
    stmt=select(Scenery).order_by(Scenery.id.asc())
    result= await db.execute(stmt)
    return result.scalars().all()

#景点详情页
async def get_scenery_by_id(id:int,db:AsyncSession):
    stmt=select(Scenery).where(Scenery.id==id)
    result= await db.execute(stmt)
    return result.scalars().first()



async def get_scenery_images(db: AsyncSession, scenery_id: int):
    stmt = select(SceneryImage).where(SceneryImage.scenery_id == scenery_id)
    result = await db.execute(stmt)
    return result.scalars().all()




#查询景点总条数
async def get_scenery_count(db: AsyncSession,name:str):
    # 1. 先根据城市名找到城市
    if name:
        result = await db.execute(select(Cities).filter(Cities.name == name))
        city = result.scalar_one_or_none()
        #城市不存在，返回 0 条
        if not city:
            return 0
        # 2. 直接查询该城市下的景点总数
        stmt = select(func.count(Scenery.id)).where(Scenery.cities_id==city.id)
    else:
        # 3. 不传城市名 → 统计所有景点
        stmt = select(func.count(Scenery.id))
        # 执行查询
    count_result = await db.execute(stmt)
    total = count_result.scalar_one()
    return total


#景点列表页
async def get_scenery_list_db(db: AsyncSession,
                              name:str,
                              skip:int=0,
                              limit:int=8):
    if name:
        result = await db.execute(select(Cities).filter(Cities.name == name))
        city = result.scalar_one_or_none()
        if not city:
            return []
        stmt = select(Scenery).where(Scenery.cities_id == city.id)
    else:
        stmt = select(Scenery)
    stmt = stmt.offset(skip).limit(limit)
    # 4. 执行
    result = await db.execute(stmt)
    return result.scalars().all()
