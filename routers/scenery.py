from fastapi import Query

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import scenery
from schemas.scenery import SceneryListOut, SceneryDetailOut, SceneryOutAll

router=APIRouter(prefix= "/scenery", tags=["景点"])


@router.get("/list",response_model=SceneryOutAll)
async def get_scenery_list_all(
        name: str = Query(""),
        page: int = 1,
        page_size: int = Query(8, alias='pageSize', le=100),
        db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * page_size
    scenery_list=await scenery.get_scenery_list_db(db,name,offset,page_size)
    total=await scenery.get_scenery_count(db,name)
    return {
        'code': 200,
        'message': '景点列表获取成功',
        'data': {
            'list': scenery_list,
            'total': total,
        }
    }



@router.get("", response_model=SceneryListOut)
async def get_scenery_list(db: AsyncSession = Depends(get_db)):
    res=await scenery.get_scenery(db)
    return {"message": "获取景点列表成功！", "data": res}



@router.get("/{id}", response_model=SceneryDetailOut)
async def get_scenery_detail(id: int, db: AsyncSession = Depends(get_db)):
    res=await scenery.get_scenery_by_id(id, db)
    return {"message": "获取景点详情成功！", "data": res}



#景点详情页风格图片
@router.get("/images/{id}")
async def get_scenery_images_by_id(id: int, db: AsyncSession = Depends(get_db)):
    res=await scenery.get_scenery_images(db, id)
    if not res:
        raise HTTPException(status_code=404, detail="该景点暂无图片")
    url=[ i.image_url for i in res]
    return {"message": "获取景点图片成功！", "data":url}


#景点列表页

