from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ReplayJob(Base):
    __tablename__ = "replay_job"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(256))
    application_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("application.id"))
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    # PENDING/RUNNING/DONE/FAILED/CANCELLED
    concurrency: Mapped[int] = mapped_column(Integer, default=5)
    timeout_ms: Mapped[int] = mapped_column(Integer, default=5000)

    total: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    errored: Mapped[int] = mapped_column(Integer, default=0)

    use_sub_invocation_mocks: Mapped[bool] = mapped_column(Boolean, default=False)
    diff_rules: Mapped[str | None] = mapped_column(Text)
    assertions: Mapped[str | None] = mapped_column(Text)
    perf_threshold_ms: Mapped[int | None] = mapped_column(Integer)

    webhook_url: Mapped[str | None] = mapped_column(String(512))
    notify_type: Mapped[str | None] = mapped_column(String(32))

    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ReplayResult(Base):
    __tablename__ = "replay_result"
    __table_args__ = (
        UniqueConstraint("job_id", "test_case_id", name="uq_replay_result_job_case"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("replay_job.id"), nullable=False)
    test_case_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("test_case.id"))

    status: Mapped[str] = mapped_column(String(16), nullable=False)
    request_method: Mapped[str | None] = mapped_column(String(16))
    request_uri: Mapped[str | None] = mapped_column(String(512))

    actual_status_code: Mapped[int | None] = mapped_column(Integer)
    actual_response: Mapped[str | None] = mapped_column(Text)
    expected_response: Mapped[str | None] = mapped_column(Text)

    diff_result: Mapped[str | None] = mapped_column(Text)
    assertion_results: Mapped[str | None] = mapped_column(Text)
    is_pass: Mapped[bool] = mapped_column(Boolean, default=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)

    failure_category: Mapped[str | None] = mapped_column(String(64))
    failure_reason: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
