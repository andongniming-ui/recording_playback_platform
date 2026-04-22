import hashlib
import json
import re
from xml.etree import ElementTree as ET

GOVERNANCE_STATUSES = {"raw", "candidate", "approved", "rejected", "archived"}
SUITE_TYPES = {"smoke", "regression"}
DEFAULT_TRANSACTION_CODE_KEYS = {
    "txn_code",
    "txncode",
    "code",
    "trs_code",
    "trscode",
    "service_code",
    "servicecode",
    "biz_code",
    "bizcode",
    "transaction_id",
    "transactionid",
    "service_id",
    "serviceid",
    "transaction_code",
    "transactioncode",
    "trans_code",
    "transcode",
    "trade_code",
    "tradecode",
    "tx_code",
    "txcode",
    "rct_code",
    "rctcode",
}


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_transaction_code_keys(value) -> list[str]:
    if value in (None, "", []):
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except Exception:
            parsed = None
        if isinstance(parsed, list):
            return [
                str(item).strip().replace("-", "_").lower()
                for item in parsed
                if str(item).strip()
            ]
        return [
            part.strip().replace("-", "_").lower()
            for part in re.split(r"[\n,，;；]+", value)
            if part.strip()
        ]
    if isinstance(value, (list, tuple, set)):
        return [
            str(item).strip().replace("-", "_").lower()
            for item in value
            if str(item).strip()
        ]
    return []


def _resolve_transaction_code_keys(candidate_keys=None) -> set[str]:
    normalized = normalize_transaction_code_keys(candidate_keys)
    return set(normalized) if normalized else set(DEFAULT_TRANSACTION_CODE_KEYS)


def _search_json_for_transaction_code(value, candidate_keys: set[str]) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = str(key).replace("-", "_").lower()
            if normalized_key in candidate_keys:
                text = _normalize_text(item)
                if text:
                    return text
            nested = _search_json_for_transaction_code(item, candidate_keys)
            if nested:
                return nested
    elif isinstance(value, list):
        for item in value:
            nested = _search_json_for_transaction_code(item, candidate_keys)
            if nested:
                return nested
    return None


def _search_xml_for_transaction_code(text: str, candidate_keys: set[str]) -> str | None:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None

    for element in root.iter():
        tag = element.tag.split("}", 1)[-1].replace("-", "_").lower()
        if tag in candidate_keys:
            value = _normalize_text(element.text)
            if value:
                return value
    return None


def infer_transaction_code(*values: str | None, candidate_keys=None) -> str | None:
    resolved_keys = _resolve_transaction_code_keys(candidate_keys)
    for raw in values:
        text = _normalize_text(raw)
        if not text:
            continue
        xml_value = _search_xml_for_transaction_code(text, resolved_keys)
        if xml_value:
            return xml_value
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = None
        if parsed is not None:
            json_value = _search_json_for_transaction_code(parsed, resolved_keys)
            if json_value:
                return json_value
    return None


def normalize_governance_status(value: str | None, default: str) -> str:
    status = (value or default).strip().lower()
    if status not in GOVERNANCE_STATUSES:
        return default
    return status


def normalize_suite_type(value: str | None, default: str = "regression") -> str:
    suite_type = (value or default).strip().lower()
    if suite_type not in SUITE_TYPES:
        return default
    return suite_type


def build_scene_key(
    transaction_code: str | None,
    request_method: str | None,
    request_uri: str | None,
    response_status: int | None,
) -> str:
    status_bucket = "success" if response_status and 200 <= response_status < 400 else "non_success"
    return "|".join(
        [
            transaction_code or "unknown_tx",
            (request_method or "GET").upper(),
            request_uri or "/",
            status_bucket,
        ]
    )


def _normalize_request_body(value: str | None) -> str:
    text = _normalize_text(value) or ""
    if not text:
        return ""
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except Exception:
        return re.sub(r">\s+<", "><", text)


def build_dedupe_hash(
    transaction_code: str | None,
    request_method: str | None,
    request_uri: str | None,
    request_body: str | None,
) -> str:
    payload = "||".join(
        [
            transaction_code or "unknown_tx",
            (request_method or "GET").upper(),
            request_uri or "/",
            _normalize_request_body(request_body),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
