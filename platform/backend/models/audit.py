from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class RecordingAuditLog(Base):
    __tablename__ = "recording_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("recording_session.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("application.id"))
    recording_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("recording.id", ondelete="SET NULL"))

    level: Mapped[str] = mapped_column(String(16), default="INFO")
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    record_id: Mapped[str | None] = mapped_column(String(128))
    request_method: Mapped[str | None] = mapped_column(String(16))
    request_uri: Mapped[str | None] = mapped_column(String(512))
    transaction_code: Mapped[str | None] = mapped_column(String(128))
    message: Mapped[str | None] = mapped_column(Text)
    detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ReplayAuditLog(Base):
    __tablename__ = "replay_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("replay_job.id", ondelete="CASCADE"), nullable=False)
    result_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("replay_result.id", ondelete="SET NULL"))
    test_case_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("test_case.id", ondelete="SET NULL"))
    application_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("application.id"))

    level: Mapped[str] = mapped_column(String(16), default="INFO")
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_url: Mapped[str | None] = mapped_column(String(1024))
    request_method: Mapped[str | None] = mapped_column(String(16))
    request_uri: Mapped[str | None] = mapped_column(String(512))
    transaction_code: Mapped[str | None] = mapped_column(String(128))
    actual_status_code: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    message: Mapped[str | None] = mapped_column(Text)
    detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
