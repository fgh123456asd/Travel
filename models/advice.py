from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from . import Base

class Advice(Base):
    __tablename__ = "advice"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    advice: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str |  None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str |  None] = mapped_column(String(50), nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )