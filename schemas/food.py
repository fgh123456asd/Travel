from pydantic import BaseModel, ConfigDict


class FoodOut(BaseModel):
    id: int
    name: str
    introduce: str | None = None
    detailed: str | None = None
    image_url: str | None = None
    model_config = ConfigDict(from_attributes=True)

class FoodListOut(BaseModel):
    message: str
    data: list[FoodOut]