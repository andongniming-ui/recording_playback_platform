"""
Result comparison using deepdiff, with optional Smart Diff Rules.

diff_rules format (list of dicts):
  {"type": "ignore",            "path": "data.timestamp"}
  {"type": "numeric_tolerance", "path": "data.price",   "tolerance": 0.01}
  {"type": "regex_match",       "path": "data.message", "pattern": ".*success.*"}
  {"type": "type_only",         "path": "data.id"}

Path syntax: dot-separated keys, e.g. "data.price", "items.*.total"
Use "*" as a wildcard to match all list/dict children.
"""
import re
import copy
import json
from deepdiff import DeepDiff


# P0: 内置智能降噪规则 - 30+ 常见动态字段自动忽略
# 当用户启用 smart_noise_reduction 时自动应用这些规则
BUILTIN_SMART_NOISE_PATTERNS = [
    # 时间相关
    r"timestamp", r"timestampMs", r"time", r"timeStamp", r"date", r"datetime",
    r"createdAt", r"created_at", r"updatedAt", r"updated_at", r"deletedAt", r"deleted_at",
    r"expireTime", r"expire_time", r"expired", r"expires", r"expireDate",
    # ID/序列号相关
    r"requestId", r"request_id", r"traceId", r"trace_id", r"spanId", r"span_id",
    r"^id$", r"^uuid$", r"serialNo", r"serial_no", r"^orderNo$", r"^order_no$",
    # Token/Session 相关
    r"token", r"session", r"sessionId", r"session_id", r"auth", r"authToken",
    r"accessToken", r"access_token", r"refreshToken", r"refresh_token", r"jwt",
    # 随机数/盐值
    r"random", r"rand", r"salt", r"nonce", r"signature", r"sign",
    # 缓存相关
    r"ttl", r"ttlSeconds", r"cacheTime", r"cache_time", r"lastUpdate", r"last_update",
    # 浮点数精度
    r"lat", r"lng", r"longitude", r"latitude", r"\.lat$", r"\.lng$",
    # 内存地址/对象标识
    r"ptr", r"pointer", r"address", r"memory",
    # 版本号（允许小版本差异）
    r"version", r"\.v$", r"build",
    # 统计类（允许小幅波动）
    r"count", r"totalCount", r"total_count", r"viewCount", r"view_count",
    # 毫秒时间戳
    r"ms$", r"Unix", r"epoch",
]


def get_builtin_noise_ignore_rules() -> list[str]:
    """
    获取内置智能降噪规则的字段列表。
    返回的是用于 DeepDiff exclude_regex_paths 的正则表达式列表。
    """
    return BUILTIN_SMART_NOISE_PATTERNS


def compute_diff(
    original: str | None,
    replayed: str | None,
    ignore_paths: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    smart_noise_reduction: bool = False,
    *,
    ignore_fields: list[str] | None = None,
    ignore_order: bool = True,
) -> tuple[str | None, float]:
    """
    Compare original and replayed response strings.
    Returns (diff_json, diff_score) where diff_score 0.0=identical, 1.0=totally different.

    Args:
        original: 录制时的原始响应
        replayed: 回放时的响应
        ignore_paths: 用户自定义忽略字段列表
        diff_rules: 智能差异规则
        smart_noise_reduction: 是否启用内置智能降噪规则（自动忽略30+常见动态字段）
        ignore_order: 是否忽略 JSON 数组顺序
    """
    if original is None and replayed is None:
        return None, 0.0

    orig_obj = _parse(original)
    repl_obj = _parse(replayed)

    # Support both `ignore_paths` (internal regex list) and `ignore_fields`
    # (user-facing field-name list, auto-converted to regex patterns).
    combined_paths = list(ignore_paths or [])
    if ignore_fields:
        combined_paths.extend([rf".*\['{f}'\].*" for f in ignore_fields])
    exclude_regex = combined_paths

    # P0: 启用内置智能降噪规则
    if smart_noise_reduction:
        # 将模式列表转换为 DeepDiff 的 exclude_regex_paths 格式
        builtin_excludes = _convert_patterns_to_deepdiff_regex(BUILTIN_SMART_NOISE_PATTERNS)
        exclude_regex.extend(builtin_excludes)

    # Apply Smart Diff Rules
    if diff_rules:
        orig_obj, repl_obj, extra_excludes = _apply_diff_rules(orig_obj, repl_obj, diff_rules)
        exclude_regex.extend(extra_excludes)

    try:
        diff = DeepDiff(
            orig_obj,
            repl_obj,
            ignore_order=ignore_order,
            exclude_regex_paths=exclude_regex if exclude_regex else None,
            verbose_level=1,
        )
    except Exception as e:
        return json.dumps({"error": str(e)}), 1.0

    if not diff:
        return None, 0.0

    diff_json = diff.to_json()

    # Compute a naive diff score: ratio of changed keys to total keys
    total_keys = _count_keys(orig_obj) or 1
    changed_keys = _count_diff_items(diff)
    score = min(changed_keys / total_keys, 1.0)

    return diff_json, score


