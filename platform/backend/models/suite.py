from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Suite(Base):
    __tablename__ = "replay_suite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    suite_type: Mapped[str] = mapped_column(String(32), default="regression")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=datetime.utcnow
    )


class SuiteCase(Base):
    __tablename__ = "replay_suite_case"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    suite_id: Mapped[int] = mapped_column(Integer, ForeignKey("replay_suite.id"), nullable=False)
    test_case_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_case.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
