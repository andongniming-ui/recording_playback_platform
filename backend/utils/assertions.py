"""
Assertion evaluation for replay results.

assertions format (list of dicts):
  {"type": "status_code_eq",      "value": 200}
  {"type": "response_not_empty"}
  {"type": "json_path_eq",        "path": "code",        "value": 0}
  {"type": "json_path_contains",  "path": "message",     "value": "success"}
  {"type": "json_path_exists",    "path": "data.id"}
  {"type": "json_path_regex",     "path": "data.time",   "pattern": "\\d{4}-\\d{2}-\\d{2}"}
  {"type": "diff_score_lte",      "value": 0.1}

Path syntax: dot-separated keys, e.g. "code", "data.id", "items.0.name"
"""
import re
import json


def evaluate_assertions(
    assertions: list[dict] | None,
    replayed_body: str | None,
    status_code: int | None,
    diff_score: float | None,
) -> list[dict]:
    """
    Evaluate all assertions and return a list of results:
    [{"type": ..., "passed": bool, "message": str}, ...]
    """
    if not assertions:
        return []

    results = []
    parsed_body = _parse_json(replayed_body)

    for assertion in assertions:
        atype = assertion.get("type", "")
        try:
            result = _evaluate_one(assertion, atype, replayed_body, parsed_body, status_code, diff_score)
        except Exception as e:
            result = {"type": atype, "passed": False, "message": f"评估异常: {e}"}
        results.append(result)

    return results


def assertions_all_passed(assertion_results: list[dict] | None) -> bool:
    """Returns True if all assertions passed (or there are no assertions)."""
    if not assertion_results:
        return True
    return all(r.get("passed", False) for r in assertion_results)


def _evaluate_one(
    assertion: dict,
    atype: str,
    raw_body: str | None,
    parsed_body,
    status_code: int | None,
    diff_score: float | None,
) -> dict:
    if atype == "status_code_eq":
        expected = _coerce_value(assertion.get("value"))
        passed = status_code == expected
        return {
            "type": atype,
            "passed": passed,
            "message": f"HTTP状态码 {status_code} {'==' if passed else '!='} {expected}",
        }

    elif atype == "response_not_empty":
        passed = bool(raw_body and raw_body.strip())
        return {
            "type": atype,
            "passed": passed,
            "message": "响应体不为空" if passed else "响应体为空",
        }

    elif atype == "json_path_eq":
        path = assertion.get("path", "")
        expected = _coerce_value(assertion.get("value"))
        actual = _get_path(parsed_body, path)
        passed = actual == expected
        return {
            "type": atype,
            "passed": passed,
            "message": f"$.{path} = {json.dumps(actual, ensure_ascii=False)} {'==' if passed else '!='} {json.dumps(expected, ensure_ascii=False)}",
        }

    elif atype == "json_path_contains":
        path = assertion.get("path", "")
        expected = str(assertion.get("value", ""))
        actual = _get_path(parsed_body, path)
        actual_str = str(actual) if actual is not None else ""
        passed = expected in actual_str
        return {
            "type": atype,
            "passed": passed,
            "message": f"$.{path} {'包含' if passed else '不包含'} \"{expected}\"",
        }

    elif atype == "json_path_exists":
        path = assertion.get("path", "")
        passed = _path_exists(parsed_body, path)
        return {
            "type": atype,
            "passed": passed,
            "message": f"$.{path} {'存在' if passed else '不存在'}",
        }

    elif atype == "json_path_regex":
        path = assertion.get("path", "")
        pattern = assertion.get("pattern", ".*")
        actual = _get_path(parsed_body, path)
        actual_str = str(actual) if actual is not None else ""
        try:
            passed = bool(re.search(pattern, actual_str))
        except re.error:
            passed = False
        return {
            "type": atype,
            "passed": passed,
            "message": f"$.{path} = \"{actual_str[:60]}\" {'匹配' if passed else '不匹配'} /{pattern}/",
        }

    elif atype == "diff_score_lte":
        threshold = float(assertion.get("value", 0.0))
        actual_score = diff_score if diff_score is not None else 1.0
        passed = actual_score <= threshold
        return {
            "type": atype,
            "passed": passed,
            "message": f"差异分数 {actual_score:.4f} {'<=' if passed else '>'} {threshold}",
        }

    else:
        return {"type": atype, "passed": False, "message": f"未知断言类型: {atype}"}


_MISSING = object()  # sentinel distinct from None


def _get_path(obj, path: str):
    """Navigate a dot-separated path; returns None for missing OR null values."""
    val = _get_path_sentinel(obj, path)
    return None if val is _MISSING else val


def _path_exists(obj, path: str) -> bool:
    """Returns True even when the field value is explicitly null (JSON null)."""
    return _get_path_sentinel(obj, path) is not _MISSING


def _get_path_sentinel(obj, path: str):
    """Navigate path; returns _MISSING when key is absent, None when value is null."""
    if obj is None:
        return _MISSING
    parts = [p for p in path.strip("$. ").split(".") if p]
    current = obj
    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return _MISSING
            current = current[part]
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            if idx >= len(current):
                return _MISSING
            current = current[idx]
        else:
            return _MISSING
    return current


def _coerce_value(value):
    """
    Coerce a value that may have been stringified by the frontend.
    e.g. "200" → 200, "0.5" → 0.5, "true" → True, "null" → None.
    Non-numeric strings are returned as-is.
    """
    if not isinstance(value, str):
        return value
    # Try JSON parsing: handles integers, floats, booleans, null
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value


def _parse_json(text: str | None):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None