def _convert_patterns_to_deepdiff_regex(patterns: list[str]) -> list[str]:
    """
    将智能降噪模式列表转换为 DeepDiff 的 exclude_regex_paths 格式。
    例如：timestamp -> root['timestamp']$
    """
    # 简化版本：生成匹配任何层级的模式
    # 例如 timestamp 会匹配 root['timestamp'] 和 root['data']['items'][*]['timestamp'] 等
    result = []
    for pattern in patterns:
        exact_match = re.fullmatch(r"\^([A-Za-z_][A-Za-z0-9_]*)\$", pattern)
        if exact_match:
            field_name = exact_match.group(1)
            result.append(rf"root(\[[^\]]+\])*\['{re.escape(field_name)}'\]$")
            continue
        # 移除首尾 ^ $ 锚点，因为我们要做正则匹配
        clean_pattern = pattern.strip("^$")
        # 对纯字段名模式使用更严格的“token 边界”匹配，避免 count 误伤 account_no。
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", clean_pattern):
            result.append(
                rf"root(\[[^\]]+\])*\['[^']*(?<![A-Za-z0-9]){re.escape(clean_pattern)}(?![A-Za-z0-9])[^']*'\]"
            )
        else:
            # DeepDiff 的 exclude_regex_paths 使用 Python 正则格式
            result.append(rf"root(\[[^\]]+\])*\[.*{clean_pattern}.*\]")
    return result


# ── Smart Diff Rules ──────────────────────────────────────────────────────────

def _apply_diff_rules(
    orig: object,
    repl: object,
    rules: list[dict],
) -> tuple[object, object, list[str]]:
    """
    Pre-process objects according to diff rules.
    Returns (modified_orig, modified_repl, extra_exclude_regexes).
    """
    orig = copy.deepcopy(orig)
    repl = copy.deepcopy(repl)
    extra_excludes: list[str] = []

    for rule in rules:
        rtype = rule.get("type", "")
        path = rule.get("path", "")
        if not path:
            continue

        path_parts = _split_path(path)

        if rtype == "ignore":
            # Add a DeepDiff regex exclude pattern for this path
            extra_excludes.append(_path_to_deepdiff_regex(path_parts))

        elif rtype == "numeric_tolerance":
            tolerance = float(rule.get("tolerance", 0.0))
            # Normalize repl to orig where the numeric difference is within tolerance
            repl = _transform_at_path_with_other(orig, repl, path_parts, tolerance)

        elif rtype == "regex_match":
            pattern = rule.get("pattern", ".*")
            # Pre-compile to validate; skip rule silently if pattern is invalid
            try:
                compiled = re.compile(pattern)
            except re.error:
                continue
            sentinel = "__REGEX_MATCHED__"
            orig = _transform_at_path(orig, path_parts, lambda v, _: sentinel if isinstance(v, str) and compiled.search(v) else v)
            repl = _transform_at_path(repl, path_parts, lambda v, _: sentinel if isinstance(v, str) and compiled.search(v) else v)

        elif rtype == "type_only":
            # Replace value with type name so only type differences are detected
            orig = _transform_at_path(orig, path_parts, lambda v, _: type(v).__name__)
            repl = _transform_at_path(repl, path_parts, lambda v, _: type(v).__name__)

    return orig, repl, extra_excludes


def _split_path(path: str) -> list[str]:
    """Split "data.items.*.price" → ["data", "items", "*", "price"]"""
    return [p for p in path.strip("$. ").split(".") if p]


