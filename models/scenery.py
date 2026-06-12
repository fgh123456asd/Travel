from datetime import datetime
from sqlalchemy import Integer, String, DateTime, DECIMAL, Text,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from . import Base
import settings as config


class Scenery(Base):
    __tablename__ = "scenic_spot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 景点名称
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    tag:Mapped[str] = mapped_column(String(255), nullable=True)
    # 简介
    intro: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 封面图
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 景区等级
    level: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # 地址
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # 开放时间
    opening_time: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 门票信息
    ticket_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 电话
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 纬度
    lat: Mapped[float | None] = mapped_column(DECIMAL(10, 6), nullable=True)

    # 经度
    lng: Mapped[float | None] = mapped_column(DECIMAL(10, 6), nullable=True)

    # 视频
    video: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 所属城市ID
    cities_id: Mapped[int] = mapped_column(Integer, ForeignKey('cities.id'), nullable=False)

    # 创建时间
    create_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    # 更新时间
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )


    @property
    def cover_url(self) -> str | None:
        if self.cover_image:
            return f"{config.IMAGE_BASE_URL}/static/ssc/{self.cover_image}"
        return None

    @property
    def video_url(self) -> str | None:
        if self.video:
            return f"{config.IMAGE_BASE_URL}/static/video/{self.video}"
        return None



class SceneryImage(Base):
    __tablename__ = "scenery_img"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    scenery_id: Mapped[int] = mapped_column(Integer, ForeignKey('scenic_spot.id'), nullable=False)

    @property
    def image_url(self) -> str | None:
        if self.image:
            return f"{config.IMAGE_BASE_URL}/static/ssc/{self.image}"
        return None