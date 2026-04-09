from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ScheduleCreate(BaseModel):
    name: str
    suite_id: Optional[int] = None
    cron_expr: str
    is_active: bool = True
    notify_type: Optional[str] = None    # 'dingtalk'/'wecom'/'none'
    notify_webhook: Optional[str] = None
    diff_rules: Optional[str] = None
    assertions: Optional[str] = None
    perf_threshold_ms: Optional[int] = None
    override_host: Optional[str] = None

    @field_validator("notify_type")
    @classmethod
    def validate_notify_type(cls, v):
        if v is not None and v not in ("dingtalk", "wecom", "none", ""):
            raise ValueError("notify_type must be dingtalk, wecom, none, or empty")
        return v


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    suite_id: Optional[int] = None
    cron_expr: Optional[str] = None
    is_active: Optional[bool] = None
    notify_type: Optional[str] = None
    notify_webhook: Optional[str] = None
    diff_rules: Optional[str] = None
    assertions: Optional[str] = None
    perf_threshold_ms: Optional[int] = None
    override_host: Optional[str] = None


class ScheduleOut(BaseModel):
    id: int
    name: str
    suite_id: Optional[int]
    cron_expr: str
    is_active: bool
    notify_type: Optional[str]
    notify_webhook: Optional[str]
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
