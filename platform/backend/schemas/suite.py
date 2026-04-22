from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SuiteCreate(BaseModel):
    name: str
    description: Optional[str] = None
    suite_type: str = "regression"


class SuiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    suite_type: Optional[str] = None


class SuiteCaseItem(BaseModel):
    test_case_id: int
    order_index: int

    model_config = {"from_attributes": True}


class SuiteOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    suite_type: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class SuiteWithCases(SuiteOut):
    cases: List[SuiteCaseItem] = []


class SetCasesRequest(BaseModel):
    """Replace all cases in a suite with ordered list."""
    case_ids: List[int]


class ReorderRequest(BaseModel):
    """Reorder cases: list of {test_case_id, order_index}."""
    items: List[SuiteCaseItem]


class SuiteRunRequest(BaseModel):
    """Configuration for running a suite as a replay job."""
    target_application_id: Optional[int] = None   # 回放目标应用，不填则用用例所属应用
    ignore_fields: Optional[List[str]] = None      # 忽略字段列表
    concurrency: int = 5                           # 并发数 1~50
    timeout_ms: int = 5000                         # 超时毫秒
    smart_noise_reduction: bool = False            # 智能降噪


class AutoSmokeSuiteCreate(BaseModel):
    application_id: int
    name: Optional[str] = None
    description: Optional[str] = None


class AutoSmokeSuiteResult(BaseModel):
    suite_id: int
    name: str
    added_case_ids: List[int]
    skipped_transaction_codes: List[str] = []
