from aiosmtplib import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from models.advice import Advice
from schemas.advice import AdviceCreate

router=APIRouter()


@router.post("/advice")
async def create_advice(data:AdviceCreate,db: AsyncSession = Depends(get_db)):
    try:
        # 将 Pydantic 模型转换为 SQLAlchemy 模型实
        # 例
        db_advice = Advice(
            advice=data.advice,
            name=data.name,
            phone=data.phone
            # create_time 会自动使用数据库/ORM定义的默认当前时间
        )

        # 写入数据库
        db.add(db_advice)
        db.commit()
        db.refresh(db_advice)

        return {
            "code": 200,
            "message": "意见提交成功，感谢您的反馈！",
            "data": {
                "id": db_advice.id
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误，保存失败: {str(e)}"
        )
