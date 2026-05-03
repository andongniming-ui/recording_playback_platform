"""Sub-call diff and matching utilities for replay comparison.

Extracted from core/replay_executor.py. These functions handle comparing
recorded vs replayed sub-calls: matching, scoring, deep equality, and
building per-pair diff details.
"""

import json
import logging

from utils.diff import compute_diff
from utils.sub_call_matcher import (
    normalize_sub_call_type,
    normalize_sub_call_operation,
    normalize_sub_call_value,
    unwrap_sub_call_response,
)

logger = logging.getLogger(__name__)

# HttpClient mocks during replay are served from the agent's local cache
# (cacheLoad/cacheRemove) without a storage round-trip, so the agent never
# reports their usage back. Excluding these types prevents spurious FAIL
# results when the only "missing" sub-calls are HttpClient calls.
_REPLAY_UNRELIABLE_SUB_CALL_TYPES = frozenset({"httpclient", "http"})


def _sub_call_request_signature(item: dict | None) -> str:
    if not isinstance(item, dict):
        return ""
    parts = []
    for key in ("sql", "sql_text", "params", "request", "method", "endpoint"):
        normalized = normalize_sub_call_value(item.get(key))
        if normalized:
            parts.append(f"{key}={normalized}")
    return "\n".join(parts)


def _sub_call_match_score(expected_item: dict | None, actual_item: dict | None) -> int | None:
    if not isinstance(expected_item, dict) or not isinstance(actual_item, dict):
        return None

    expected_type = normalize_sub_call_type(expected_item.get("type"))
    actual_type = normalize_sub_call_type(actual_item.get("type"))
    if expected_type != actual_type:
        return None

    expected_operation = normalize_sub_call_operation(expected_item)
    actual_operation = normalize_sub_call_operation(actual_item)
    if expected_operation and actual_operation and expected_operation != actual_operation:
        return None
    if expected_operation or actual_operation:
        base_score = 2
    else:
        base_score = 0

    expected_signature = _sub_call_request_signature(expected_item)
    actual_signature = _sub_call_request_signature(actual_item)
    if expected_signature and actual_signature:
        if expected_signature == actual_signature:
            return base_score + 3
        return base_score
    return base_score


def _to_diff_text(value) -> str | None:
    if value is None:
        return None
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _deep_equal(left, right) -> bool:
    """Recursive equality check for sub-call response values."""
    if isinstance(left, str):
        try:
            left = json.loads(left)
        except Exception:
            pass
    if isinstance(right, str):
        try:
            right = json.loads(right)
        except Exception:
            pass

    if isinstance(left, dict) and isinstance(right, dict):
        if set(left.keys()) != set(right.keys()):
            return False
        return all(_deep_equal(left[k], right[k]) for k in left)

    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False
        return all(_deep_equal(a, b) for a, b in zip(left, right))

    return left == right


