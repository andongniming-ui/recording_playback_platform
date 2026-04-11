from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TestCaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    application_id: Optional[int] = None
    governance_status: str = "candidate"
    transaction_code: Optional[str] = None
    scene_key: Optional[str] = None
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
    governance_status: Optional[str] = None
    transaction_code: Optional[str] = None
    scene_key: Optional[str] = None
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
    governance_status: str
    transaction_code: Optional[str]
    scene_key: Optional[str]
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
    governance_status: Optional[str] = None


class AddToSuiteRequest(BaseModel):
    suite_id: int


class BatchCheckRequest(BaseModel):
    recording_ids: list[int]


class BatchCheckItem(BaseModel):
    recording_id: int
    transaction_code: Optional[str]
    has_existing: bool
    existing_case_id: Optional[int] = None
    existing_case_name: Optional[str] = None


class BatchFromRecordingsRequest(BaseModel):
    recording_ids: list[int]
    prefix: str


class BatchResultItem(BaseModel):
    recording_id: int
    status: str  # "created" | "failed"
    test_case_id: Optional[int] = None
    name: Optional[str] = None
    error: Optional[str] = None


class BatchFromRecordingsResponse(BaseModel):
    total: int
    created: int
    failed: int
    results: list[BatchResultItem]
