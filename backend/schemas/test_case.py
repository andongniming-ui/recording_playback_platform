from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TestCaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    application_id: Optional[int] = None
    request_method: str
    request_uri: str
    request_headers: Optional[str] = None   # JSON string
    request_body: Optional[str] = None
    expected_status: Optional[int] = None
    expected_response: Optional[str] = None  # JSON string
    assert_rules: Optional[str] = None       # JSON string: [{"path": "$.code", "op": "eq", "value": 0}]
    ignore_fields: Optional[str] = None      # JSON string: ["/timestamp"]
    perf_threshold_ms: Optional[int] = None
    tags: Optional[str] = None               # comma-separated
    status: str = "draft"


class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    application_id: Optional[int] = None
    request_method: Optional[str] = None
    request_uri: Optional[str] = None
    request_headers: Optional[str] = None
    request_body: Optional[str] = None
    expected_status: Optional[int] = None
    expected_response: Optional[str] = None
    assert_rules: Optional[str] = None
    ignore_fields: Optional[str] = None
    perf_threshold_ms: Optional[int] = None
    tags: Optional[str] = None
    status: Optional[str] = None


class TestCaseOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    application_id: Optional[int]
    source_recording_id: Optional[int]
    status: str
    tags: Optional[str]
    request_method: str
    request_uri: str
    request_headers: Optional[str]
    request_body: Optional[str]
    expected_status: Optional[int]
    expected_response: Optional[str]
    assert_rules: Optional[str]
    ignore_fields: Optional[str]
    perf_threshold_ms: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TestCaseFromRecording(BaseModel):
    recording_id: int
    name: Optional[str] = None
    tags: Optional[str] = None
    status: str = "active"


class AddToSuiteRequest(BaseModel):
    suite_id: int
