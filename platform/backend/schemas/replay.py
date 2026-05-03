import json
from pydantic import BaseModel, field_validator
from typing import Optional, List, Literal, Any
from datetime import datetime


class HeaderTransform(BaseModel):
    type: Literal["replace", "remove", "add"] = "replace"
    key: str
    value: Optional[str] = None


class DiffRule(BaseModel):
    type: str
    path: Optional[str] = None
    tolerance: Optional[float] = None
    pattern: Optional[str] = None
    key: Optional[str] = None
    field: Optional[str] = None


class AssertionRule(BaseModel):
    type: str
    path: Optional[str] = None
    value: Optional[Any] = None
    pattern: Optional[str] = None


class ReplayJobCreate(BaseModel):
    name: Optional[str] = None
    application_id: Optional[int] = None
    case_ids: List[int]           # test case IDs to replay
    concurrency: int = 5           # constrained: 1..50
    timeout_ms: int = 5000         # constrained: >= 1
    delay_ms: int = 0
    ignore_fields: Optional[List[str]] = None

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

    @field_validator("delay_ms")
    @classmethod
    def _validate_delay_ms(cls, v):
        if v < 0:
            raise ValueError("delay_ms must be >= 0")
        return v

    use_sub_invocation_mocks: bool = False
    fail_on_sub_call_diff: bool = False
    diff_rules: Optional[List[DiffRule]] = None
    assertions: Optional[List[AssertionRule]] = None
    perf_threshold_ms: Optional[int] = None
    webhook_url: Optional[str] = None
    notify_type: Optional[str] = None
    target_host: Optional[str] = None      # override target host for replay
    smart_noise_reduction: bool = False    # 启用内置智能降噪规则
    ignore_order: bool = True              # JSON 数组是否忽略顺序
    retry_count: int = 0                   # 失败重试次数（0 = 不重试）
    repeat_count: int = 1                  # 每条录制重复回放次数（流量放大）
    header_transforms: Optional[List[HeaderTransform]] = None

    @field_validator("retry_count")
    @classmethod
    def _validate_retry_count(cls, v):
        if v < 0 or v > 5:
            raise ValueError("retry_count must be between 0 and 5")
        return v

    @field_validator("repeat_count")
    @classmethod
    def _validate_repeat_count(cls, v):
        if v < 1 or v > 100:
            raise ValueError("repeat_count must be between 1 and 100")
        return v


class ReplayJobOut(BaseModel):
    id: int
    name: Optional[str]
    application_id: Optional[int]
    status: str
    concurrency: int
    timeout_ms: int
    delay_ms: int = 0
    total: int
    passed: int
    failed: int
    errored: int
    ignore_fields: Optional[List[str]] = None
    diff_rules: Optional[List[DiffRule]] = None
    assertions: Optional[List[AssertionRule]] = None
    header_transforms: Optional[List[HeaderTransform]] = None
    use_sub_invocation_mocks: bool = False
    fail_on_sub_call_diff: bool = False
    perf_threshold_ms: Optional[int] = None
    smart_noise_reduction: bool = False
    ignore_order: bool = True
    retry_count: int = 0
    repeat_count: int = 1
    target_host: Optional[str] = None
    webhook_url: Optional[str] = None
    notify_type: Optional[str] = None
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("ignore_fields", mode="before")
    @classmethod
    def _parse_ignore_fields(cls, value):
        if value in (None, ""):
            return None
        if isinstance(value, list):
            return value
        try:
            parsed = json.loads(value)
        except Exception:
            return None
        return parsed if isinstance(parsed, list) else None

    @field_validator("diff_rules", "assertions", "header_transforms", mode="before")
    @classmethod
    def _parse_json_list(cls, value):
        if value in (None, ""):
            return None
        if isinstance(value, list):
            return value
        try:
            parsed = json.loads(value)
        except Exception:
            return None
        return parsed if isinstance(parsed, list) else None


class ReplayResultOut(BaseModel):
    id: int
    job_id: int
    test_case_id: Optional[int]
    use_sub_invocation_mocks: bool = False
    source_recording_id: Optional[int] = None
    source_recording_transaction_code: Optional[str] = None
    source_recording_scene_key: Optional[str] = None
    source_recording_sub_call_count: Optional[int] = None
    status: str
    request_method: Optional[str]
    request_uri: Optional[str]
    actual_status_code: Optional[int]
    actual_response: Optional[str]
    expected_response: Optional[str]
    diff_result: Optional[str]
    diff_score: Optional[float] = None
    assertion_results: Optional[str]
    is_pass: bool
    latency_ms: Optional[int]
    failure_category: Optional[str]
    failure_reason: Optional[str]
    actual_sub_calls: Optional[str] = None        # JSON list of replayed sub-calls
    sub_call_diff_detail: Optional[str] = None    # JSON list of per-pair diff results
    created_at: datetime
    transaction_code: Optional[str] = None   # 来自关联的 TestCase

    model_config = {"from_attributes": True}


class ReplayAuditOut(BaseModel):
    id: int
    job_id: int
    result_id: Optional[int] = None
    test_case_id: Optional[int] = None
    application_id: Optional[int] = None
    level: str
    event_type: str
    target_url: Optional[str] = None
    request_method: Optional[str] = None
    request_uri: Optional[str] = None
    transaction_code: Optional[str] = None
    actual_status_code: Optional[int] = None
    latency_ms: Optional[int] = None
    message: Optional[str] = None
    detail: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplayRuleApplyRequest(BaseModel):
    suggestion_key: str
    target: Literal["job_ignore_fields", "application_default_ignore_fields"] = "application_default_ignore_fields"
