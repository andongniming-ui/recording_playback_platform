"""Recording session management & arex-storage sync."""
import asyncio
import base64
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete, or_, asc, desc

from database import get_db, async_session_factory
from models.recording import RecordingSession, Recording
from models.application import Application
from models.arex_mocker import ArexMocker
from schemas.recording import (
    RecordingSessionCreate,
    RecordingSessionOut,
    RecordingOut,
    RecordingGroupOut,
    RecordingGovernanceUpdate,
    SyncRequest,
)
from schemas.common import BulkDeleteResponse, BulkIdsRequest
from core.security import require_viewer, require_editor
from config import settings
from utils.governance import (
    build_dedupe_hash,
    build_scene_key,
    infer_transaction_code,
    normalize_governance_status,
    normalize_transaction_code_keys,
)
from utils.repository_capture import (
    NOISE_DYNAMIC_CLASS_OPERATIONS,
    is_noise_dynamic_mocker,
    normalize_repository_sub_call,
)

logger = logging.getLogger(__name__)
runtime_logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/sessions", tags=["sessions"])
HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
REPRESENTATIVE_PRIORITY = {"approved": 4, "candidate": 3, "raw": 2, "archived": 1, "rejected": 0}
_DIDI_COMPLEX_TRANSACTION_CODES = {f"car{index:06d}" for index in range(1, 16)}
_collection_tasks: set[asyncio.Task] = set()
_ACTIVE_PREVIEW_LOOKBACK = timedelta(minutes=5)
_ACTIVE_PREVIEW_PAGE_SIZE = 200


def _ensure_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_sort_order(value: str | None) -> str:
    return "asc" if (value or "").lower() == "asc" else "desc"


def _apply_ordering(stmt, primary_column, id_column, sort_order: str):
    direction = asc if _normalize_sort_order(sort_order) == "asc" else desc
    return stmt.order_by(direction(primary_column), direction(id_column))


def _track_collection_task(task: asyncio.Task) -> None:
    _collection_tasks.add(task)

    def _cleanup(done_task: asyncio.Task) -> None:
        _collection_tasks.discard(done_task)
        try:
            done_task.result()
        except asyncio.CancelledError:
            logger.info("录制同步任务已取消")
        except Exception:
            logger.exception("录制同步任务异常退出")

    task.add_done_callback(_cleanup)


def _extract_records_from_query_response(data) -> list[dict]:
    records_raw: list[dict] = []
    if isinstance(data, dict):
        if "records" in data:
            records_raw = data["records"] or []
        else:
            body_val = data.get("body")
            if isinstance(body_val, list):
                records_raw = body_val
            elif isinstance(body_val, dict):
                records_raw = (
                    body_val.get("records")
                    or body_val.get("recordResult")
                    or body_val.get("recordList")
                    or body_val.get("sources")
                    or []
                )
            if not records_raw:
                records_raw = data.get("recordResult") or []
    return [item for item in records_raw if isinstance(item, dict)]


async def _get_app_or_404(app_id: int, db: AsyncSession) -> Application:
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


def _extract_request_meta(detail: dict, raw: dict) -> tuple[str, str]:
    # arex-storage 0.4.x/0.6.x stores method in targetRequest.attributes.HttpMethod
    def _attrs_method(d: dict) -> str | None:
        target_request = d.get("targetRequest") or {}
        attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
        return attrs.get("HttpMethod") or attrs.get("httpMethod")

    def _attrs_path(d: dict) -> str | None:
        target_request = d.get("targetRequest") or {}
        attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
        return attrs.get("RequestPath") or attrs.get("requestPath")

    method_candidates = [
        _attrs_method(detail),
        _attrs_method(raw),
        detail.get("requestMethod"),
        raw.get("requestMethod"),
    ]
    uri_candidates = [
        _attrs_path(detail),
        _attrs_path(raw),
        detail.get("requestUri"),
        raw.get("requestUri"),
        detail.get("uri"),
        raw.get("uri"),
    ]
    operation_name = detail.get("operationName") or raw.get("operationName") or ""
    if operation_name:
        first, sep, rest = operation_name.partition(" ")
        if sep and first.upper() in HTTP_METHODS:
            method_candidates.append(first.upper())
            uri_candidates.append(rest.strip())
        else:
            uri_candidates.append(operation_name)

    method = next((str(value).upper() for value in method_candidates if value), "GET")
    uri = next((str(value).strip() for value in uri_candidates if value), "/")
    return method, uri


