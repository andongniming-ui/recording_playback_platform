import json
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from typing import Any, Literal


class TransactionRule(BaseModel):
    type: Literal["rename", "delete", "default", "set", "copy"]
    source: Optional[str] = None
    target: Optional[str] = None
    value: Optional[Any] = None
    enabled: bool = True
    description: Optional[str] = None


class TransactionMappingConfig(BaseModel):
    transaction_code: str
    enabled: bool = True
    description: Optional[str] = None
    request_rules: list[TransactionRule] = Field(default_factory=list)
    response_rules: list[TransactionRule] = Field(default_factory=list)


class ApplicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    ssh_host: str
    ssh_user: str
    ssh_key_path: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_port: int = 22
    launch_mode: Literal["ssh_script", "docker_compose"] = "ssh_script"
    docker_workdir: Optional[str] = None
    docker_compose_file: Optional[str] = None
    docker_service_name: Optional[str] = None
    docker_storage_url: Optional[str] = None
    docker_agent_path: Optional[str] = None
    service_port: int = 8080
    jvm_process_name: Optional[str] = None
    arex_storage_url: Optional[str] = None
    arex_app_id: Optional[str] = None
    sample_rate: float = 1.0
    desensitize_rules: Optional[str] = None
    default_ignore_fields: Optional[str] = None
    default_assertions: Optional[str] = None
    transaction_mappings: Optional[str] = None
    default_perf_threshold_ms: Optional[int] = None

    @field_validator("transaction_mappings", mode="before")
    @classmethod
    def _normalize_transaction_mappings(cls, value):
        if value in (None, ""):
            return None
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return None


class ApplicationCreate(ApplicationBase):
    @model_validator(mode="after")
    def _validate_launch_mode_requirements(self):
        if self.launch_mode == "docker_compose":
            missing = []
            if not self.docker_workdir:
                missing.append("docker_workdir")
            if not self.docker_service_name:
                missing.append("docker_service_name")
            if missing:
                raise ValueError(
                    "launch_mode=docker_compose requires: " + ", ".join(missing)
                )
        return self


class ApplicationUpdate(ApplicationBase):
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
    launch_mode: str = "ssh_script"
    docker_workdir: Optional[str] = None
    docker_compose_file: Optional[str] = None
    docker_service_name: Optional[str] = None
    docker_storage_url: Optional[str] = None
    docker_agent_path: Optional[str] = None
    has_password: bool = False     # 是否已设置 SSH 密码（不返回明文）
    service_port: int
    jvm_process_name: Optional[str]
    agent_status: str
    arex_storage_url: Optional[str]
    arex_app_id: Optional[str]
    sample_rate: float
    default_ignore_fields: Optional[list[str]] = None
    default_assertions: Optional[list[dict]] = None
    transaction_mappings: Optional[list[TransactionMappingConfig]] = None
    default_perf_threshold_ms: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_meta(cls, app) -> "ApplicationOut":
        data = cls.model_validate(app)
        data.has_password = bool(app.ssh_password)
        return data

    @field_validator("default_ignore_fields", "default_assertions", mode="before")
    @classmethod
    def _parse_json_field(cls, value):
        if value in (None, ""):
            return None
        if isinstance(value, list):
            return value
        try:
            parsed = json.loads(value)
        except Exception:
            return None
        return parsed if isinstance(parsed, list) else None

    @field_validator("transaction_mappings", mode="before")
    @classmethod
    def _parse_transaction_mappings(cls, value):
        if value in (None, ""):
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]
        try:
            parsed = json.loads(value)
        except Exception:
            return None
        if isinstance(parsed, dict):
            return [parsed]
        return parsed if isinstance(parsed, list) else None
