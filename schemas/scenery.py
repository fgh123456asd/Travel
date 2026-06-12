from pydantic import BaseModel, ConfigDict


class SceneryOut(BaseModel):
    id: int
    name: str
    tag: str | None = None
    cover_url: str | None = None
    model_config = ConfigDict(from_attributes=True)

class SceneryListOut(BaseModel):
    message: str
    data: list[SceneryOut]



class SceneryDetail(BaseModel):
    id: int
    name: str
    tag: str | None = None
    cover_url: str | None = None
    intro : str | None = None
    level: str | None = None
    address: str | None = None
    opening_time: str | None = None
    ticket_info: str | None = None
    phone: str | None = None
    lat: float | None = None
    lng: float | None = None
    level: str | None = None
    video_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SceneryDetailOut(BaseModel):
    message: str
    data: SceneryDetail


class SceneryData(BaseModel):
    list: list[SceneryDetail]
    total: int

class SceneryOutAll(BaseModel):
    code:int
    message:str
    data:SceneryData



