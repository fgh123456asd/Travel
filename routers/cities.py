from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import cities
from schemas.cities import Cityout, CityListOut

router=APIRouter(prefix= "/cities", tags=["城市"])



@router.get("",response_model=CityListOut)
async def get_cities(db: AsyncSession = Depends(get_db)):
    res=await cities.get_cities_cache(db)
    return {"message": "获取城市列表成功！", "data": res}

