"""
Failure Analyzer for Replay Results

Classifies replay failures into categories:
- ENVIRONMENT: Network timeout, connection refused, service unavailable (502/503)
- DATA_ISSUE: Dynamic fields like timestamps, IDs, tokens that vary between runs
- BUG: Actual code bugs - status code errors, business logic field changes
- PERFORMANCE: Response time exceeded threshold
- UNKNOWN: Cannot determine automatically
"""

import json
import re
from typing import Optional


# Error patterns indicating environment issues
ENVIRONMENT_ERROR_PATTERNS = [
    r"timeout",
    r"connection refused",
    r"connection reset",
    r"connection closed",
    r"502",
    r"503",
    r"504",
    r"network",
    r"unreachable",
    r"dns",
    r"ECONNREFUSED",
    r"ETIMEDOUT",
    r"ENOTFOUND",
    r"service unavailable",
    r"bad gateway",
    r"gateway timeout",
]

# Common dynamic fields that often cause false positives
DYNAMIC_FIELD_PATTERNS = [
    r"timestamp",
    r"requestId",
    r"request_id",
    r"traceId",
    r"trace_id",
    r"id",
    r"_id",
    r"\.id$",
    r"token",
    r"session",
    r"uuid",
    r"createdAt",
    r"created_at",
    r"updatedAt",
    r"updated_at",
    r"expired",
    r"expires",
    r"ttl",
    r"random",
    r"salt",
    r"nonce",
    r"signature",
]

# Critical business fields that indicate real bugs when changed
CRITICAL_FIELD_PATTERNS = [
    r"price",
    r"amount",
    r"total",
    r"balance",
    r"status",
    r"code",
    r"error",
    r"message",
    r"result",
    r"data\.",
    r"\.data$",
    r"success",
    r"failed",
    r"permission",
    r"auth",
    r"role",
    r"access",
]


def _matches_any_pattern(text: str, patterns: list[str]) -> bool:
    """Check if text matches any of the given patterns."""
    if not text:
        return False
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False


def _analyze_diff_fields(diff_json_str: Optional[str], ignore_fields: list[str]) -> dict:
    """
    Analyze diff_json to extract field-level information.
    Returns dict with: all_fields, critical_fields, dynamic_fields, ignore_candidate_fields
    """
    result = {
        "all_fields": [],
        "critical_fields": [],
        "dynamic_fields": [],
        "ignore_candidate_fields": [],
    }

    if not diff_json_str:
        return result

    try:
        diff_data = json.loads(diff_json_str)
    except (json.JSONDecodeError, TypeError):
        return result

    # Collect all changed fields from all diff types
    all_changed_paths = set()

    for change_type, changes in diff_data.items():
        if isinstance(changes, dict):
            for field_path in changes.keys():
                all_changed_paths.add(field_path)
                result["all_fields"].append(field_path)

                # Check if it's a dynamic field
                if _matches_any_pattern(field_path, DYNAMIC_FIELD_PATTERNS):
                    result["dynamic_fields"].append(field_path)
                    result["ignore_candidate_fields"].append(field_path)

                # Check if it's a critical field
                if _matches_any_pattern(field_path, CRITICAL_FIELD_PATTERNS):
                    result["critical_fields"].append(field_path)

    return result


def _analyze_assertions(assertion_results: Optional[list]) -> dict:
    """
    Analyze assertion results to determine failure type.
    """
    if not assertion_results:
        return {"perf_failed": False, "assertion_failed": False, "failed_types": []}

    perf_failed = False
    assertion_failed = False
    failed_types = []

    for ar in assertion_results:
        if not isinstance(ar, dict):
            continue

        passed = ar.get("passed", True)
        ar_type = ar.get("type", "")

        if not passed:
            if ar_type == "perf_threshold":
                perf_failed = True
            else:
                assertion_failed = True

            if ar_type not in failed_types:
                failed_types.append(ar_type)

    return {
        "perf_failed": perf_failed,
        "assertion_failed": assertion_failed,
        "failed_types": failed_types,
    }


