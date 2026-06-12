from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import culture
from schemas.culture import CultureListOut

router = APIRouter(prefix="/culture", tags=["文化"])



@router.get("", response_model=CultureListOut)
async def get_culture(db: AsyncSession = Depends(get_db)):
    culture_list = await culture.get_culture_db(db)
    return {"message": "获取文化列表成功！", "data": culture_list}
