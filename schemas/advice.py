from pydantic import BaseModel, Field
from typing import List, Optional, Annotated


class AdviceCreate(BaseModel):
    advice: str = Field(..., min_length=1, max_length=500, description="意见内容")
    # 对应 varchar(10)
    name: Annotated[str, Field(None, max_length=10)]
    # 对应 varchar(11)
    phone: Optional[str] = Field(None, max_length=11, description="联系方式")
