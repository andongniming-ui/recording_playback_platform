from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from utils.timezone import current_time_for_update


class TestCase(Base):
    __tablename__ = "test_case"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    application_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("application.id"))
    source_recording_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("recording.id"))
    status: Mapped[str] = mapped_column(String(32), default="draft")
    # 'draft'/'active'/'deprecated'
    governance_status: Mapped[str] = mapped_column(String(32), default="candidate")
    transaction_code: Mapped[str | None] = mapped_column(String(128))
    scene_key: Mapped[str | None] = mapped_column(String(256))
    tags: Mapped[str | None] = mapped_column(String(512))  # comma-separated

    request_method: Mapped[str] = mapped_column(String(16), nullable=False)
    request_uri: Mapped[str] = mapped_column(String(512), nullable=False)
    request_headers: Mapped[str | None] = mapped_column(Text)  # JSON
    request_body: Mapped[str | None] = mapped_column(Text)

    expected_status: Mapped[int | None] = mapped_column(Integer)
    expected_response: Mapped[str | None] = mapped_column(Text)
    assert_rules: Mapped[str | None] = mapped_column(Text)  # JSON: [{path, op, value}]
    ignore_fields: Mapped[str | None] = mapped_column(Text)  # JSON: ["/field/path"]
    perf_threshold_ms: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=current_time_for_update
    )
