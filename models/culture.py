from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from . import Base
import settings as config

class Culture(Base):
    __tablename__ = "culture"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    tag: Mapped[str] = mapped_column(String(255), nullable=True)
    image: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detail:Mapped[str | None] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    # 更新时间
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    @property
    def image_url(self) -> str | None:
        if self.image:
            return f"{config.IMAGE_BASE_URL}/static/culture/{self.image}"
        return None
