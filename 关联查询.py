from sqlalchemy import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


# 接口：根据城市ID，查这个城市下的所有景点
@app.get("/cities/{city_id}/scenic-spots")
async def get_scenic_spots_by_city(
        city_id: int,
        db: AsyncSession = Depends(get_db)
):
    # 核心 SQL：JOIN 连表 + 按城市ID筛选
    stmt = (
        select(ScenicSpot)  # 查询景点表
        .join(City)  # 关联城市表（自动按 cities_id 关联）
        .where(City.id == city_id)  # 只查当前城市
    )

    # 执行查询
    result = await db.execute(stmt)

    # 获取该城市下所有景点
    scenic_spots = result.scalars().all()

    return {
        "city_id": city_id,
        "total": len(scenic_spots),
        "data": scenic_spots
    }

#--------------------------------------------------------------------------


from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

# 接口：根据城市ID查询景点 + 分页（默认一页10条）
@app.get("/cities/{city_id}/scenic-spots")
async def get_scenic_spots_by_city(
    city_id: int,
    page: int = 1,          # 页码，默认第1页
    page_size: int = 10,    # 每页条数，默认10条
    db: AsyncSession = Depends(get_db)
):
    # ===================== 1. 先查总条数（分页必须）
    count_stmt = select(func.count()).select_from(ScenicSpot).where(ScenicSpot.cities_id == city_id)
    total = await db.scalar(count_stmt)

    # ===================== 2. 分页查询当前页数据
    stmt = (
        select(ScenicSpot)
        .where(ScenicSpot.cities_id == city_id)  # 直接按外键筛选，最简单
        .offset((page - 1) * page_size)          # 跳过前面的页数
        .limit(page_size)                        # 取当前页10条
    )

    result = await db.execute(stmt)
    scenic_spots = result.scalars().all()

    # ===================== 3. 返回标准分页格式
    return {
        "city_id": city_id,
        "page": page,            # 当前页
        "page_size": page_size,  # 每页条数
        "total": total,          # 总条数
        "total_pages": (total + page_size - 1) // page_size,  # 总页数
        "data": scenic_spots     # 当前页景点列表
    }