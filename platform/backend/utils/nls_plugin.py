"""NLS (bank) system plugin — encapsulates NLS-specific sub-call logic.

Replaces the old utils/nls_sub_calls.py. The NLS system has a bank_sub_call_log
table that records business steps, which the platform correlates with
AREX mocker data to reconstruct full sub-call trees.
"""

import json
import logging
import re
from typing import Any

from config import settings
from models.arex_mocker import ArexMocker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.repository_capture import (
    is_noise_dynamic_mocker,
    normalize_generic_database_sub_call,
    normalize_repository_sub_call,
)
from utils.sub_call_parser import _filter_noise_sub_calls, _is_noise_sub_call
from utils.system_plugin import SystemPlugin, register_plugin

logger = logging.getLogger(__name__)

# ── NLS-specific constants ─────────────────────────────────────────────────

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

_JDBC_METHOD_PARAM_KEY: dict[str, str] = {
    "findAccountByNo": "account_no",
    "findPrimaryAccountByCustomerNo": "customer_no",
    "findLoanByNo": "loan_no",
    "findRecentStatements": "account_no",
    "findRecentTransactionsByAccountNo": "account_no",
}

_NLS_XML_FIELDS = (
    "account_no", "loan_no", "amount", "repayment_amount",
    "withdraw_amount", "customer_no", "id_no", "transaction_id",
)


# ── NlsPlugin class ────────────────────────────────────────────────────────

class NlsPlugin(SystemPlugin):
    """Plugin for the NLS (bank) system."""

    @property
    def system_name(self) -> str:
        return "nls"

    async def fetch_extra_sub_calls(
        self,
        request_body: str | None,
        app_id: str,
        record_id: str | None,
        db: Any,
    ) -> list[dict]:
        return await _fetch_nls_sub_calls(request_body, app_id, record_id, db)

    def extract_xml_params(self, request_body: str | None) -> dict[str, str]:
        return _extract_nls_xml_params(request_body)

    def get_jdbc_method_table(self) -> dict[str, str]:
        return dict(_JDBC_METHOD_TABLE)

    def get_jdbc_method_param_key(self) -> dict[str, str]:
        return dict(_JDBC_METHOD_PARAM_KEY)

    def assign_jdbc_to_step(self, method_name: str, step_names: list[str]) -> str | None:
        return _assign_jdbc_to_step(method_name, step_names)


# ── Internal helpers ───────────────────────────────────────────────────────

def _extract_nls_xml_params(request_body: str | None) -> dict[str, str]:
    """Extract common field values from HTTP request XML body."""
    params: dict[str, str] = {}
    if not request_body:
        return params
    for field in _NLS_XML_FIELDS:
        m = re.search(rf"<{field}>([^<]+)</{field}>", request_body)
        if m:
            params[field] = m.group(1).strip()
    return params


def _assign_jdbc_to_step(method_name: str, step_names: list[str]) -> str | None:
    """Map a BankJdbcRepository method to its business step name."""
    n = method_name.lower()
    if "customer" in n:
        return next((s for s in step_names if "customer" in s.lower()), None)
    if "account" in n or "primaryaccount" in n:
        return next((s for s in step_names if "account" in s.lower()), None)
    if "loan" in n:
        return next((s for s in step_names if "loan" in s.lower()), None)
    last_db = next((s for s in reversed(step_names) if s not in ("risk-check",)), None)
    return last_db


# ── DynamicClass sub-call fetching (shared across systems, kept here) ──────

async def fetch_dynamic_class_sub_calls(record_id: str, db: AsyncSession) -> list[dict]:
    """Collect DynamicClass sub-calls from arex_mocker and normalise to sub_call format."""
    result = await db.execute(
        select(ArexMocker).where(
            ArexMocker.record_id == record_id,
            ArexMocker.is_entry_point.is_(False),
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
        generic_database_sub_call = normalize_generic_database_sub_call(mocker, m.category_name)
        if generic_database_sub_call is not None:
            sub_calls.append(generic_database_sub_call)
            continue
        target_req = mocker.get("targetRequest") or {}
        target_resp = mocker.get("targetResponse") or {}
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

        cat = (m.category_name or "").lower()
        if "http" in cat:
            req_attrs = target_req.get("attributes") or {}
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


# ── Internal: fetch NLS sub-calls from bank database ───────────────────────

async def _fetch_nls_sub_calls(
    request_body: str | None,
    app_id: str,
    record_id: str | None = None,
    db: AsyncSession | None = None,
) -> list[dict]:
    """Reconstruct N-L-S business-step sub-calls from bank_sub_call_log."""
    if not request_body or not settings.nls_mysql_host:
        return []

    m = re.search(r"<SYS_EVT_TRACE_ID>([^<]+)</SYS_EVT_TRACE_ID>", request_body)
    if not m:
        return []
    trace_id = m.group(1).strip()

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
        xml_params = _extract_nls_xml_params(request_body)
        last_db_step = next((s[0] for s in reversed(steps) if s[1] == "db"), None)

        # ── 1. 从 arex_mocker 取 BankJdbcRepository READ 调用 ──────────
        step_children: dict[str, list[dict]] = {name: [] for name in step_names}
        step_read_resp: dict[str, object] = {}

        if record_id and db is not None:
            result = await db.execute(
                select(ArexMocker).where(
                    ArexMocker.record_id == record_id,
                    ArexMocker.is_entry_point.is_(False),
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
                    if method_name != "countSubCalls" and target not in step_read_resp:
                        step_read_resp[target] = resp_body

        # ── 2. 从 NLS MySQL 查写入数据 ──────────────────────────────────
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
            logger.debug("[nls_plugin] 写入数据查询失败: %s", e)

        # ── 3. 构建父步骤 ──────────────────────────────────────────────
        step_req_param: dict[str, object] = {}
        for step in steps:
            sname = step[0]
            n = sname.lower()
            if "account" in n:
                step_req_param[sname] = xml_params.get("account_no")
            elif "loan" in n:
                loan_no = xml_params.get("loan_no")
                if not loan_no:
                    kids = step_children.get(sname, [])
                    loan_resp = kids[0].get("response") if kids else None
                    if isinstance(loan_resp, dict):
                        loan_no = loan_resp.get("loan_no")
                step_req_param[sname] = loan_no
            elif "customer" in n:
                kids = step_children.get(sname, [])
                cust_resp = kids[0].get("response") if kids else None
                if isinstance(cust_resp, dict):
                    step_req_param[sname] = cust_resp.get("customer_no") or cust_resp.get("id_no")
                else:
                    step_req_param[sname] = xml_params.get("customer_no") or xml_params.get("id_no")
            elif sname == last_db_step:
                amt = xml_params.get("repayment_amount") or xml_params.get("withdraw_amount") or xml_params.get("amount")
                if amt:
                    step_req_param[sname] = {
                        k: xml_params[k] for k in ("account_no", "loan_no",
                                                    "repayment_amount", "withdraw_amount")
                        if xml_params.get(k)
                    }

        sub_calls = []
        for step_name, layer_name, detail_text, duration_ms, result_status in steps:
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
        logger.warning("[nls_plugin] 查询 %s trace=%s 失败: %s", app_id, trace_id, e)
        return []


# ── Auto-register ──────────────────────────────────────────────────────────

register_plugin(NlsPlugin())
