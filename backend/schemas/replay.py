from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReplayJobCreate(BaseModel):
    name: Optional[str] = None
    application_id: Optional[int] = None
    case_ids: List[int]           # test case IDs to replay
    concurrency: int = 5
    timeout_ms: int = 5000
    use_sub_invocation_mocks: bool = False
    diff_rules: Optional[str] = None       # JSON
    assertions: Optional[str] = None       # JSON
    perf_threshold_ms: Optional[int] = None
    webhook_url: Optional[str] = None
    notify_type: Optional[str] = None
    target_host: Optional[str] = None      # override target host for replay


class ReplayJobOut(BaseModel):
    id: int
    name: Optional[str]
    application_id: Optional[int]
    status: str
    concurrency: int
    timeout_ms: int
    total: int
    passed: int
    failed: int
    errored: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplayResultOut(BaseModel):
    id: int
    job_id: int
    test_case_id: Optional[int]
    status: str
    request_method: Optional[str]
    request_uri: Optional[str]
    actual_status_code: Optional[int]
    actual_response: Optional[str]
    expected_response: Optional[str]
    diff_result: Optional[str]
    assertion_results: Optional[str]
    is_pass: bool
    latency_ms: Optional[int]
    failure_category: Optional[str]
    failure_reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
