"""Didi system plugin — encapsulates didi-specific sub-call logic.

Replaces the old utils/didi_sub_calls.py. The didi system has JdbcTemplate-based
database access, so the platform needs to reconstruct sub-calls by querying the
SUT database directly.
"""

import json
import logging
import re
from typing import Any

from config import settings
from utils.governance import infer_transaction_code
from utils.sub_call_merge import exclude_duplicate_database_sub_calls, merge_sub_calls
from utils.system_plugin import SystemPlugin, register_plugin

logger = logging.getLogger(__name__)

# ── Didi-specific constants ────────────────────────────────────────────────

_DIDI_COMPLEX_TRANSACTION_CODES: set[str] = {f"car{index:06d}" for index in range(1, 16)}

_APP_DB_ENV: dict[str, str] = {
    "didi-car-sat": "sat",
    "didi-system-a": "sat",
    "didi-car-uat": "uat",
    "didi-system-b": "uat",
}


def _get_app_db_name(app_id: str | None) -> str:
    env = _APP_DB_ENV.get((app_id or "").strip().lower())
    if env == "sat":
        return settings.didi_mysql_db_sat
    if env == "uat":
        return settings.didi_mysql_db_uat
    return ""

# XML fields to extract from didi request bodies
_DIDI_XML_FIELDS = (
    "code", "trs_code", "service_code", "biz_code", "request_no",
    "customer_no", "plate_no", "vin", "policy_no", "claim_no",
    "garage_code", "city", "tra_id", "traId",
)

# Repository capture specs for didi system
_DIDI_REPOSITORY_SPECS: list[dict] = [
    {
        "full_class_name": "com.arex.demo.didi.common.repository.CarDataRepository",
        "database": "mysql",
        "type": "MySQL",
        "methods": [
            {
                "method_name": "findVehicle",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["plateNo", "vin"],
                "table": "car_vehicle",
                "operation": "SELECT car_vehicle",
                "status": "READ",
            },
            {
                "method_name": "findCustomer",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerNo"],
                "table": "car_customer",
                "operation": "SELECT car_customer",
                "status": "READ",
            },
            {
                "method_name": "findPolicy",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["policyNo", "plateNo"],
                "table": "car_policy",
                "operation": "SELECT car_policy",
                "status": "READ",
            },
            {
                "method_name": "findClaim",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["claimNo", "plateNo"],
                "table": "car_claim",
                "operation": "SELECT car_claim",
                "status": "READ",
            },
            {
                "method_name": "findDispatch",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["plateNo", "garageCode"],
                "table": "car_dispatch",
                "operation": "SELECT car_dispatch",
                "status": "READ",
            },
            {
                "method_name": "saveAudit",
                "parameter_types": "java.lang.String@java.lang.String@java.lang.String@java.lang.String@java.lang.String@java.math.BigDecimal@java.lang.String",
                "key_formula": "#p1",
                "parameter_names": [
                    "txnCode", "requestNo", "customerNo", "plateNo",
                    "riskLevel", "quotedAmount", "variantId",
                ],
                "table": "car_order_audit",
                "operation": "INSERT car_order_audit",
                "status": "WRITE",
            },
            {
                "method_name": "updateVehicleStatus",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["plateNo", "status"],
                "table": "car_vehicle",
                "operation": "UPDATE car_vehicle",
                "status": "WRITE",
            },
        ],
    },
]


# ── Shared utility functions (kept for reuse by other plugins) ──────────────

def _legacy_exclude_duplicate_database_sub_calls(
    preferred: list[dict] | None,
    candidates: list[dict] | None,
) -> list[dict]:
    """Remove database sub-calls from candidates that already exist in preferred."""
    identities = {
        identity
        for identity in (_legacy_database_sub_call_identity(item) for item in (preferred or []))
        if identity is not None
    }
    if not identities:
        return candidates or []
    filtered: list[dict] = []
    for item in candidates or []:
        identity = _legacy_database_sub_call_identity(item)
        if identity is not None and identity in identities:
            continue
        filtered.append(item)
    return filtered


def _legacy_database_sub_call_identity(item: dict | None) -> tuple[str, str, str] | None:
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


# ── DidiPlugin class ───────────────────────────────────────────────────────

class DidiPlugin(SystemPlugin):
    """Plugin for the didi (car) system."""

    @property
    def system_name(self) -> str:
        return "didi"

    def match_app_id(self, app_id: str) -> bool:
        normalized = (app_id or "").strip().lower()
        return normalized in _APP_DB_ENV or normalized.startswith("didi-")

    async def fetch_extra_sub_calls(
        self,
        request_body: str | None,
        app_id: str,
        record_id: str | None,
        db: Any,
    ) -> list[dict]:
        db_name = _get_app_db_name(app_id)
        if not request_body or not settings.didi_mysql_host or not db_name:
            return []

        txn_code = infer_transaction_code(request_body)
        if txn_code not in _DIDI_COMPLEX_TRANSACTION_CODES:
            return []

        params = self.extract_xml_params(request_body)
        return await _fetch_didi_db_sub_calls(request_body, app_id, db_name, txn_code, params)

    def is_complex_transaction(self, txn_code: str) -> bool:
        return txn_code in _DIDI_COMPLEX_TRANSACTION_CODES

    def get_complex_transaction_codes(self) -> set[str]:
        return set(_DIDI_COMPLEX_TRANSACTION_CODES)

    def should_fetch_sibling_http_sub_calls(
        self,
        request_body: str | None,
        correlation_tokens: set[str],
    ) -> bool:
        txn_code = infer_transaction_code(request_body) if request_body else None
        return bool(correlation_tokens) or self.is_complex_transaction(txn_code or "")

    def matches_sibling_http_sub_call(
        self,
        *,
        endpoint: str,
        query_params: dict[str, str],
        request_body: str | None,
        correlation_text: str,
        correlation_tokens: set[str],
    ) -> bool:
        if not str(endpoint or "").startswith("/internal/didi/"):
            return super().matches_sibling_http_sub_call(
                endpoint=endpoint,
                query_params=query_params,
                request_body=request_body,
                correlation_text=correlation_text,
                correlation_tokens=correlation_tokens,
            )

        txn_code = infer_transaction_code(request_body) if request_body else None
        if not self.is_complex_transaction(txn_code or ""):
            return False

        row_txn_code = query_params.get("txnCode") or query_params.get("txn_code")
        row_tra_id = query_params.get("traId") or query_params.get("tra_id")
        request_params = self.extract_xml_params(request_body)
        tra_id = request_params.get("tra_id") or request_params.get("traId")
        if txn_code and row_txn_code != txn_code:
            return False
        if tra_id and row_tra_id != tra_id:
            return False
        return True

    def extract_xml_params(self, request_body: str | None) -> dict[str, str]:
        params: dict[str, str] = {}
        if not request_body:
            return params
        for field in _DIDI_XML_FIELDS:
            m = re.search(rf"<{field}>([^<]+)</{field}>", request_body)
            if m:
                params[field] = m.group(1).strip()
        return params

    def get_repository_specs(self) -> list[dict]:
        return _DIDI_REPOSITORY_SPECS


# ── Internal: fetch sub-calls from didi database ───────────────────────────

async def _fetch_didi_db_sub_calls(
    request_body: str | None,
    app_id: str,
    db_name: str,
    txn_code: str,
    params: dict[str, str],
) -> list[dict]:
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
            charset="utf8",
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
        logger.warning("[didi_plugin] 查询 %s 失败: %s", app_id, exc)
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


# ── Auto-register ──────────────────────────────────────────────────────────

register_plugin(DidiPlugin())