def analyze_failure(
    error_message: Optional[str],
    diff_json: Optional[str],
    diff_score: Optional[float],
    replayed_status_code: Optional[int],
    assertion_results: Optional[list],
    ignore_fields: Optional[list[str]] = None,
) -> tuple[str, str]:
    """
    Main function to classify a replay failure.

    Returns:
        tuple: (category, reason)

    Categories:
        - ENVIRONMENT: Network/connection/service issues
        - DATA_ISSUE: Dynamic fields that should be ignored
        - BUG: Actual code bugs
        - PERFORMANCE: Response time exceeded threshold
        - UNKNOWN: Cannot determine
    """
    ignore_fields = ignore_fields or []

    # Step 1: Check for environment errors (ERROR status)
    if error_message and _matches_any_pattern(error_message, ENVIRONMENT_ERROR_PATTERNS):
        reason = f"环境/网络问题: {error_message[:100]}"
        return "ENVIRONMENT", reason

    # Step 2: Check for HTTP status code errors
    if replayed_status_code:
        if replayed_status_code >= 500:
            return "ENVIRONMENT", f"服务器错误: HTTP {replayed_status_code}"
        elif replayed_status_code >= 400:
            return "BUG", f"客户端错误: HTTP {replayed_status_code}"

    # Step 3: Analyze assertions (especially performance)
    assertion_analysis = _analyze_assertions(assertion_results)
    if assertion_analysis["perf_failed"]:
        for ar in assertion_results or []:
            if ar.get("type") == "perf_threshold" and not ar.get("passed"):
                return "PERFORMANCE", ar.get("message", "性能超标")

    # Step 4: Analyze diff fields
    diff_analysis = _analyze_diff_fields(diff_json, ignore_fields)

    # Check if ALL changed fields are in ignore list or are dynamic
    all_changed = set(diff_analysis["all_fields"])
    dynamic_changed = set(diff_analysis["dynamic_fields"])

    # User-defined ignore fields (from job config)
    user_ignored = set(ignore_fields)

    # Fields that are either dynamic or user-ignored
    safe_to_ignore = dynamic_changed | user_ignored

    # If diff score is very low and only safe fields changed
    if diff_score is not None:
        if diff_score < 0.1 and all_changed.issubset(safe_to_ignore):
            return "DATA_ISSUE", f"仅动态字段变化: {', '.join(list(all_changed)[:5])}"

        # Medium diff score with mostly dynamic fields
        if diff_score < 0.3 and len(dynamic_changed) > len(all_changed) / 2:
            return "DATA_ISSUE", f"主要是动态字段变化: {', '.join(list(dynamic_changed)[:5])}"

    # Step 5: Check for critical field changes
    critical_changed = set(diff_analysis["critical_fields"])
    if critical_changed:
        return "BUG", f"核心业务字段变化: {', '.join(list(critical_changed)[:5])}"

    # Step 6: Assertion failures (non-performance) indicate bugs
    if assertion_analysis["assertion_failed"]:
        return "BUG", f"断言失败: {', '.join(assertion_analysis['failed_types'])}"

    # Step 7: If there's a diff but we can't categorize, it's likely a bug
    if diff_score is not None and diff_score > 0:
        return "BUG", f"存在差异 (score={diff_score:.3f})"

    # Default: unknown
    return "UNKNOWN", "无法自动判定，请人工检查"


def get_failure_category_stats(results: list) -> dict:
    """
    Aggregate failure statistics from a list of replay results.

    Args:
        results: List of dicts with keys: status, failure_category, error_message, diff_score, etc.

    Returns:
        dict with category counts and percentages
    """
    stats = {
        "ENVIRONMENT": {"count": 0, "percentage": 0.0},
        "DATA_ISSUE": {"count": 0, "percentage": 0.0},
        "BUG": {"count": 0, "percentage": 0.0},
        "PERFORMANCE": {"count": 0, "percentage": 0.0},
        "UNKNOWN": {"count": 0, "percentage": 0.0},
    }

    total_failures = 0

    for r in results:
        # Only count FAIL and ERROR statuses
        status = r.get("status", "")
        if status not in ("FAIL", "ERROR"):
            continue

        total_failures += 1
        category = r.get("failure_category", "UNKNOWN")
        if category not in stats:
            category = "UNKNOWN"
        stats[category]["count"] += 1

    # Calculate percentages
    if total_failures > 0:
        for cat in stats:
            stats[cat]["percentage"] = round(stats[cat]["count"] / total_failures * 100, 1)

    stats["total_failures"] = total_failures
    return stats
