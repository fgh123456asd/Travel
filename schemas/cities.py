from pydantic import BaseModel, ConfigDict


class Cityout(BaseModel):
    id: int
    name: str
    image_url: str | None = None  # ✅ 允许为空
    description: str | None = None  # ✅ 允许为空
    tags: str
    model_config = ConfigDict(from_attributes=True)  # 告诉 Pydantic 从数据库模型中获取字段


class CityListOut(BaseModel):
    message: str
    data: list[Cityout]

