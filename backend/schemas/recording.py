from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RecordingSessionCreate(BaseModel):
    application_id: int
    name: str


class RecordingSessionOut(BaseModel):
    id: int
    application_id: int
    name: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_count: int
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordingOut(BaseModel):
    id: int
    session_id: Optional[int]
    application_id: int
    record_id: Optional[str]
    request_method: str
    request_uri: str
    request_headers: Optional[str]
    request_body: Optional[str]
    response_status: Optional[int]
    response_body: Optional[str]
    sub_calls: Optional[str]
    latency_ms: Optional[int]
    tags: Optional[str]
    recorded_at: datetime

    model_config = {"from_attributes": True}


class SyncRequest(BaseModel):
    """Request body for manual sync from arex-storage."""
    begin_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page_size: int = 50
    page_index: int = 0


class FilterRuleUpdate(BaseModel):
    """Update recording filter rules (stored in application)."""
    sample_rate: Optional[float] = None
    desensitize_rules: Optional[str] = None  # JSON