def _decode_body(value) -> str | None:
    """Decode arex-storage request/response body.

    arex agent stores the raw bytes as Base64 in the 'body' field of
    targetRequest / targetResponse.  Decode to UTF-8 text when possible;
    fall back to the original value if it is not valid Base64 or not UTF-8.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return json.dumps(value)
    try:
        decoded = base64.b64decode(value).decode("utf-8")
        return decoded
    except Exception:
        return value


def _serialize_payload(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def _extract_request_headers(detail: dict) -> str | None:
    target_request = detail.get("targetRequest") or {}
    attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
    headers = attrs.get("Headers") or detail.get("requestHeaders") or {}
    return _serialize_payload(headers)


def _extract_request_body(detail: dict) -> str | None:
    target_request = detail.get("targetRequest")
    if isinstance(target_request, dict):
        body = target_request.get("body")
    else:
        body = target_request
    return _decode_body(body or detail.get("requestBody"))


def _extract_response_body(detail: dict) -> str | None:
    target_response = detail.get("targetResponse")
    if isinstance(target_response, dict):
        body = target_response.get("body")
    else:
        body = target_response
    return _decode_body(body or detail.get("responseBody"))


def _stringify_sub_call_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def _normalize_recording_filter_prefixes(value) -> list[str]:
    if value in (None, "", []):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except Exception:
            parsed = None
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
        text = value.strip()
        if not text:
            return []
        lowered = text.lower()
        if any(marker in lowered for marker in ("re:", "regex:")) or (text.startswith("/") and text.endswith("/")):
            parts = re.split(r"[\n;；]+", text)
        else:
            parts = re.split(r"[\n,，;；]+", text)
        return [part.strip() for part in parts if part.strip()]
    return [str(value).strip()] if str(value).strip() else []


def _matches_recording_filter(transaction_code: str | None, prefixes: list[str]) -> bool:
    normalized_tx = (transaction_code or "").strip()
    if not prefixes:
        return True
    if not normalized_tx:
        return False
    normalized_tx_upper = normalized_tx.upper()
    for raw_rule in prefixes:
        rule = (raw_rule or "").strip()
        if not rule:
            continue
        lowered = rule.lower()
        if lowered.startswith("exact:"):
            target = rule.split(":", 1)[1].strip()
            if target and normalized_tx_upper == target.upper():
                return True
            continue
        if rule.startswith("="):
            target = rule[1:].strip()
            if target and normalized_tx_upper == target.upper():
                return True
            continue
        if lowered.startswith("re:") or lowered.startswith("regex:"):
            pattern = rule.split(":", 1)[1].strip()
            if not pattern:
                continue
            try:
                if re.fullmatch(pattern, normalized_tx, flags=re.IGNORECASE):
                    return True
            except re.error:
                logger.warning("无效的录制过滤正则规则: %s", rule)
            continue
        if len(rule) >= 2 and rule.startswith("/") and rule.endswith("/"):
            pattern = rule[1:-1].strip()
            if not pattern:
                continue
            try:
                if re.fullmatch(pattern, normalized_tx, flags=re.IGNORECASE):
                    return True
            except re.error:
                logger.warning("无效的录制过滤正则规则: %s", rule)
            continue
        if normalized_tx_upper.startswith(rule.upper()):
            return True
    return False


def _extract_sub_call_scalar(item: dict, keys: tuple[str, ...]):
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


def _extract_sub_call_children(item: dict) -> list[dict] | None:
    for key in ("children", "subCalls", "subInvocations", "sub_invocations", "items"):
        nested = item.get(key)
        if isinstance(nested, list) and nested:
            return [_normalize_sub_call_item(child) for child in nested if child is not None]
    return None


def _normalize_sub_call_item(item):
    if isinstance(item, dict):
        call_type = (
            item.get("type")
            or item.get("callType")
            or item.get("category")
            or item.get("subCallType")
            or item.get("invocationType")
            or item.get("name")
            or "UNKNOWN"
        )
        request_value = _extract_sub_call_scalar(
            item,
            ("request", "sql", "statement", "command", "query", "body", "detail", "params", "arguments"),
        )
        response_value = _extract_sub_call_scalar(
            item,
            ("response", "result", "returnValue", "output", "responseBody", "value", "rows"),
        )
        target_value = _extract_sub_call_scalar(item, ("target", "db", "service", "host", "endpoint", "datasource"))
        sql_value = _extract_sub_call_scalar(item, ("sql", "statement", "query"))
        params_value = _extract_sub_call_scalar(item, ("params", "parameters", "args", "arguments"))
        database_value = _extract_sub_call_scalar(item, ("database", "dbName", "schema", "catalog", "datasource"))
        operation_value = _extract_sub_call_scalar(item, ("operation", "operationName", "methodName", "action", "command"))
        table_value = _extract_sub_call_scalar(item, ("table", "tableName", "collection"))
        method_value = _extract_sub_call_scalar(item, ("method", "httpMethod", "rpcMethod", "verb"))
        endpoint_value = _extract_sub_call_scalar(item, ("endpoint", "path", "uri", "url"))
        elapsed_value = (
            item.get("elapsed_ms")
            or item.get("elapsedMs")
            or item.get("duration")
            or item.get("cost")
            or item.get("latencyMs")
            or item.get("elapsed")
        )
        normalized = {
            "type": str(call_type).strip() or "UNKNOWN",
            "request": request_value if isinstance(request_value, (dict, list)) else _stringify_sub_call_value(request_value),
            "response": response_value if isinstance(response_value, (dict, list)) else _stringify_sub_call_value(response_value),
        }
        if target_value is not None:
            normalized["target"] = _stringify_sub_call_value(target_value)
        if database_value is not None:
            normalized["database"] = _stringify_sub_call_value(database_value)
        if operation_value is not None:
            normalized["operation"] = _stringify_sub_call_value(operation_value)
        if table_value is not None:
            normalized["table"] = _stringify_sub_call_value(table_value)
        if method_value is not None:
            normalized["method"] = _stringify_sub_call_value(method_value)
        if endpoint_value is not None:
            normalized["endpoint"] = _stringify_sub_call_value(endpoint_value)
        if isinstance(request_value, dict):
            sql_value = sql_value or request_value.get("sql") or request_value.get("statement") or request_value.get("query")
            params_value = params_value or request_value.get("params") or request_value.get("parameters") or request_value.get("args") or request_value.get("arguments")
        if sql_value is not None:
            normalized["sql"] = _stringify_sub_call_value(sql_value)
        if params_value is not None:
            normalized["params"] = params_value if isinstance(params_value, (dict, list)) else _stringify_sub_call_value(params_value)
        if elapsed_value is not None:
            try:
                normalized["elapsed_ms"] = float(elapsed_value)
            except (TypeError, ValueError):
                pass
        if item.get("status") is not None:
            normalized["status"] = _stringify_sub_call_value(item.get("status"))
        for canonical_key, aliases in (
            ("trace_id", ("trace_id", "traceId")),
            ("parent_id", ("parent_id", "parentId")),
            ("span_id", ("span_id", "spanId")),
            ("thread_name", ("thread_name", "threadName")),
            ("error", ("error", "error_message", "message")),
        ):
            value = _extract_sub_call_scalar(item, aliases)
            if value is not None:
                normalized[canonical_key] = _stringify_sub_call_value(value)
        children = _extract_sub_call_children(item)
        if children:
            normalized["children"] = children
        return normalized
    return {
        "type": "UNKNOWN",
        "request": _stringify_sub_call_value(item),
        "response": None,
    }


def _extract_sub_calls(detail: dict, raw: dict) -> list[dict]:
    candidate_keys = (
        "subCallInfo",
        "subCalls",
        "subCallList",
        "subInvocationList",
        "subInvocations",
        "sub_invocations",
    )

    def _maybe_parse(value):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for key in candidate_keys + ("items", "data"):
                nested = value.get(key)
                if isinstance(nested, list):
                    return nested
            return [value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except Exception:
                return None
            return _maybe_parse(parsed)
        return [value]

    for source in (detail, raw):
        for key in candidate_keys:
            normalized = _maybe_parse(source.get(key))
            if normalized:
                return _filter_noise_sub_calls(
                    [_normalize_sub_call_item(item) for item in normalized if item is not None]
                )
    return []


def _is_noise_sub_call(item: dict | None) -> bool:
    if not isinstance(item, dict):
        return False
    sub_type = str(item.get("type") or "").strip().lower()
    operation = str(item.get("operation") or item.get("operationName") or "").strip()
    if sub_type != "dynamicclass":
        return False
    return operation in NOISE_DYNAMIC_CLASS_OPERATIONS


def _filter_noise_sub_calls(items: list[dict] | None) -> list[dict]:
    if not items:
        return []

    filtered: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized = dict(item)
        children = normalized.get("children")
        if isinstance(children, list):
            cleaned_children = _filter_noise_sub_calls(children)
            if cleaned_children:
                normalized["children"] = cleaned_children
            else:
                normalized.pop("children", None)
        if _is_noise_sub_call(normalized):
            continue
        filtered.append(normalized)
    return filtered


def _merge_sub_calls(primary: list[dict] | None, secondary: list[dict] | None) -> list[dict]:
    merged: list[dict] = []
    seen: set[str] = set()
    for group in (primary or [], secondary or []):
        for item in group if isinstance(group, list) else [group]:
            if not isinstance(item, dict):
                continue
            signature = json.dumps(item, ensure_ascii=False, sort_keys=True)
            if signature in seen:
                continue
            seen.add(signature)
            merged.append(item)
    return merged


def _database_sub_call_identity(item: dict | None) -> tuple[str, str, str] | None:
    if not isinstance(item, dict):
        return None
    sub_type = str(item.get("type") or "").strip().lower()
    if sub_type not in {"mysql", "jdbc"}:
        return None
    operation = str(item.get("operation") or "").strip()
    table = str(item.get("table") or "").strip()
    if not operation or not table:
        return None
    return sub_type, operation, table


def _exclude_duplicate_database_sub_calls(
    preferred: list[dict] | None,
    candidates: list[dict] | None,
) -> list[dict]:
    identities = {
        identity
        for identity in (_database_sub_call_identity(item) for item in (preferred or []))
        if identity is not None
    }
    if not identities:
        return candidates or []
    filtered: list[dict] = []
    for item in candidates or []:
        identity = _database_sub_call_identity(item)
        if identity is not None and identity in identities:
            continue
        filtered.append(item)
    return filtered


# BankJdbcRepository 方法名 → 实际表名
_JDBC_METHOD_TABLE: dict[str, str] = {
    "findCustomerByIdNo": "bank_customer",
    "findCustomerByNo": "bank_customer",
    "findAccountByNo": "bank_account",
    "findPrimaryAccountByCustomerNo": "bank_account",
    "findLoanByNo": "bank_loan",
    "findRecentStatements": "bank_statement_line",
    "findRecentTransactionsByAccountNo": "bank_transaction_log",
    "countSubCalls": "bank_sub_call_log",
}

# BankJdbcRepository 方法 → 从 HTTP 请求 XML 中提取的参数字段名
_JDBC_METHOD_PARAM_KEY: dict[str, str] = {
    "findAccountByNo": "account_no",
    "findPrimaryAccountByCustomerNo": "customer_no",
    "findLoanByNo": "loan_no",
    "findRecentStatements": "account_no",
    "findRecentTransactionsByAccountNo": "account_no",
}


def _extract_xml_params(request_body: str | None) -> dict[str, str]:
    """从 HTTP 请求 XML 中提取常用字段值。"""
    params: dict[str, str] = {}
    if not request_body:
        return params
    for field in ("account_no", "loan_no", "amount", "repayment_amount",
                  "withdraw_amount", "customer_no", "id_no", "transaction_id"):
        m = re.search(rf'<{field}>([^<]+)</{field}>', request_body)
        if m:
            params[field] = m.group(1).strip()
    return params


def _extract_didi_xml_params(request_body: str | None) -> dict[str, str]:
    params = {}
    if not request_body:
        return params
    for field in (
        "code",
        "trs_code",
        "service_code",
        "biz_code",
        "request_no",
        "customer_no",
        "plate_no",
        "vin",
        "policy_no",
        "claim_no",
        "garage_code",
        "city",
    ):
        m = re.search(rf"<{field}>([^<]+)</{field}>", request_body)
        if m:
            params[field] = m.group(1).strip()
    return params


def _resolve_didi_db_name(app_id: str | None) -> str | None:
    normalized = (app_id or "").strip().lower()
    if normalized in {"didi-car-sat", "didi-system-a"}:
        return settings.didi_mysql_db_sat
    if normalized in {"didi-car-uat", "didi-system-b"}:
        return settings.didi_mysql_db_uat
    return None


async def _fetch_didi_sub_calls(request_body: str | None, app_id: str) -> list[dict]:
    db_name = _resolve_didi_db_name(app_id)
    if not request_body or not settings.didi_mysql_host or not db_name:
        return []

    txn_code = infer_transaction_code(request_body)
    if txn_code not in _DIDI_COMPLEX_TRANSACTION_CODES:
        return []

    params = _extract_didi_xml_params(request_body)
    plate_no = params.get("plate_no")
    vin = params.get("vin")
    customer_no = params.get("customer_no")
    policy_no = params.get("policy_no")
    claim_no = params.get("claim_no")
    garage_code = params.get("garage_code")
    request_no = params.get("request_no")

    async def _fetchone_dict(cursor, sql: str, sql_params: tuple) -> dict | None:
        await cursor.execute(sql, sql_params)
        row = await cursor.fetchone()
        if not row:
            return None
        columns = [item[0] for item in cursor.description]
        return {
            column: (str(value) if value is not None else None)
            for column, value in zip(columns, row)
        }

    try:
        import aiomysql

        conn = await aiomysql.connect(
            host=settings.didi_mysql_host,
            port=settings.didi_mysql_port,
            user=settings.didi_mysql_user,
            password=settings.didi_mysql_password,
            db=db_name,
            connect_timeout=3,
            charset="utf8mb4",
        )
        try:
            cursor = await conn.cursor()

            vehicle_row = None
            if plate_no:
                vehicle_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_vehicle WHERE plate_no = %s LIMIT 1",
                    (plate_no,),
                )
            elif vin:
                vehicle_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_vehicle WHERE vin = %s LIMIT 1",
                    (vin,),
                )

            if not customer_no and vehicle_row:
                customer_no = vehicle_row.get("owner_customer_no") or customer_no

            customer_row = None
            if customer_no:
                customer_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_customer WHERE customer_no = %s LIMIT 1",
                    (customer_no,),
                )

            policy_row = None
            if policy_no:
                policy_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_policy WHERE policy_no = %s LIMIT 1",
                    (policy_no,),
                )
            elif plate_no:
                policy_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_policy WHERE plate_no = %s ORDER BY policy_no LIMIT 1",
                    (plate_no,),
                )

            claim_row = None
            if claim_no:
                claim_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_claim WHERE claim_no = %s LIMIT 1",
                    (claim_no,),
                )
            elif plate_no:
                claim_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_claim WHERE plate_no = %s ORDER BY claim_no LIMIT 1",
                    (plate_no,),
                )

            dispatch_row = None
            if garage_code:
                dispatch_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_dispatch WHERE garage_code = %s ORDER BY dispatch_no LIMIT 1",
                    (garage_code,),
                )
            elif plate_no:
                dispatch_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_dispatch WHERE plate_no = %s ORDER BY dispatch_no LIMIT 1",
                    (plate_no,),
                )

            audit_row = None
            if request_no:
                audit_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_order_audit WHERE request_no = %s ORDER BY id DESC LIMIT 1",
                    (request_no,),
                )

            updated_vehicle_row = None
            if plate_no:
                updated_vehicle_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_vehicle WHERE plate_no = %s LIMIT 1",
                    (plate_no,),
                )
            elif vin:
                updated_vehicle_row = await _fetchone_dict(
                    cursor,
                    "SELECT * FROM car_vehicle WHERE vin = %s LIMIT 1",
                    (vin,),
                )

        finally:
            conn.close()
    except Exception as exc:
        logger.warning("[didi_sub_calls] 查询 %s 失败: %s", app_id, exc)
        return []

    sub_calls = [
        {
            "type": "MySQL",
            "source": "reconstructed",
            "database": db_name,
            "table": "car_vehicle",
            "operation": "SELECT car_vehicle",
            "request": {k: v for k, v in {"plateNo": plate_no, "vin": vin}.items() if v},
            "params": {k: v for k, v in {"plateNo": plate_no, "vin": vin}.items() if v},
            "response": vehicle_row or {},
            "status": "READ",
        },
        {
            "type": "MySQL",
            "source": "reconstructed",
            "database": db_name,
            "table": "car_customer",
            "operation": "SELECT car_customer",
            "request": {"customerNo": customer_no} if customer_no else None,
            "params": {"customerNo": customer_no} if customer_no else None,
            "response": customer_row or {},
            "status": "READ",
        },
        {
            "type": "MySQL",
            "source": "reconstructed",
            "database": db_name,
            "table": "car_policy",
            "operation": "SELECT car_policy",
            "request": {k: v for k, v in {"policyNo": policy_no, "plateNo": plate_no}.items() if v},
            "params": {k: v for k, v in {"policyNo": policy_no, "plateNo": plate_no}.items() if v},
            "response": policy_row or {},
            "status": "READ",
        },
        {
            "type": "MySQL",
            "source": "reconstructed",
            "database": db_name,
            "table": "car_claim",
            "operation": "SELECT car_claim",
            "request": {k: v for k, v in {"claimNo": claim_no, "plateNo": plate_no}.items() if v},
            "params": {k: v for k, v in {"claimNo": claim_no, "plateNo": plate_no}.items() if v},
            "response": claim_row or {},
            "status": "READ",
        },
        {
            "type": "MySQL",
            "source": "reconstructed",
            "database": db_name,
            "table": "car_dispatch",
            "operation": "SELECT car_dispatch",
            "request": {k: v for k, v in {"plateNo": plate_no, "garageCode": garage_code}.items() if v},
            "params": {k: v for k, v in {"plateNo": plate_no, "garageCode": garage_code}.items() if v},
            "response": dispatch_row or {},
            "status": "READ",
        },
    ]

    if request_no:
        sub_calls.append(
            {
                "type": "MySQL",
                "source": "reconstructed",
                "database": db_name,
                "table": "car_order_audit",
                "operation": "INSERT car_order_audit",
                "request": {
                    key: value
                    for key, value in {
                        "txnCode": txn_code,
                        "requestNo": request_no,
                        "customerNo": customer_no,
                        "plateNo": plate_no,
                    }.items()
                    if value
                },
                "params": {
                    key: value
                    for key, value in {
                        "txnCode": txn_code,
                        "requestNo": request_no,
                        "customerNo": customer_no,
                        "plateNo": plate_no,
                    }.items()
                    if value
                },
                "response": audit_row or {},
                "status": "WRITE",
            }
        )

    if plate_no or vin:
        sub_calls.append(
            {
                "type": "MySQL",
                "source": "reconstructed",
                "database": db_name,
                "table": "car_vehicle",
                "operation": "UPDATE car_vehicle",
                "request": {
                    key: value
                    for key, value in {
                        "plateNo": plate_no,
                        "vin": vin,
                        "status": (updated_vehicle_row or {}).get("vehicle_status"),
                    }.items()
                    if value
                },
                "params": {
                    key: value
                    for key, value in {
                        "plateNo": plate_no,
                        "vin": vin,
                        "status": (updated_vehicle_row or {}).get("vehicle_status"),
                    }.items()
                    if value
                },
                "response": updated_vehicle_row or {},
                "status": "WRITE",
            }
        )

    return sub_calls


def _assign_jdbc_to_step(method_name: str, step_names: list[str]) -> str | None:
    """将 BankJdbcRepository 方法按业务语义归属到对应步骤。"""
    n = method_name.lower()
    if "customer" in n:
        return next((s for s in step_names if "customer" in s.lower()), None)
    if "account" in n or "primaryaccount" in n:
        return next((s for s in step_names if "account" in s.lower()), None)
    if "loan" in n:
        return next((s for s in step_names if "loan" in s.lower()), None)
    # findRecentStatements / findRecentTransactionsByAccountNo / countSubCalls → 最后一个 db 步骤
    last_db = next((s for s in reversed(step_names) if s not in ("risk-check",)), None)
    return last_db


async def _fetch_nls_sub_calls(
    request_body: str | None,
    app_id: str,
    record_id: str | None = None,
    db: AsyncSession | None = None,
) -> list[dict]:
    """从 N-LS bank_sub_call_log 查询业务步骤子调用。

    通过 request_body XML 中的 SYS_EVT_TRACE_ID 关联到 bank_transaction_log，
    再查询对应的 bank_sub_call_log 业务步骤。
    同时从 arex_mocker 中获取 SubCallLogger.trace 的响应数据（按时间顺序对齐）。
    """
    if not request_body or not settings.nls_mysql_host:
        return []

    m = re.search(r'<SYS_EVT_TRACE_ID>([^<]+)</SYS_EVT_TRACE_ID>', request_body)
    if not m:
        return []
    trace_id = m.group(1).strip()

    # app_id 格式如 "nls-sat" → db 名 "nls_sat"
    db_name = app_id.replace("-", "_")

    try:
        import aiomysql
        conn = await aiomysql.connect(
            host=settings.nls_mysql_host,
            port=settings.nls_mysql_port,
            user=settings.nls_mysql_user,
            password=settings.nls_mysql_password,
            db=db_name,
            connect_timeout=3,
        )
        try:
            cur = await conn.cursor()
            await cur.execute(
                "SELECT id FROM bank_transaction_log WHERE sys_evt_trace_id = %s LIMIT 1",
                (trace_id,),
            )
            row = await cur.fetchone()
            if not row:
                return []
            tx_log_id = row[0]

            await cur.execute(
                "SELECT step_name, layer_name, detail_text, duration_ms, result_status "
                "FROM bank_sub_call_log WHERE tx_log_id = %s ORDER BY id",
                (tx_log_id,),
            )
            steps = await cur.fetchall()
        finally:
            conn.close()

        if not steps:
            return []

        step_names = [row[0] for row in steps]
        xml_params = _extract_xml_params(request_body)
        last_db_step = next((s[0] for s in reversed(steps) if s[1] == "db"), None)

        # ── 1. 从 arex_mocker 取 BankJdbcRepository READ 调用 ──────────────
        step_children: dict[str, list[dict]] = {name: [] for name in step_names}
        # 用于提升到父步骤的单条响应（key=step_name）
        step_read_resp: dict[str, object] = {}

        if record_id and db is not None:
            result = await db.execute(
                select(ArexMocker).where(
                    ArexMocker.record_id == record_id,
                    ArexMocker.is_entry_point == False,  # noqa: E712
                ).order_by(ArexMocker.created_at_ms)
            )
            for mocker_row in result.scalars().all():
                try:
                    md = json.loads(mocker_row.mocker_data)
                except Exception:
                    continue
                op = md.get("operationName") or ""
                if "BankJdbcRepository" not in op:
                    continue
                method_name = op.split(".")[-1]
                table = _JDBC_METHOD_TABLE.get(method_name, "")
                resp_body = (md.get("targetResponse") or {}).get("body")
                if isinstance(resp_body, str):
                    try:
                        resp_body = json.loads(resp_body)
                    except Exception:
                        pass
                param_key = _JDBC_METHOD_PARAM_KEY.get(method_name)
                req_param = xml_params.get(param_key) if param_key else None
                if not req_param and "customer" in method_name.lower():
                    req_param = xml_params.get("customer_no") or xml_params.get("id_no")
                # 如果参数仍为空，从响应中反查主键字段
                # 如 car004_followup XML 无 loan_no，但 findLoanByNo 响应含 loan_no
                # 如 findCustomerByNo 响应含 customer_no
                if not req_param and isinstance(resp_body, dict):
                    if param_key:
                        req_param = resp_body.get(param_key)
                    elif "customer" in method_name.lower():
                        req_param = resp_body.get("customer_no") or resp_body.get("id_no")
                child = {
                    "type": "jdbc",
                    "operation": method_name,
                    "table": table,
                    "request": req_param,
                    "response": resp_body,
                    "status": "SUCCESS",
                }
                target = _assign_jdbc_to_step(method_name, step_names)
                if target and target in step_children:
                    step_children[target].append(child)
                    # 第一个非 count 的 READ 结果提升为父步骤响应
                    if method_name != "countSubCalls" and target not in step_read_resp:
                        step_read_resp[target] = resp_body

        # ── 2. 从 N-LS MySQL 查写入数据（bank_transaction_log / bank_statement_line）
        try:
            import aiomysql
            conn2 = await aiomysql.connect(
                host=settings.nls_mysql_host,
                port=settings.nls_mysql_port,
                user=settings.nls_mysql_user,
                password=settings.nls_mysql_password,
                db=db_name,
                connect_timeout=3,
                charset="utf8mb4",
            )
            try:
                cur2 = await conn2.cursor()
                # bank_transaction_log 写入记录
                await cur2.execute(
                    "SELECT transaction_id, transaction_code, transaction_name, "
                    "account_no, loan_no, status, created_at "
                    "FROM bank_transaction_log WHERE sys_evt_trace_id = %s LIMIT 1",
                    (trace_id,),
                )
                txlog = await cur2.fetchone()
                if txlog and last_db_step:
                    cols = ("transaction_id", "transaction_code", "transaction_name",
                            "account_no", "loan_no", "status", "created_at")
                    txlog_dict = {c: (str(v) if v is not None else None)
                                  for c, v in zip(cols, txlog)}
                    step_children[last_db_step].append({
                        "type": "jdbc",
                        "operation": "INSERT bank_transaction_log",
                        "table": "bank_transaction_log",
                        "request": {k: xml_params.get(k) for k in ("account_no", "loan_no")
                                    if xml_params.get(k)},
                        "response": txlog_dict,
                        "status": "WRITE",
                    })
                # bank_statement_line 写入记录
                await cur2.execute(
                    "SELECT account_no, loan_no, transaction_code, direction, "
                    "amount, balance_after, memo "
                    "FROM bank_statement_line WHERE trace_id = %s",
                    (trace_id,),
                )
                for sl in await cur2.fetchall():
                    cols2 = ("account_no", "loan_no", "transaction_code",
                             "direction", "amount", "balance_after", "memo")
                    sl_dict = {c: (str(v) if v is not None else None)
                               for c, v in zip(cols2, sl)}
                    if last_db_step:
                        step_children[last_db_step].append({
                            "type": "jdbc",
                            "operation": "INSERT bank_statement_line",
                            "table": "bank_statement_line",
                            "request": {k: xml_params.get(k)
                                        for k in ("account_no", "loan_no",
                                                  "repayment_amount", "withdraw_amount")
                                        if xml_params.get(k)},
                            "response": sl_dict,
                            "status": "WRITE",
                        })
                # bank_account 交易后状态（UPDATE 结果快照）
                account_no = xml_params.get("account_no")
                if account_no and last_db_step:
                    await cur2.execute(
                        "SELECT * FROM bank_account WHERE account_no = %s LIMIT 1",
                        (account_no,),
                    )
                    acct_row = await cur2.fetchone()
                    if acct_row:
                        acct_cols = [d[0] for d in cur2.description]
                        acct_dict = {c: (str(v) if v is not None else None)
                                     for c, v in zip(acct_cols, acct_row)}
                        step_children[last_db_step].append({
                            "type": "jdbc",
                            "operation": "UPDATE bank_account",
                            "table": "bank_account",
                            "request": {"account_no": account_no},
                            "response": acct_dict,
                            "status": "WRITE",
                        })
                # bank_loan 交易后状态（UPDATE 结果快照）
                loan_step = next((s for s in step_names if "loan" in s.lower()), None)
                loan_no_for_update = xml_params.get("loan_no")
                if not loan_no_for_update and loan_step:
                    kids = step_children.get(loan_step, [])
                    first_resp = kids[0].get("response") if kids else None
                    if isinstance(first_resp, dict):
                        loan_no_for_update = first_resp.get("loan_no")
                if loan_no_for_update and last_db_step:
                    await cur2.execute(
                        "SELECT * FROM bank_loan WHERE loan_no = %s LIMIT 1",
                        (loan_no_for_update,),
                    )
                    loan_row = await cur2.fetchone()
                    if loan_row:
                        loan_cols = [d[0] for d in cur2.description]
                        loan_dict = {c: (str(v) if v is not None else None)
                                     for c, v in zip(loan_cols, loan_row)}
                        step_children[last_db_step].append({
                            "type": "jdbc",
                            "operation": "UPDATE bank_loan",
                            "table": "bank_loan",
                            "request": {"loan_no": loan_no_for_update},
                            "response": loan_dict,
                            "status": "WRITE",
                        })
            finally:
                conn2.close()
        except Exception as e:
            logger.debug("[nls_sub_calls] 写入数据查询失败: %s", e)

        # ── 3. 构建父步骤（request = 实际参数，response = 首条 READ 结果）──
        # 父步骤 request 参数映射
        step_req_param: dict[str, object] = {}
        for sname, _, _, _, _ in steps:
            n = sname.lower()
            if "account" in n:
                step_req_param[sname] = xml_params.get("account_no")
            elif "loan" in n:
                loan_no = xml_params.get("loan_no")
                if not loan_no:
                    # 从 findLoanByNo 子调用响应中反查 loan_no（如 car004_followup）
                    kids = step_children.get(sname, [])
                    loan_resp = kids[0].get("response") if kids else None
                    if isinstance(loan_resp, dict):
                        loan_no = loan_resp.get("loan_no")
                step_req_param[sname] = loan_no
            elif "customer" in n:
                # 从首个 READ 子节点响应中提取 customer_no
                kids = step_children.get(sname, [])
                cust_resp = kids[0].get("response") if kids else None
                if isinstance(cust_resp, dict):
                    step_req_param[sname] = cust_resp.get("customer_no") or cust_resp.get("id_no")
                else:
                    step_req_param[sname] = xml_params.get("customer_no") or xml_params.get("id_no")
            elif sname == last_db_step:  # repay / withdraw
                amt = xml_params.get("repayment_amount") or xml_params.get("withdraw_amount") or xml_params.get("amount")
                if amt:
                    step_req_param[sname] = {
                        k: xml_params[k] for k in ("account_no", "loan_no",
                                                    "repayment_amount", "withdraw_amount")
                        if xml_params.get(k)
                    }

        sub_calls = []
        for step_name, layer_name, detail_text, duration_ms, result_status in steps:
            # 父步骤用 "business" 类型，区别于子调用的 "jdbc" 类型
            # layer_name="risk" 保留为 "risk" 以显示"风控"标签
            sub_type = "business" if layer_name == "db" else (layer_name or "business")
            children = step_children.get(step_name) or None
            parent_req = step_req_param.get(step_name) or detail_text
            parent_resp = step_read_resp.get(step_name)
            sub_calls.append({
                "type": sub_type,
                "operation": step_name,
                "request": parent_req,
                "response": parent_resp,
                "elapsed_ms": duration_ms,
                "status": result_status,
                **({"children": children} if children else {}),
            })
        return sub_calls

    except Exception as e:
        logger.warning("[nls_sub_calls] 查询 %s trace=%s 失败: %s", app_id, trace_id, e)
        return []


async def _remove_sub_invocation_recordings(session_id: int, db: AsyncSession) -> int:
    """移除本 session 中属于其他录制的 HTTP 子调用的 Servlet entry-point 录制。

    当 arex-agent 拦截到内部 HTTP 调用时，会将被调用方的 Servlet 请求也录制为独立
    entry-point，导致录制列表里出现主调用和子调用混合的情况。本函数通过扫描
    HttpClient 子调用 mocker 的响应头中的 arex-record-id，识别并删除这些录制。
    """
    result = await db.execute(
        select(Recording.id, Recording.record_id, Recording.request_uri, Recording.request_headers)
        .where(Recording.session_id == session_id)
    )
    rows = result.all()
    session_record_ids = {row.record_id for row in rows}
    session_id_map = {row.record_id: row.id for row in rows}
    if not session_record_ids:
        return 0

    # Scan HttpClient mockers for arex-record-id in response headers and fallback paths
    sub_invocation_record_ids: set[str] = set()
    httpclient_paths: set[str] = set()
    httpclient_result = await db.execute(
        select(ArexMocker.mocker_data).where(
            ArexMocker.record_id.in_(session_record_ids),
            ArexMocker.is_entry_point == False,  # noqa: E712
            ArexMocker.category_name == "HttpClient",
        )
    )
    for mocker_json in httpclient_result.scalars().all():
        try:
            mocker = json.loads(mocker_json)
            operation_name = str(mocker.get("operationName") or "").strip()
            if operation_name:
                httpclient_paths.add(operation_name.partition("?")[0])
            target_response = mocker.get("targetResponse") or {}

            # Method 1: targetResponse.attributes.Headers (some agent versions)
            resp_attrs = target_response.get("attributes") or {}
            headers: dict = resp_attrs.get("Headers") or {}
            arex_id = headers.get("arex-record-id")

            # Method 2: targetResponse.body is a JSON string containing {"headers": {...}}
            # Used by RestTemplate instrumentation in arex-agent 0.4.x
            if not arex_id:
                resp_body = target_response.get("body")
                if isinstance(resp_body, str):
                    try:
                        parsed_body = json.loads(resp_body)
                        body_headers = parsed_body.get("headers") or {}
                        arex_id = body_headers.get("arex-record-id")
                    except Exception:
                        pass

            if isinstance(arex_id, str):
                sub_invocation_record_ids.add(arex_id)
            elif isinstance(arex_id, list):
                sub_invocation_record_ids.update(arex_id)
        except Exception:
            pass

    def _looks_like_local_internal_recording(request_uri: str | None, request_headers: str | None) -> bool:
        uri = (request_uri or "").strip()
        if uri.startswith("/internal/"):
            return True
        if not request_headers:
            return False
        try:
            headers = json.loads(request_headers) if isinstance(request_headers, str) else request_headers
        except Exception:
            return False
        if not isinstance(headers, dict):
            return False
        host = str(headers.get("host") or headers.get("Host") or "").strip().lower()
        if not (host.startswith("127.0.0.1:") or host.startswith("localhost:")):
            return False
        return uri.partition("?")[0] in httpclient_paths

    for row in rows:
        if _looks_like_local_internal_recording(row.request_uri, row.request_headers) and row.record_id:
            sub_invocation_record_ids.add(row.record_id)

    to_delete = [
        session_id_map[rid]
        for rid in sub_invocation_record_ids
        if rid in session_id_map
    ]
    if to_delete:
        await db.execute(delete(Recording).where(Recording.id.in_(to_delete)))
    return len(to_delete)


async def _fetch_dynamic_class_sub_calls(record_id: str, db: AsyncSession) -> list[dict]:
    """从 arex_mocker 表查询 DynamicClass 子调用并转换为 sub_call 格式。"""
    result = await db.execute(
        select(ArexMocker).where(
            ArexMocker.record_id == record_id,
            ArexMocker.is_entry_point == False,  # noqa: E712
        )
    )
    sub_calls = []
    for m in result.scalars().all():
        try:
            mocker = json.loads(m.mocker_data)
        except Exception:
            continue
        op_name = mocker.get("operationName") or m.category_name or "UNKNOWN"
        repository_sub_call = normalize_repository_sub_call(mocker, m.category_name)
        if repository_sub_call is not None:
            sub_calls.append(repository_sub_call)
            continue
        target_req = mocker.get("targetRequest") or {}
        target_resp = mocker.get("targetResponse") or {}
        req_attrs = target_req.get("attributes") or {}
        req_body = target_req.get("body")
        resp_body = target_resp.get("body")
        if isinstance(resp_body, str):
            try:
                resp_body = json.loads(resp_body)
            except Exception:
                pass

        sub_call: dict = {
            "type": m.category_name or "DynamicClass",
            "operation": op_name,
            "request": req_body,
            "response": resp_body,
        }

        # HttpClient: extract HTTP method and full endpoint from request attributes
        cat = (m.category_name or "").lower()
        if "http" in cat:
            http_method = req_attrs.get("HttpMethod") or req_attrs.get("httpMethod")
            query_string = req_attrs.get("QueryString") or req_attrs.get("queryString")
            if http_method:
                sub_call["method"] = http_method
            if op_name and query_string:
                sub_call["endpoint"] = f"{op_name}?{query_string}"
            elif op_name:
                sub_call["endpoint"] = op_name

        if _is_noise_sub_call(sub_call) or is_noise_dynamic_mocker(op_name, m.category_name):
            continue
        sub_calls.append(sub_call)
    return _filter_noise_sub_calls(sub_calls)


async def _duplicate_count_map(db: AsyncSession, recordings: list[Recording]) -> dict[str, int]:
    hashes = {item.dedupe_hash for item in recordings if item.dedupe_hash}
    if not hashes:
        return {}
    result = await db.execute(
        select(Recording.dedupe_hash, func.count(Recording.id))
        .where(Recording.dedupe_hash.in_(hashes))
        .group_by(Recording.dedupe_hash)
    )
    return {dedupe_hash: count for dedupe_hash, count in result.all() if dedupe_hash}


async def _serialize_recordings(db: AsyncSession, recordings: list[Recording]) -> list[RecordingOut]:
    duplicate_counts = await _duplicate_count_map(db, recordings)
    return [
        RecordingOut.model_validate(recording).model_copy(
            update={"duplicate_count": duplicate_counts.get(recording.dedupe_hash or "", 1)}
        )
        for recording in recordings
    ]


def _representative_sort_key(recording: Recording) -> tuple[int, datetime, int]:
    recorded_at = recording.recorded_at or datetime.min.replace(tzinfo=timezone.utc)
    return (
        REPRESENTATIVE_PRIORITY.get(recording.governance_status or "raw", 0),
        recorded_at,
        recording.id,
    )


def _group_recordings(recordings: list[Recording]) -> list[RecordingGroupOut]:
    groups: dict[tuple[int, str | None, str | None], list[Recording]] = {}
    for recording in recordings:
        key = (recording.application_id, recording.transaction_code, recording.scene_key)
        groups.setdefault(key, []).append(recording)

    result: list[RecordingGroupOut] = []
    for (application_id, transaction_code, scene_key), items in groups.items():
        representative = max(items, key=_representative_sort_key)
        latest = max(item.recorded_at for item in items)
        result.append(
            RecordingGroupOut(
                application_id=application_id,
                transaction_code=transaction_code,
                scene_key=scene_key,
                total_count=len(items),
                approved_count=sum(1 for item in items if item.governance_status == "approved"),
                candidate_count=sum(1 for item in items if item.governance_status == "candidate"),
                raw_count=sum(1 for item in items if item.governance_status == "raw"),
                latest_recorded_at=latest,
                representative_recording_id=representative.id,
                representative_governance_status=representative.governance_status,
                representative_request_method=representative.request_method,
                representative_request_uri=representative.request_uri,
            )
        )
    result.sort(key=lambda item: (item.latest_recorded_at, item.transaction_code or "", item.scene_key or ""), reverse=True)
    return result


async def _refresh_session_total_counts(db: AsyncSession, session_ids: list[int]) -> None:
    unique_ids = sorted({session_id for session_id in session_ids if session_id})
    for session_id in unique_ids:
        count_result = await db.execute(
            select(func.count()).select_from(Recording).where(Recording.session_id == session_id)
        )
        await db.execute(
            update(RecordingSession)
            .where(RecordingSession.id == session_id)
            .values(total_count=count_result.scalar_one())
        )


@router.get("", response_model=list[RecordingSessionOut])
async def list_sessions(
    application_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(RecordingSession)
    if application_id:
        stmt = stmt.where(RecordingSession.application_id == application_id)
    if status:
        stmt = stmt.where(RecordingSession.status == status)
    if search:
        stmt = stmt.where(RecordingSession.name.contains(search))
    if created_after:
        stmt = stmt.where(RecordingSession.created_at >= created_after)
    if created_before:
        stmt = stmt.where(RecordingSession.created_at <= created_before)
    sort_mapping = {
        "created_at": RecordingSession.created_at,
        "start_time": RecordingSession.start_time,
        "end_time": RecordingSession.end_time,
        "total_count": RecordingSession.total_count,
        "id": RecordingSession.id,
    }
    primary_column = sort_mapping.get(sort_by, RecordingSession.created_at)
    stmt = _apply_ordering(stmt, primary_column, RecordingSession.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=RecordingSessionOut, status_code=201)
async def create_session(
    body: RecordingSessionCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    await _get_app_or_404(body.application_id, db)
    normalized_filter_prefixes = _normalize_recording_filter_prefixes(body.recording_filter_prefixes)
    session = RecordingSession(
        application_id=body.application_id,
        name=body.name,
        status="idle",
        recording_filter_prefixes=json.dumps(normalized_filter_prefixes, ensure_ascii=False) if normalized_filter_prefixes else None,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_sessions(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    session_ids = sorted({session_id for session_id in body.ids if session_id})
    if not session_ids:
        return BulkDeleteResponse(deleted=0)

    result = await db.execute(select(RecordingSession).where(RecordingSession.id.in_(session_ids)))
    sessions = result.scalars().all()
    if not sessions:
        return BulkDeleteResponse(deleted=0)

    blocked = [item.id for item in sessions if item.status in {"active", "collecting"}]
    if blocked:
        raise HTTPException(status_code=409, detail=f"Sessions are still running: {blocked[0]}")

    await db.execute(delete(Recording).where(Recording.session_id.in_([item.id for item in sessions])))
    await db.execute(delete(RecordingSession).where(RecordingSession.id.in_([item.id for item in sessions])))
    await db.commit()
    return BulkDeleteResponse(deleted=len(sessions))


@router.get("/{session_id}", response_model=RecordingSessionOut)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.status in {"active", "collecting"}:
        raise HTTPException(status_code=409, detail=f"Session is still running: {sess.status}")
    # Explicitly delete child recordings first (SQLite may not enforce FK cascade)
    await db.execute(delete(Recording).where(Recording.session_id == session_id))
    await db.delete(sess)
    await db.commit()


@router.get("/{session_id}/debug-storage")
async def debug_arex_storage(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """
    调试端点：直接查询 arex-storage 并返回原始响应。
    用于排查录制数为 0 的问题——看看 arex-storage 实际返回了什么。
    """
    from integration.arex_client import ArexClient
    from datetime import timedelta

    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    app_result = await db.execute(select(Application).where(Application.id == sess.application_id))
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    arex_url = app.arex_storage_url or settings.arex_storage_url
    app_id = app.arex_app_id or app.name
    client = ArexClient(arex_url)

    now = datetime.now(timezone.utc)
    begin_time = now - timedelta(hours=24)

    try:
        raw = await client.query_recordings(
            app_id=app_id,
            begin_time=begin_time,
            end_time=now,
            page_size=50,
            page_index=0,
        )
        return {
            "arex_url": arex_url,
            "app_id": app_id,
            "begin_time": begin_time.isoformat(),
            "end_time": now.isoformat(),
            "raw_response_keys": list(raw.keys()) if isinstance(raw, dict) else str(type(raw)),
            "raw_response": raw,
        }
    except Exception as e:
        return {"error": str(e), "arex_url": arex_url, "app_id": app_id}


async def _load_session_or_404(session_id: int, db: AsyncSession) -> RecordingSession:
    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


async def _enqueue_collection(
    session_id: int,
    sess: RecordingSession,
    body: SyncRequest,
    db: AsyncSession,
):
    recording_filter_prefixes = _normalize_recording_filter_prefixes(sess.recording_filter_prefixes)
    now = datetime.now(timezone.utc)
    sess.status = "collecting"
    sess.end_time = None
    sess.error_message = None
    await db.commit()

    task = asyncio.create_task(
        _sync_from_arex_storage(
            session_id=session_id,
            application_id=sess.application_id,
            recording_filter_prefixes=recording_filter_prefixes,
            begin_time=body.begin_time or sess.start_time,
            end_time=body.end_time or now,
            page_size=body.page_size,
            page_index=body.page_index,
        ),
        name=f"recording-sync-{session_id}",
    )
    _track_collection_task(task)
    return {"message": "Collection started", "session_id": session_id, "status": "collecting"}


@router.post("/{session_id}/start")
async def start_recording(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "idle":
        raise HTTPException(status_code=409, detail=f"Session is not idle: {sess.status}")

    now = datetime.now(timezone.utc)
    sess.status = "active"
    sess.start_time = now
    sess.end_time = None
    sess.total_count = 0
    sess.error_message = None
    await db.commit()
    await db.refresh(sess)
    return {"message": "Recording started", "session_id": session_id, "status": sess.status}


@router.post("/{session_id}/stop")
async def stop_recording(
    session_id: int,
    body: SyncRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Stop recording and sync buffered recordings from arex-storage."""
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "active":
        raise HTTPException(status_code=409, detail=f"Session is not active: {sess.status}")
    return await _enqueue_collection(session_id, sess, body, db)


