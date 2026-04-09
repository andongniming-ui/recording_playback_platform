from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SuiteCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SuiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SuiteCaseItem(BaseModel):
    test_case_id: int
    order_index: int

    model_config = {"from_attributes": True}


class SuiteOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
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
