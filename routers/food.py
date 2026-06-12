from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import food
from schemas.food import FoodListOut

router=APIRouter(prefix= "/food", tags=["美食"])


@router.get("/hot", response_model=FoodListOut)
async def get_hot_food(db: AsyncSession = Depends(get_db)):
    food_hot = await food.get_food_db(db)
    return {"message": "获取美食列表成功！", "data": food_hot}
