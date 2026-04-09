from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Application(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # SSH connectivity
    ssh_host: Mapped[str] = mapped_column(String(256), nullable=False)
    ssh_user: Mapped[str] = mapped_column(String(64), nullable=False)
    ssh_key_path: Mapped[str | None] = mapped_column(String(512))
    ssh_password: Mapped[str | None] = mapped_column(String(256))
    ssh_port: Mapped[int] = mapped_column(Integer, default=22)

    service_port: Mapped[int] = mapped_column(Integer, default=8080)
    jvm_process_name: Mapped[str | None] = mapped_column(String(256))  # used to identify process

    agent_status: Mapped[str] = mapped_column(String(32), default="unknown")
    # 'unknown'/'online'/'offline'/'mounting'

    arex_storage_url: Mapped[str | None] = mapped_column(String(512))  # override global config
    arex_app_id: Mapped[str | None] = mapped_column(String(128))  # AREX application identifier

    sample_rate: Mapped[float] = mapped_column(Float, default=1.0)  # recording sample rate
    desensitize_rules: Mapped[str | None] = mapped_column(Text)  # JSON desensitize rules
    default_ignore_fields: Mapped[str | None] = mapped_column(Text)  # JSON default ignore field list
    default_assertions: Mapped[str | None] = mapped_column(Text)  # JSON default assertion rules
    default_perf_threshold_ms: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=datetime.utcnow
    )
