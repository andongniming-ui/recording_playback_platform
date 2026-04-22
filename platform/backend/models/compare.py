from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class CompareRule(Base):
    __tablename__ = "compare_rule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    scope: Mapped[str] = mapped_column(String(16), default="global")  # 'global'/'app'
    application_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("application.id"))
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False)  # 'ignore'/'assert'
    config: Mapped[str] = mapped_column(Text, nullable=False)  # JSON rule config
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
