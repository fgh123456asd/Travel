from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
import settings as config
from models import Base


class Food(Base):
    __tablename__ = "food"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    introduce: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detailed:Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(String(100), nullable=True)

    citie_id: Mapped[int] = mapped_column(Integer, ForeignKey('cities.id'), nullable=False)

    # 创建时间
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
            return f"{config.IMAGE_BASE_URL}/static/food/{self.image}"
        return None
