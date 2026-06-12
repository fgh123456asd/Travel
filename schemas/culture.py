from pydantic import BaseModel, ConfigDict


class Cultureout(BaseModel):
    id: int
    name: str
    image_url: str | None = None  # ✅ 允许为空
    tag: str
    detail : str
    model_config = ConfigDict(from_attributes=True)

class CultureListOut(BaseModel):
    message: str
    data: list[Cultureout]