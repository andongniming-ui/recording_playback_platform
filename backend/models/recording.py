from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class RecordingSession(Base):
    __tablename__ = "recording_session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("application.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="idle")
    # 'idle'/'active'/'collecting'/'done'/'error'
    start_time: Mapped[datetime | None] = mapped_column(DateTime)
    end_time: Mapped[datetime | None] = mapped_column(DateTime)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(512))
    recording_filter_prefixes: Mapped[str | None] = mapped_column(Text)  # JSON list of tx_code prefixes
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Recording(Base):
    __tablename__ = "recording"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("recording_session.id", ondelete="CASCADE"))
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("application.id"), nullable=False)

    record_id: Mapped[str | None] = mapped_column(String(128), unique=True)  # AREX original record_id
    request_method: Mapped[str] = mapped_column(String(16), nullable=False)
    request_uri: Mapped[str] = mapped_column(String(512), nullable=False)
    request_headers: Mapped[str | None] = mapped_column(Text)  # JSON
    request_body: Mapped[str | None] = mapped_column(Text)

    response_status: Mapped[int | None] = mapped_column(Integer)
    response_headers: Mapped[str | None] = mapped_column(Text)  # JSON
    response_body: Mapped[str | None] = mapped_column(Text)

    transaction_code: Mapped[str | None] = mapped_column(String(128))
    scene_key: Mapped[str | None] = mapped_column(String(256))
    dedupe_hash: Mapped[str | None] = mapped_column(String(64))
    governance_status: Mapped[str] = mapped_column(String(32), default="raw")
    sub_calls: Mapped[str | None] = mapped_column(Text)  # JSON: [{type, request, response}]
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    tags: Mapped[str | None] = mapped_column(String(512))  # comma-separated
    recorded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
