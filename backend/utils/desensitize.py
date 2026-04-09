"""Sensitive field masking utility."""
import json
import re
from typing import Any


DEFAULT_SENSITIVE_KEYS = {
    "password", "passwd", "pwd", "secret", "token", "api_key", "apikey",
    "authorization", "auth", "credential", "private_key", "access_key",
    "card_number", "cardnumber", "cvv", "id_card", "idcard",
}

MASK = "***MASKED***"


def desensitize(data: Any, rules: list[dict] | None = None) -> Any:
    """
    Recursively mask sensitive fields in a dict/list structure.

    rules format: [{"key": "password"}, {"key_regex": ".*secret.*"}]
    If rules is None, use DEFAULT_SENSITIVE_KEYS.
    """
    sensitive_keys = set(DEFAULT_SENSITIVE_KEYS)
    regex_patterns = []

    if rules:
        for rule in rules:
            if "key" in rule:
                sensitive_keys.add(rule["key"].lower())
            elif "key_regex" in rule:
                try:
                    regex_patterns.append(re.compile(rule["key_regex"], re.IGNORECASE))
                except re.error:
                    pass

    return _mask(data, sensitive_keys, regex_patterns)


def _mask(obj: Any, sensitive_keys: set, regex_patterns: list) -> Any:
    if isinstance(obj, dict):
        return {
            k: (MASK if _is_sensitive(k, sensitive_keys, regex_patterns) else _mask(v, sensitive_keys, regex_patterns))
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [_mask(item, sensitive_keys, regex_patterns) for item in obj]
    return obj


def _is_sensitive(key: str, sensitive_keys: set, regex_patterns: list) -> bool:
    key_lower = key.lower()
    if key_lower in sensitive_keys:
        return True
    for pattern in regex_patterns:
        if pattern.search(key):
            return True
    return False


def desensitize_json_str(json_str: str | None, rules: list[dict] | None = None) -> str | None:
    """Desensitize a JSON string. Returns original string if not valid JSON."""
    if not json_str:
        return json_str
    try:
        obj = json.loads(json_str)
        return json.dumps(desensitize(obj, rules), ensure_ascii=False)
    except Exception:
        return json_str