def _sub_call_responses_have_diff(
    expected_response,
    actual_response,
    *,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> bool:
    expected_response = unwrap_sub_call_response(expected_response)
    actual_response = unwrap_sub_call_response(actual_response)
    if smart_noise_reduction or ignore_fields or diff_rules:
        diff_result, _ = compute_diff(
            original=_to_diff_text(expected_response),
            replayed=_to_diff_text(actual_response),
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields,
            diff_rules=diff_rules,
            ignore_order=ignore_order,
        )
        return diff_result is not None
    return not _deep_equal(expected_response, actual_response)


def _sub_call_response_diff_result(
    expected_response,
    actual_response,
    *,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> str | None:
    expected_response = unwrap_sub_call_response(expected_response)
    actual_response = unwrap_sub_call_response(actual_response)
    diff_result, _ = compute_diff(
        original=_to_diff_text(expected_response),
        replayed=_to_diff_text(actual_response),
        smart_noise_reduction=smart_noise_reduction,
        ignore_fields=ignore_fields,
        diff_rules=diff_rules,
        ignore_order=ignore_order,
    )
    return diff_result


def _sub_calls_have_diff(
    expected_json: str | None,
    actual_json: str | None,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> bool:
    """Return True if recorded vs replayed sub-calls have meaningful differences.

    Differences are: count mismatch, unmatched call (recorded-only / replayed-only),
    or response content change on a matched pair.

    Args:
        smart_noise_reduction: When True, apply built-in noise patterns (30+ dynamic
            fields like timestamps, IDs, tokens) before comparing responses.
        ignore_fields: Additional field names to exclude from response comparison.
        diff_rules: Smart diff rules (same format as main response comparison).
    """
    try:
        expected: list = json.loads(expected_json) if expected_json else []
        actual: list = json.loads(actual_json) if actual_json else []
    except Exception:
        return False

    if not isinstance(expected, list):
        expected = []
    if not isinstance(actual, list):
        actual = []

    if len(expected) != len(actual):
        return True

    unmatched = list(range(len(actual)))
    for exp_item in expected:
        if not isinstance(exp_item, dict):
            continue

        best_idx = None
        best_score = None
        for i in unmatched:
            act_item = actual[i]
            score = _sub_call_match_score(exp_item, act_item)
            if score is None:
                continue
            if best_score is None or score > best_score:
                best_idx = i
                best_score = score

        if best_idx is None:
            return True  # recorded call has no match in actual

        unmatched.remove(best_idx)
        act_item = actual[best_idx]

        if _sub_call_responses_have_diff(
            exp_item.get("response"),
            act_item.get("response"),
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields,
            diff_rules=diff_rules,
            ignore_order=ignore_order,
        ):
            return True

    if unmatched:
        return True  # extra calls only in actual

    return False


def _build_sub_call_diff_pairs(
    expected_json: str | None,
    actual_json: str | None,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> list[dict]:
    """Build per-pair comparison detail between recorded and replayed sub-calls.

    Returns a list of dicts, each representing a comparison pair:
    {
        "type": str,
        "operation": str,
        "matched": bool,          # was a matching actual call found?
        "has_diff": bool,
        "expected_response": ..., # original (None for extra actual-only calls)
        "actual_response": ...,   # replayed (None for missing calls)
        "diff_result": str|None,  # DeepDiff JSON when has_diff else None
    }
    """
    try:
        expected: list = json.loads(expected_json) if expected_json else []
        actual: list = json.loads(actual_json) if actual_json else []
    except Exception:
        return []

    if not isinstance(expected, list):
        expected = []
    if not isinstance(actual, list):
        actual = []

    pairs: list[dict] = []
    unmatched_actual = list(range(len(actual)))

    for exp_item in expected:
        if not isinstance(exp_item, dict):
            continue

        best_idx = None
        best_score = None
        for i in unmatched_actual:
            act_item = actual[i]
            score = _sub_call_match_score(exp_item, act_item)
            if score is None:
                continue
            if best_score is None or score > best_score:
                best_idx = i
                best_score = score

        if best_idx is None:
            pairs.append({
                "type": exp_item.get("type"),
                "operation": exp_item.get("operation"),
                "matched": False,
                "has_diff": True,
                "expected_response": exp_item.get("response"),
                "actual_response": None,
                "diff_result": None,
            })
            continue

        unmatched_actual.remove(best_idx)
        act_item = actual[best_idx]
        exp_resp = exp_item.get("response")
        act_resp = act_item.get("response")

        diff_result_str = _sub_call_response_diff_result(
            exp_resp,
            act_resp,
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields,
            diff_rules=diff_rules,
            ignore_order=ignore_order,
        )
        has_diff = diff_result_str is not None

        pairs.append({
            "type": exp_item.get("type"),
            "operation": exp_item.get("operation"),
            "matched": True,
            "has_diff": has_diff,
            "expected_response": unwrap_sub_call_response(exp_resp),
            "actual_response": unwrap_sub_call_response(act_resp),
            "diff_result": diff_result_str,
        })

    # Extra calls only in actual (no matching recorded call)
    for i in sorted(unmatched_actual):
        act_item = actual[i]
        if not isinstance(act_item, dict):
            continue
        pairs.append({
            "type": act_item.get("type"),
            "operation": act_item.get("operation"),
            "matched": False,
            "has_diff": True,
            "expected_response": None,
            "actual_response": act_item.get("response"),
            "diff_result": None,
        })

    return pairs


def _load_sub_call_list(value: str | None) -> list:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _count_sub_call_items(value: str | None) -> int:
    return len(_load_sub_call_list(value))


def _filter_sub_calls_for_strict_check(sub_calls_json: str | None) -> str | None:
    """Strip HttpClient-type entries before strict failure check."""
    if not sub_calls_json:
        return sub_calls_json
    try:
        items = json.loads(sub_calls_json)
    except Exception:
        return sub_calls_json
    if not isinstance(items, list):
        return sub_calls_json
    filtered = [
        item for item in items
        if not (
            isinstance(item, dict)
            and normalize_sub_call_type(item.get("type") or "").lower()
            in _REPLAY_UNRELIABLE_SUB_CALL_TYPES
        )
    ]
    return json.dumps(filtered, ensure_ascii=False) if filtered else None


def _strict_sub_call_failure(
    *,
    expected_sub_calls_json: str | None,
    actual_sub_calls_json: str | None,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> tuple[str, str] | None:
    # Strip HttpClient-type sub-calls before comparison — they are unreliable
    # to capture during replay (agent serves them from local cache without
    # reporting back), so their absence must not trigger a FAIL.
    expected = _filter_sub_calls_for_strict_check(expected_sub_calls_json)
    actual = _filter_sub_calls_for_strict_check(actual_sub_calls_json)

    expected_count = _count_sub_call_items(expected)
    actual_count = _count_sub_call_items(actual)
    if expected_count > 0 and actual_count == 0:
        return (
            "sub_call_missing",
            f"回放未抓取到子调用：录制侧 {expected_count} 条，回放侧 0 条",
        )
    if _sub_calls_have_diff(
        expected,
        actual,
        smart_noise_reduction=smart_noise_reduction,
        ignore_fields=ignore_fields,
        diff_rules=diff_rules,
        ignore_order=ignore_order,
    ):
        return ("sub_call_diff", "子调用差异")
    return None
