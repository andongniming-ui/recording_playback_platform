from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class CiTokenCreate(BaseModel):
    name: str
    scope: str = "trigger"   # 'trigger' / 'read_only'
    expires_days: Optional[int] = None   # None = never expires


class CiTokenOut(BaseModel):
    id: int
    name: str
    scope: str
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    # plain_token only returned on creation
    plain_token: Optional[str] = None

    model_config = {"from_attributes": True}


class CiTriggerRequest(BaseModel):
    suite_id: int
    concurrency: int = 5
    timeout_ms: int = 5000
    notify_type: Optional[str] = None
    notify_webhook: Optional[str] = None

    @field_validator("concurrency")
    @classmethod
    def _validate_concurrency(cls, v):
        if v < 1 or v > 50:
            raise ValueError("concurrency must be between 1 and 50")
        return v

    @field_validator("timeout_ms")
    @classmethod
    def _validate_timeout_ms(cls, v):
        if v < 1:
            raise ValueError("timeout_ms must be >= 1")
        return v


class CiResultResponse(BaseModel):
    job_id: int
    status: str
    total: int
    passed: int
    failed: int
    errored: int
    pass_rate: Optional[float] = None