@router.post("/{session_id}/sync")
async def sync_recordings(
    session_id: int,
    body: SyncRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Compatibility alias for stop_recording."""
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "active":
        raise HTTPException(status_code=409, detail=f"Session is not active: {sess.status}")
    return await _enqueue_collection(session_id, sess, body, db)


async def _sync_from_arex_storage(
    session_id: int,
    application_id: int,
    recording_filter_prefixes: list[str] | None = None,
    begin_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page_size: int = 50,
    page_index: int = 0,
    finalize_session: bool = True,
):
    """Background task: pull recordings from arex-storage and save to DB."""
    from integration.arex_client import ArexClient, ArexClientError

    async with async_session_factory() as db:
        # Get application
        result = await db.execute(select(Application).where(Application.id == application_id))
        app = result.scalar_one_or_none()
        if not app:
            return

        arex_url = app.arex_storage_url or settings.arex_storage_url
        app_id = app.arex_app_id or app.name
        transaction_code_fields = normalize_transaction_code_keys(app.transaction_code_fields)
        client = ArexClient(arex_url)

        # Default time range: last 7 days
        now = datetime.now(timezone.utc)
        if not begin_time:
            from datetime import timedelta
            begin_time = now - timedelta(days=7)
        if not end_time:
            end_time = now

        try:
            remote_total = None
            try:
                remote_total = await client.count_recordings(
                    app_id=app_id,
                    begin_time=begin_time,
                    end_time=end_time,
                )
            except Exception as exc:
                logger.info("同步会话 %s：获取录制总数失败，回退到逐页探测: %s", session_id, exc)

            current_page = max(page_index, 0)
            while True:
                data = await client.query_recordings(
                    app_id=app_id,
                    begin_time=begin_time,
                    end_time=end_time,
                    page_size=page_size,
                    page_index=current_page,
                )
                logger.info(
                    "同步会话 %s：第 %d 页 replayCase 响应 keys: %s",
                    session_id,
                    current_page,
                    list(data.keys()) if isinstance(data, dict) else type(data).__name__,
                )
                records_raw = _extract_records_from_query_response(data)
                logger.info(
                    "同步会话 %s：第 %d 页获取到 %d 条录制记录",
                    session_id,
                    current_page,
                    len(records_raw),
                )
                if not records_raw:
                    break

                for raw in records_raw:
                    record_id = raw.get("recordId") or raw.get("id")
                    if not record_id:
                        continue

                    existing = await db.execute(
                        select(Recording).where(Recording.record_id == str(record_id))
                    )
                    if existing.scalar_one_or_none():
                        continue

                    try:
                        detail = await client.view_recording(str(record_id))
                    except Exception:
                        detail = raw

                    request_method, request_uri = _extract_request_meta(detail, raw)
                    request_body = _extract_request_body(detail)
                    response_body = _extract_response_body(detail)
                    response_status = detail.get("responseStatusCode") or 200
                    transaction_code = infer_transaction_code(
                        request_body,
                        response_body,
                        candidate_keys=transaction_code_fields,
                    )
                    if recording_filter_prefixes and not _matches_recording_filter(transaction_code, recording_filter_prefixes):
                        logger.info(
                            "同步会话 %s：跳过录制 %s，因为交易码 %s 不匹配过滤规则 %s",
                            session_id,
                            record_id,
                            transaction_code,
                            recording_filter_prefixes,
                        )
                        continue

                    record_time_ms = (
                        detail.get("creationTime") or raw.get("creationTime")
                        or raw.get("recordTime") or raw.get("createTime")
                        or detail.get("recordTime") or detail.get("createTime")
                    )
                    if record_time_ms:
                        try:
                            recorded_at = datetime.fromtimestamp(int(record_time_ms) / 1000, tz=timezone.utc)
                        except (ValueError, TypeError):
                            recorded_at = datetime.now(timezone.utc)
                    else:
                        recorded_at = datetime.now(timezone.utc)

                    extracted_sub_calls = _extract_sub_calls(detail, raw)
                    dynamic_sub_calls = await _fetch_dynamic_class_sub_calls(str(record_id), db)
                    normalized_sub_calls = await _fetch_nls_sub_calls(request_body, app_id, str(record_id), db)
                    if not normalized_sub_calls:
                        didi_sub_calls = await _fetch_didi_sub_calls(request_body, app_id)
                        dynamic_sub_calls = _exclude_duplicate_database_sub_calls(didi_sub_calls, dynamic_sub_calls)
                        normalized_sub_calls = _merge_sub_calls(extracted_sub_calls, didi_sub_calls)
                        normalized_sub_calls = _merge_sub_calls(normalized_sub_calls, dynamic_sub_calls)

                    rec = Recording(
                        session_id=session_id,
                        application_id=application_id,
                        record_id=str(record_id),
                        request_method=request_method,
                        request_uri=request_uri,
                        request_headers=_extract_request_headers(detail),
                        request_body=request_body,
                        response_status=response_status,
                        response_body=response_body,
                        transaction_code=transaction_code,
                        scene_key=build_scene_key(transaction_code, request_method, request_uri, response_status),
                        dedupe_hash=build_dedupe_hash(transaction_code, request_method, request_uri, request_body),
                        governance_status="raw",
                        sub_calls=json.dumps(normalized_sub_calls, ensure_ascii=False),
                        recorded_at=recorded_at,
                    )
                    db.add(rec)
                    runtime_logger.info(
                        "同步会话 %s：收录 record_id=%s method=%s uri=%s transaction_code=%s",
                        session_id,
                        record_id,
                        request_method,
                        request_uri,
                        transaction_code or "-",
                    )

                await db.commit()

                current_page += 1
                if remote_total is not None and current_page * page_size >= remote_total:
                    break
                if len(records_raw) < page_size:
                    break

            # Post-processing: remove sub-invocation recordings
            # (internal HTTP calls recorded as separate Servlet entry-points)
            removed = await _remove_sub_invocation_recordings(session_id, db)
            if removed:
                logger.info("同步会话 %s：移除 %d 条子调用 Servlet 录制", session_id, removed)
                await db.commit()

            # Update session status
            sess_result = await db.execute(
                select(RecordingSession).where(RecordingSession.id == session_id)
            )
            sess = sess_result.scalar_one_or_none()
            if sess:
                count_result = await db.execute(
                    select(func.count()).select_from(Recording).where(Recording.session_id == session_id)
                )
                sess.total_count = count_result.scalar_one()
                sess.error_message = None
                if finalize_session:
                    sess.status = "done"
                    sess.end_time = datetime.now(timezone.utc)
                await db.commit()

        except ArexClientError as e:
            logger.error("同步会话 %s 失败: %s", session_id, e)
            if finalize_session:
                sess_result = await db.execute(
                    select(RecordingSession).where(RecordingSession.id == session_id)
                )
                sess = sess_result.scalar_one_or_none()
                if sess:
                    sess.status = "error"
                    sess.error_message = str(e)
                    await db.commit()
        except Exception as e:
            logger.exception("同步会话 %s 发生未预期异常: %s", session_id, e)
            if finalize_session:
                sess_result = await db.execute(
                    select(RecordingSession).where(RecordingSession.id == session_id)
                )
                sess = sess_result.scalar_one_or_none()
                if sess:
                    sess.status = "error"
                    sess.error_message = f"未预期错误: {e}"
                    await db.commit()


async def _sync_active_session_preview(session_id: int, db: AsyncSession) -> None:
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "active" or not sess.start_time:
        return

    session_start_time = _ensure_utc_datetime(sess.start_time)
    if session_start_time is None:
        return

    latest_result = await db.execute(
        select(func.max(Recording.recorded_at)).where(Recording.session_id == session_id)
    )
    latest_recorded_at = _ensure_utc_datetime(latest_result.scalar_one_or_none())
    begin_time = session_start_time
    if latest_recorded_at:
        begin_time = max(session_start_time, latest_recorded_at - _ACTIVE_PREVIEW_LOOKBACK)

    try:
        await _sync_from_arex_storage(
            session_id=session_id,
            application_id=sess.application_id,
            recording_filter_prefixes=_normalize_recording_filter_prefixes(sess.recording_filter_prefixes),
            begin_time=begin_time,
            end_time=datetime.now(timezone.utc),
            page_size=_ACTIVE_PREVIEW_PAGE_SIZE,
            page_index=0,
            finalize_session=False,
        )
    except Exception as exc:
        logger.warning("会话 %s 预览同步失败: %s", session_id, exc)


@router.get("/{session_id}/recordings", response_model=list[RecordingOut])
async def list_recordings(
    session_id: int,
    transaction_code: Optional[str] = Query(None),
    governance_status: Optional[str] = Query(None),
    duplicate_only: bool = Query(False),
    search: Optional[str] = Query(None),
    sort_by: str = Query("recorded_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    sess = await _load_session_or_404(session_id, db)
    if sess.status == "active" and skip == 0:
        await _sync_active_session_preview(session_id, db)

    stmt = select(Recording).where(Recording.session_id == session_id)
    if transaction_code:
        stmt = stmt.where(Recording.transaction_code == transaction_code)
    if governance_status:
        stmt = stmt.where(Recording.governance_status == governance_status)
    if search:
        stmt = stmt.where(
            or_(
                Recording.request_uri.contains(search),
                Recording.request_method.contains(search),
                Recording.transaction_code.contains(search),
                Recording.tags.contains(search),
            )
        )
    if duplicate_only:
        duplicate_hashes = (
            select(Recording.dedupe_hash)
            .where(Recording.dedupe_hash.is_not(None))
            .group_by(Recording.dedupe_hash)
            .having(func.count(Recording.id) > 1)
        )
        stmt = stmt.where(Recording.dedupe_hash.in_(duplicate_hashes))
    sort_mapping = {
        "recorded_at": Recording.recorded_at,
        "id": Recording.id,
    }
    primary_column = sort_mapping.get(sort_by, Recording.recorded_at)
    stmt = _apply_ordering(stmt, primary_column, Recording.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return await _serialize_recordings(db, result.scalars().all())


@router.get("/recordings/all", response_model=list[RecordingOut])
async def list_all_recordings(
    application_id: Optional[int] = Query(None),
    session_id: Optional[int] = Query(None),
    transaction_code: Optional[str] = Query(None),
    governance_status: Optional[str] = Query(None),
    duplicate_only: bool = Query(False),
    uri_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("recorded_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """List all recordings across sessions, with optional filters."""
    stmt = select(Recording)
    if application_id:
        stmt = stmt.where(Recording.application_id == application_id)
    if session_id:
        stmt = stmt.where(Recording.session_id == session_id)
    if transaction_code:
        stmt = stmt.where(Recording.transaction_code == transaction_code)
    if governance_status:
        stmt = stmt.where(Recording.governance_status == governance_status)
    if duplicate_only:
        duplicate_hashes = (
            select(Recording.dedupe_hash)
            .where(Recording.dedupe_hash.is_not(None))
            .group_by(Recording.dedupe_hash)
            .having(func.count(Recording.id) > 1)
        )
        stmt = stmt.where(Recording.dedupe_hash.in_(duplicate_hashes))
    if uri_filter:
        stmt = stmt.where(Recording.request_uri.contains(uri_filter))
    if search:
        stmt = stmt.where(
            or_(
                Recording.request_uri.contains(search),
                Recording.request_method.contains(search),
                Recording.tags.contains(search),
                Recording.transaction_code.contains(search),
            )
        )
    sort_mapping = {
        "recorded_at": Recording.recorded_at,
        "id": Recording.id,
    }
    primary_column = sort_mapping.get(sort_by, Recording.recorded_at)
    stmt = _apply_ordering(stmt, primary_column, Recording.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return await _serialize_recordings(db, result.scalars().all())


@router.get("/recordings/groups", response_model=list[RecordingGroupOut])
async def list_recording_groups(
    application_id: Optional[int] = Query(None),
    governance_status: Optional[str] = Query(None),
    transaction_code: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("latest_recorded_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(Recording)
    if application_id:
        stmt = stmt.where(Recording.application_id == application_id)
    if governance_status:
        stmt = stmt.where(Recording.governance_status == governance_status)
    if transaction_code:
        stmt = stmt.where(Recording.transaction_code == transaction_code)
    if search:
        stmt = stmt.where(
            or_(
                Recording.request_uri.contains(search),
                Recording.request_method.contains(search),
                Recording.transaction_code.contains(search),
                Recording.scene_key.contains(search),
                Recording.tags.contains(search),
            )
        )
    result = await db.execute(stmt.order_by(Recording.recorded_at.desc()))
    groups = _group_recordings(result.scalars().all())
    reverse = _normalize_sort_order(sort_order) == "desc"
    if sort_by == "transaction_code":
        groups.sort(key=lambda item: ((item.transaction_code or "").lower(), item.latest_recorded_at, item.representative_recording_id), reverse=reverse)
    elif sort_by == "scene_key":
        groups.sort(key=lambda item: ((item.scene_key or "").lower(), item.latest_recorded_at, item.representative_recording_id), reverse=reverse)
    else:
        groups.sort(key=lambda item: (item.latest_recorded_at, item.representative_recording_id), reverse=reverse)
    return groups


@router.get("/recordings/{recording_id}", response_model=RecordingOut)
async def get_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")
    return (await _serialize_recordings(db, [rec]))[0]


@router.post("/recordings/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_recordings(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    recording_ids = sorted({recording_id for recording_id in body.ids if recording_id})
    if not recording_ids:
        return BulkDeleteResponse(deleted=0)

    result = await db.execute(select(Recording).where(Recording.id.in_(recording_ids)))
    recordings = result.scalars().all()
    if not recordings:
        return BulkDeleteResponse(deleted=0)

    session_ids = [recording.session_id for recording in recordings if recording.session_id]
    await db.execute(delete(Recording).where(Recording.id.in_([recording.id for recording in recordings])))
    await _refresh_session_total_counts(db, session_ids)
    await db.commit()
    return BulkDeleteResponse(deleted=len(recordings))


@router.delete("/recordings/{recording_id}", status_code=204)
async def delete_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")

    session_id = rec.session_id
    await db.delete(rec)
    if session_id:
        await _refresh_session_total_counts(db, [session_id])
    await db.commit()


@router.patch("/recordings/{recording_id}", response_model=RecordingOut)
async def update_recording_governance(
    recording_id: int,
    body: RecordingGovernanceUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")

    if body.transaction_code is not None:
        rec.transaction_code = body.transaction_code.strip() or None
    elif not rec.transaction_code:
        app_result = await db.execute(select(Application).where(Application.id == rec.application_id))
        app = app_result.scalar_one_or_none()
        rec.transaction_code = infer_transaction_code(
            rec.request_body,
            rec.response_body,
            candidate_keys=normalize_transaction_code_keys(app.transaction_code_fields if app else None),
        )
    if body.governance_status is not None:
        rec.governance_status = normalize_governance_status(body.governance_status, rec.governance_status or "raw")

    rec.scene_key = build_scene_key(rec.transaction_code, rec.request_method, rec.request_uri, rec.response_status)
    rec.dedupe_hash = build_dedupe_hash(rec.transaction_code, rec.request_method, rec.request_uri, rec.request_body)
    await db.commit()
    await db.refresh(rec)
    return (await _serialize_recordings(db, [rec]))[0]
