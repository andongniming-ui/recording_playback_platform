"""Compare-rule parsing and failure-reason utilities for replay.

Extracted from core/replay_executor.py. These functions handle loading
compare rules from DB models, extracting ignore_fields / diff_rules /
assertions, applying header transforms, and building human-readable
failure reasons.
"""

import json
import logging
from typing import Optional

from models.compare import CompareRule
from utils.transaction_mapping import normalize_transaction_mapping_configs

logger = logging.getLogger(__name__)


def _load_json_value(raw: str | None, label: str, default):
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        logger.warning("Invalid JSON for %s", label)
        return default


def _normalize_rule_entries(value) -> list[dict]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _collect_compare_rule_effects(rule: CompareRule) -> tuple[list[str], list[dict], list[dict]]:
    config = _load_json_value(rule.config, f"compare rule {rule.id}", default=None)
    entries = _normalize_rule_entries(config)
    ignore_fields: list[str] = []
    diff_rule_entries: list[dict] = []
    assertion_entries: list[dict] = []

    for entry in entries:
        if rule.rule_type == "ignore":
            if entry.get("path"):
                normalized = dict(entry)
                normalized["type"] = normalized.get("type") or "ignore"
                diff_rule_entries.append(normalized)
            elif entry.get("key"):
                ignore_fields.append(str(entry["key"]))
            elif entry.get("field"):
                ignore_fields.append(str(entry["field"]))
        elif rule.rule_type == "assert" and entry.get("type"):
            assertion_entries.append(entry)

    return ignore_fields, diff_rule_entries, assertion_entries


def _apply_header_transforms(headers: dict, transforms) -> dict:
    if not isinstance(headers, dict):
        headers = {}
    result = {
        str(key): "" if value is None else str(value)
        for key, value in headers.items()
    }
    entries = _normalize_rule_entries(transforms)
    for entry in entries:
        transform_type = str(entry.get("type") or "replace").lower()
        key = str(entry.get("key") or "").strip()
        if not key:
            continue
        if transform_type == "remove":
            matched = next((existing for existing in result if existing.lower() == key.lower()), None)
            if matched:
                result.pop(matched, None)
            continue
        value = "" if entry.get("value") is None else str(entry.get("value"))
        matched = next((existing for existing in result if existing.lower() == key.lower()), None)
        result[matched or key] = value
    return result


def _extract_diff_paths(diff_json: str | None, limit: int = 5) -> list[str]:
    if not diff_json:
        return []
    try:
        payload = json.loads(diff_json)
    except Exception:
        return []
    paths: list[str] = []
    for change_type, items in payload.items():
        if not isinstance(items, dict):
            continue
        for raw_path in items.keys():
            normalized = (
                str(raw_path)
                .replace("root", "")
                .replace("']['", ".")
                .replace("['", ".")
                .replace("']", "")
                .replace("[", ".")
                .replace("]", "")
                .lstrip(".")
            )
            if normalized and normalized not in paths:
                paths.append(normalized)
            if len(paths) >= limit:
                return paths
    return paths


def _build_failure_reason(
    *,
    status_ok: bool,
    expected_status: Optional[int],
    actual_status: Optional[int],
    diff_ok: bool,
    diff_json: str | None,
    assertions_ok: bool,
    assertion_results: list[dict],
    perf_ok: bool,
    latency_ms: Optional[int],
    perf_threshold_ms: Optional[int],
) -> str:
    if not status_ok:
        return f"状态码不一致：期望 {expected_status}，实际 {actual_status}"
    if not diff_ok:
        diff_paths = _extract_diff_paths(diff_json)
        if diff_paths:
            return f"响应内容不一致：差异字段 {', '.join(diff_paths)}"
        return "响应内容不一致"
    if not assertions_ok:
        failed_messages = [
            str(item.get("message"))
            for item in assertion_results
            if isinstance(item, dict) and not item.get("passed", False) and item.get("message")
        ]
        if failed_messages:
            return f"断言失败：{failed_messages[0]}"
        return "断言失败"
    return f"耗时超阈值：{latency_ms}ms > {perf_threshold_ms}ms"


def _normalize_mappings(raw) -> list[dict]:
    return normalize_transaction_mapping_configs(raw)