def _path_to_deepdiff_regex(parts: list[str]) -> str:
    """
    Convert path parts to a DeepDiff exclude regex.
    Wildcards (*) match any key segment.  Exact segments use word-boundary anchoring
    to avoid 'price' matching 'unit_price'.
    """
    if not parts:
        return ".*"
    segments = []
    for p in parts:
        if p == "*":
            segments.append(r"\[[^\]]+\]")   # any single key/index
        else:
            segments.append(rf"\['{re.escape(p)}'\]")
    chain = "".join(segments)
    return rf"root{chain}$"


def _transform_at_path(obj: object, parts: list[str], fn) -> object:
    """Recursively transform values at the given path using fn(value, None)."""
    if not parts:
        return fn(obj, None)
    key = parts[0]
    rest = parts[1:]
    if isinstance(obj, dict):
        if key == "*":
            return {k: _transform_at_path(v, rest, fn) for k, v in obj.items()}
        elif key in obj:
            obj = dict(obj)
            obj[key] = _transform_at_path(obj[key], rest, fn)
    elif isinstance(obj, list):
        if key == "*":
            return [_transform_at_path(item, rest, fn) for item in obj]
        elif key.isdigit():
            idx = int(key)
            if idx < len(obj):
                obj = list(obj)
                obj[idx] = _transform_at_path(obj[idx], rest, fn)
    return obj


def _transform_at_path_with_other(orig: object, repl: object, parts: list[str], tolerance: float) -> object:
    """
    For numeric_tolerance: walk both objects simultaneously, normalize repl value
    to match orig if within tolerance.
    """
    if not parts:
        if isinstance(orig, (int, float)) and isinstance(repl, (int, float)):
            if abs(orig - repl) <= tolerance:
                return orig
        return repl
    key = parts[0]
    rest = parts[1:]
    if isinstance(orig, dict) and isinstance(repl, dict):
        if key == "*":
            repl = dict(repl)
            for k in repl:
                orig_v = orig.get(k)
                repl[k] = _transform_at_path_with_other(orig_v, repl[k], rest, tolerance)
        elif key in repl:
            repl = dict(repl)
            orig_v = orig.get(key) if isinstance(orig, dict) else None
            repl[key] = _transform_at_path_with_other(orig_v, repl[key], rest, tolerance)
    elif isinstance(orig, list) and isinstance(repl, list):
        if key == "*":
            repl = [
                _transform_at_path_with_other(
                    orig[i] if i < len(orig) else None, v, rest, tolerance
                )
                for i, v in enumerate(repl)
            ]
        elif key.isdigit():
            idx = int(key)
            if idx < len(repl):
                repl = list(repl)
                orig_v = orig[idx] if idx < len(orig) else None
                repl[idx] = _transform_at_path_with_other(orig_v, repl[idx], rest, tolerance)
    return repl


# ── Helpers ───────────────────────────────────────────────────────────────────

def _xml_to_dict(element):
    """Recursively convert an XML Element to a plain dict."""
    children = list(element)
    if not children:
        return element.text or None
    result: dict = {}
    for child in children:
        value = _xml_to_dict(child)
        tag = child.tag
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value
    return result


def _parse(text: str | None):
    if not text:
        return text
    if not isinstance(text, str):
        return text

    def _parse_text(value: str, depth: int = 0):
        if depth > 3:
            return value
        stripped_value = value.strip()
        if not stripped_value:
            return stripped_value

        # Try JSON first. AREX sometimes stores a plain XML/text response as a
        # JSON string literal, e.g. "\"<BookVo>...</BookVo>\"".
        try:
            parsed = json.loads(stripped_value)
            if isinstance(parsed, str):
                return _parse_text(parsed, depth + 1)
            return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Try XML — parse into a dict so field-level ignores work on XML responses
        if stripped_value.startswith("<"):
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(stripped_value)
                return {root.tag: _xml_to_dict(root)}
            except Exception:
                pass
        return value

    return _parse_text(text)


def _count_keys(obj, depth: int = 0) -> int:
    if depth > 10:
        return 1
    if isinstance(obj, dict):
        return sum(_count_keys(v, depth + 1) for v in obj.values()) or 1
    if isinstance(obj, list):
        return sum(_count_keys(i, depth + 1) for i in obj) or 1
    return 1


def _count_diff_items(diff: DeepDiff) -> int:
    total = 0
    for change_type in ("dictionary_item_added", "dictionary_item_removed",
                         "values_changed", "type_changes", "iterable_item_added",
                         "iterable_item_removed"):
        items = diff.get(change_type)
        if items:
            total += len(items)
    return total
