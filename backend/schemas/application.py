from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ssh_host: str
    ssh_user: str
    ssh_key_path: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_port: int = 22
    service_port: int = 8080
    jvm_process_name: Optional[str] = None
    arex_storage_url: Optional[str] = None
    arex_app_id: Optional[str] = None
    sample_rate: float = 1.0
    desensitize_rules: Optional[str] = None
    default_ignore_fields: Optional[str] = None
    default_assertions: Optional[str] = None
    default_perf_threshold_ms: Optional[int] = None


class ApplicationUpdate(ApplicationCreate):
    name: Optional[str] = None
    ssh_host: Optional[str] = None
    ssh_user: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    ssh_host: str
    ssh_user: str
    ssh_port: int
    service_port: int
    jvm_process_name: Optional[str]
    agent_status: str
    arex_storage_url: Optional[str]
    arex_app_id: Optional[str]
    sample_rate: float
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
