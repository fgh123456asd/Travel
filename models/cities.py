from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from . import Base
import settings as config

class Cities(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    cover_image: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 修复类型
    description: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(100), nullable=True)


    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )


    @property
    def image_url(self) -> str | None:
        if self.cover_image:
            return f"{config.IMAGE_BASE_URL}/static/cover/{self.cover_image}"
        return None