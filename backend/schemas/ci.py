from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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


class CiResultResponse(BaseModel):
    job_id: int
    status: str
    total: int
    passed: int
    failed: int
    errored: int
    pass_rate: Optional[float] = None
