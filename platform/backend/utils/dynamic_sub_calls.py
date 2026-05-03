"""Generic AREX DynamicClass sub-call extraction."""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.arex_mocker import ArexMocker
from utils.repository_capture import (
    is_noise_dynamic_mocker,
    normalize_generic_database_sub_call,
    normalize_repository_sub_call,
)
from utils.sub_call_parser import _filter_noise_sub_calls, _is_noise_sub_call


async def fetch_dynamic_class_sub_calls(record_id: str, db: AsyncSession) -> list[dict]:
    """Collect DynamicClass sub-calls from arex_mocker and normalize to sub_call format."""
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


_fetch_dynamic_class_sub_calls = fetch_dynamic_class_sub_calls
