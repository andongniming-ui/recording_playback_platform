import json
import re
from typing import Any, Optional

from pydantic import BaseModel, field_validator
from datetime import datetime


def _split_recording_filter_rules(value: str) -> list[str]:
    text = (value or "").strip()
    if not text:
        return []
    lowered = text.lower()
    if any(marker in lowered for marker in ("re:", "regex:")) or (text.startswith("/") and text.endswith("/")):
        parts = re.split(r"[\n;；]+", text)
    else:
        parts = re.split(r"[\n,，;；]+", text)
    return [part.strip() for part in parts if part.strip()]


class RecordingSessionCreate(BaseModel):
    application_id: int
    name: str
    recording_filter_prefixes: Optional[list[str]] = None

    @field_validator("recording_filter_prefixes", mode="before")
    @classmethod
    def _parse_recording_filter_prefixes(cls, value):
        if value in (None, "", []):
            return None
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except Exception:
                parsed = None
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
            return _split_recording_filter_rules(value) or None
        return None


class RecordingSessionOut(BaseModel):
    id: int
    application_id: int
    name: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_count: int
    error_message: Optional[str]
    recording_filter_prefixes: Optional[list[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("recording_filter_prefixes", mode="before")
    @classmethod
    def _parse_recording_filter_prefixes(cls, value):
        if value in (None, "", []):
            return None
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except Exception:
                parsed = None
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
            return _split_recording_filter_rules(value)
        return None


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
    transaction_code: Optional[str]
    scene_key: Optional[str]
    dedupe_hash: Optional[str]
    governance_status: str
    duplicate_count: Optional[int] = None
    sub_calls: Optional[list["RecordingSubCall"]] = None
    latency_ms: Optional[int]
    tags: Optional[str]
    recorded_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("sub_calls", mode="before")
    @classmethod
    def _parse_sub_calls(cls, value):
        if value in (None, "", []):
            return []
        if isinstance(value, list):
            return [item if isinstance(item, dict) else {"type": "UNKNOWN", "request": item} for item in value]
        if isinstance(value, dict):
            nested = (
                value.get("items")
                or value.get("subCalls")
                or value.get("subCallInfo")
                or value.get("sub_invocations")
                or value.get("subInvocations")
            )
            if isinstance(nested, list):
                return [item if isinstance(item, dict) else {"type": "UNKNOWN", "request": item} for item in nested]
            return [value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except Exception:
                return []
            if isinstance(parsed, dict):
                nested = (
                    parsed.get("items")
                    or parsed.get("subCalls")
                    or parsed.get("subCallInfo")
                    or parsed.get("sub_invocations")
                    or parsed.get("subInvocations")
                )
                if isinstance(nested, list):
                    return [item if isinstance(item, dict) else {"type": "UNKNOWN", "request": item} for item in nested]
                return [parsed]
            if isinstance(parsed, list):
                return [item if isinstance(item, dict) else {"type": "UNKNOWN", "request": item} for item in parsed]
        return []


class RecordingSubCall(BaseModel):
    type: Optional[str] = None
    target: Optional[str] = None
    database: Optional[str] = None
    operation: Optional[str] = None
    table: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    sql: Optional[str] = None
    params: Optional[Any] = None
    request: Any = None
    response: Any = None
    elapsed_ms: Optional[float] = None
    status: Optional[str] = None
    trace_id: Optional[str] = None
    parent_id: Optional[str] = None
    span_id: Optional[str] = None
    thread_name: Optional[str] = None
    error: Optional[str] = None
    children: Optional[list["RecordingSubCall"]] = None

    model_config = {"from_attributes": True}


RecordingOut.model_rebuild()
RecordingSubCall.model_rebuild()


class RecordingGovernanceUpdate(BaseModel):
    transaction_code: Optional[str] = None
    governance_status: Optional[str] = None


class RecordingGroupOut(BaseModel):
    application_id: int
    transaction_code: Optional[str]
    scene_key: Optional[str]
    total_count: int
    approved_count: int
    candidate_count: int
    raw_count: int
    latest_recorded_at: datetime
    representative_recording_id: int
    representative_governance_status: str
    representative_request_method: str
    representative_request_uri: str


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
