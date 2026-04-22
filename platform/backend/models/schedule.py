from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    suite_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("replay_suite.id"))
    cron_expr: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "0 9 * * *"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_type: Mapped[str | None] = mapped_column(String(32))  # 'dingtalk'/'wecom'/'none'
    notify_webhook: Mapped[str | None] = mapped_column(String(512))
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_run_status: Mapped[str | None] = mapped_column(String(32))
    diff_rules: Mapped[str | None] = mapped_column(Text)  # JSON
    assertions: Mapped[str | None] = mapped_column(Text)  # JSON
    perf_threshold_ms: Mapped[int | None] = mapped_column(Integer)
    override_host: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
