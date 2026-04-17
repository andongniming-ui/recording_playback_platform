"""Transaction-code scoped request/response mapping for SAT -> UAT replay."""
from __future__ import annotations

import copy
import json
import logging
from collections.abc import Iterable
from typing import Any
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

MAPPING_RULE_TYPES = {"rename", "delete", "default", "set", "copy"}


def normalize_transaction_mapping_configs(raw: Any) -> list[dict]:
    """Return a normalized list of transaction mapping configs."""
    payload = _load_jsonish(raw)
    if payload is None:
        return []
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return []

    configs: list[dict] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        config = _normalize_config(item)
        if config and config.get("transaction_code"):
            configs.append(config)
    return configs


def find_transaction_mapping(transaction_code: str | None, configs: list[dict] | None) -> dict | None:
    """Find the first enabled config that matches the exact transaction code."""
    normalized_tx = _normalize_text(transaction_code)
    if not normalized_tx or not configs:
        return None
    for config in configs:
        if not isinstance(config, dict):
            continue
        if not config.get("enabled", True):
            continue
        if _normalize_text(config.get("transaction_code")) == normalized_tx:
            return config
    return None


def apply_transaction_mapping(
    text: str | None,
    transaction_code: str | None,
    configs: list[dict] | None,
    *,
    direction: str,
) -> str | None:
    """Apply request/response mappings for one transaction code."""
    if text in (None, ""):
        return text

    config = find_transaction_mapping(transaction_code, configs)
    if not config:
        return text

    rules = config.get("request_rules" if direction == "request" else "response_rules") or []
    if not isinstance(rules, list) or not rules:
        return text

    payload_kind, payload = _parse_payload(text)
    if payload_kind == "text":
        return text

    original_payload = payload
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        source = _normalize_text(rule.get("source"))
        if source and isinstance(payload, dict) and len(payload) == 1:
            root_key = next(iter(payload))
            path_parts = _split_path(source)
            if path_parts and path_parts[0] != root_key and path_parts[0] != "*":
                inner = payload.get(root_key)
                if isinstance(inner, (dict, list)):
                    new_inner, inner_changed = _apply_rule(inner, rule)
                    if inner_changed:
                        payload = dict(payload)
                        payload[root_key] = new_inner
                        continue

        payload, _ = _apply_rule(payload, rule)

    if payload is original_payload:
        return text
    return _serialize_payload(payload_kind, payload)


def describe_transaction_mapping(configs: list[dict] | None) -> list[dict]:
    """Return a UI-friendly summary of mapping configs."""
    normalized = normalize_transaction_mapping_configs(configs)
    summary: list[dict] = []
    for config in normalized:
        summary.append(
            {
                "transaction_code": config.get("transaction_code"),
                "enabled": config.get("enabled", True),
                "request_rule_count": len(config.get("request_rules") or []),
                "response_rule_count": len(config.get("response_rules") or []),
                "description": config.get("description"),
            }
        )
    return summary


def _normalize_config(value: dict) -> dict | None:
    transaction_code = _normalize_text(
        value.get("transaction_code") or value.get("transactionCode") or value.get("tx_code")
    )
    if not transaction_code:
        return None
    request_rules = _normalize_rules(
        value.get("request_rules") or value.get("requestRules") or value.get("request_mapping") or value.get("requestMapping")
    )
    response_rules = _normalize_rules(
        value.get("response_rules") or value.get("responseRules") or value.get("response_mapping") or value.get("responseMapping")
    )
    return {
        "transaction_code": transaction_code,
        "enabled": bool(value.get("enabled", True)),
        "description": value.get("description") or value.get("remark"),
        "request_rules": request_rules,
        "response_rules": response_rules,
    }


def _normalize_rules(value: Any) -> list[dict]:
    payload = _load_jsonish(value)
    if payload is None:
        return []
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return []

    rules: list[dict] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        rule_type = _normalize_text(item.get("type") or item.get("transform_type") or item.get("transformType")) or ""
        rule_type = rule_type.lower()
        if rule_type not in MAPPING_RULE_TYPES:
            continue
        source = _normalize_text(
            item.get("source")
            or item.get("source_path")
            or item.get("sourcePath")
            or item.get("field")
        )
        target = _normalize_text(
            item.get("target")
            or item.get("target_path")
            or item.get("targetPath")
        )
        value = item.get("value")
        if value is None and "default_value" in item:
            value = item.get("default_value")
        if value is None and "defaultValue" in item:
            value = item.get("defaultValue")
        rules.append(
            {
                "type": rule_type,
                "source": source,
                "target": target,
                "value": value,
                "enabled": bool(item.get("enabled", True)),
                "description": item.get("description") or item.get("remark"),
            }
        )
    return rules


def _apply_rule(payload: Any, rule: dict) -> tuple[Any, bool]:
    if not rule.get("enabled", True):
        return payload, False

    rule_type = _normalize_text(rule.get("type")).lower()
    if rule_type not in MAPPING_RULE_TYPES:
        return payload, False

    if rule_type in {"rename", "copy"}:
        source = _normalize_text(rule.get("source"))
        target = _normalize_text(rule.get("target"))
        if not source or not target:
            return payload, False
        found, value = _get_path(payload, _split_path(source))
        if not found:
            return payload, False
        if rule_type == "rename":
            payload, deleted = _delete_path(payload, _split_path(source))
            if not deleted:
                return payload, False
        payload, _ = _set_path(payload, _split_path(target), value, create_missing=True, only_if_missing=False)
        return payload, True

    if rule_type == "delete":
        source = _normalize_text(rule.get("source"))
        if not source:
            return payload, False
        return _delete_path(payload, _split_path(source))

    if rule_type == "default":
        source = _normalize_text(rule.get("source"))
        if not source:
            return payload, False
        found, value = _get_path(payload, _split_path(source))
        if found and not _is_empty(value):
            return payload, False
        payload, changed = _set_path(
            payload,
            _split_path(source),
            rule.get("value"),
            create_missing=True,
            only_if_missing=False,
        )
        return payload, changed

    if rule_type == "set":
        source = _normalize_text(rule.get("source"))
        if not source:
            return payload, False
        payload, changed = _set_path(
            payload,
            _split_path(source),
            rule.get("value"),
            create_missing=True,
            only_if_missing=False,
        )
        return payload, changed

    return payload, False


def _split_path(path: str) -> list[str]:
    return [part.strip() for part in str(path).strip("$. ").split(".") if part.strip()]


def _get_path(obj: Any, parts: list[str]) -> tuple[bool, Any]:
    if not parts:
        return True, obj
    if isinstance(obj, dict):
        key = parts[0]
        if key == "*":
            for value in obj.values():
                found, item = _get_path(value, parts[1:])
                if found:
                    return True, item
            return False, None
        if key not in obj:
            return False, None
        return _get_path(obj[key], parts[1:])
    if isinstance(obj, list):
        key = parts[0]
        if key == "*":
            for item in obj:
                found, value = _get_path(item, parts[1:])
                if found:
                    return True, value
            return False, None
        if key.isdigit():
            idx = int(key)
            if 0 <= idx < len(obj):
                return _get_path(obj[idx], parts[1:])
        return False, None
    return False, None


def _set_path(
    obj: Any,
    parts: list[str],
    value: Any,
    *,
    create_missing: bool,
    only_if_missing: bool,
) -> tuple[Any, bool]:
    if not parts:
        return value, True
    if isinstance(obj, dict):
        cloned = dict(obj)
        key = parts[0]
        if key == "*":
            changed = False
            for existing_key, existing_value in list(cloned.items()):
                new_value, sub_changed = _set_path(
                    existing_value,
                    parts[1:],
                    value,
                    create_missing=create_missing,
                    only_if_missing=only_if_missing,
                )
                if sub_changed:
                    cloned[existing_key] = new_value
                    changed = True
            return cloned, changed
        if len(parts) == 1:
            if only_if_missing and key in cloned and not _is_empty(cloned.get(key)):
                return obj, False
            cloned[key] = value
            return cloned, True
        child = cloned.get(key)
        if child is None:
            if not create_missing:
                return obj, False
            child = {}
        new_child, changed = _set_path(
            child,
            parts[1:],
            value,
            create_missing=create_missing,
            only_if_missing=only_if_missing,
        )
        if not changed:
            return obj, False
        cloned[key] = new_child
        return cloned, True
    if isinstance(obj, list):
        cloned_list = list(obj)
        key = parts[0]
        if key == "*":
            changed = False
            for index, existing_value in enumerate(cloned_list):
                new_value, sub_changed = _set_path(
                    existing_value,
                    parts[1:],
                    value,
                    create_missing=create_missing,
                    only_if_missing=only_if_missing,
                )
                if sub_changed:
                    cloned_list[index] = new_value
                    changed = True
            return cloned_list, changed
        if not key.isdigit():
            return obj, False
        idx = int(key)
        if idx >= len(cloned_list):
            return obj, False
        if len(parts) == 1:
            if only_if_missing and not _is_empty(cloned_list[idx]):
                return obj, False
            cloned_list[idx] = value
            return cloned_list, True
        new_child, changed = _set_path(
            cloned_list[idx],
            parts[1:],
            value,
            create_missing=create_missing,
            only_if_missing=only_if_missing,
        )
        if not changed:
            return obj, False
        cloned_list[idx] = new_child
        return cloned_list, True
    return obj, False


def _delete_path(obj: Any, parts: list[str]) -> tuple[Any, bool]:
    if not parts:
        return obj, False
    if isinstance(obj, dict):
        cloned = dict(obj)
        key = parts[0]
        if key == "*":
            changed = False
            for existing_key, existing_value in list(cloned.items()):
                new_value, sub_changed = _delete_path(existing_value, parts[1:])
                if sub_changed:
                    cloned[existing_key] = new_value
                    changed = True
            return cloned, changed
        if len(parts) == 1:
            if key in cloned:
                cloned.pop(key, None)
                return cloned, True
            return obj, False
        if key not in cloned:
            return obj, False
        new_child, changed = _delete_path(cloned[key], parts[1:])
        if not changed:
            return obj, False
        cloned[key] = new_child
        return cloned, True
    if isinstance(obj, list):
        cloned_list = list(obj)
        key = parts[0]
        if key == "*":
            changed = False
            for index, existing_value in enumerate(cloned_list):
                new_value, sub_changed = _delete_path(existing_value, parts[1:])
                if sub_changed:
                    cloned_list[index] = new_value
                    changed = True
            return cloned_list, changed
        if not key.isdigit():
            return obj, False
        idx = int(key)
        if idx >= len(cloned_list):
            return obj, False
        if len(parts) == 1:
            cloned_list.pop(idx)
            return cloned_list, True
        new_child, changed = _delete_path(cloned_list[idx], parts[1:])
        if not changed:
            return obj, False
        cloned_list[idx] = new_child
        return cloned_list, True
    return obj, False


def _parse_payload(text: str) -> tuple[str, Any]:
    stripped = text.strip()
    if not stripped:
        return "text", text
    try:
        return "json", json.loads(text)
    except Exception:
        pass
    if stripped.startswith("<"):
        try:
            root = ET.fromstring(stripped)
        except Exception:
            return "text", text
        return "xml", {root.tag: _xml_to_dict(root)}
    return "text", text


def _xml_to_dict(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return element.text or ""
    result: dict[str, Any] = {}
    for child in children:
        value = _xml_to_dict(child)
        tag = child.tag.split("}", 1)[-1]
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value
    return result


def _serialize_payload(kind: str, payload: Any) -> str | None:
    if kind == "json":
        return json.dumps(payload, ensure_ascii=False)
    if kind == "xml":
        if not isinstance(payload, dict) or not payload:
            return None
        root_tag = next(iter(payload))
        root = _dict_to_xml(root_tag, payload[root_tag])
        return ET.tostring(root, encoding="unicode")
    return payload if isinstance(payload, str) else str(payload)


def _dict_to_xml(tag: str, value: Any) -> ET.Element:
    element = ET.Element(tag)
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, list):
                for nested in item:
                    element.append(_dict_to_xml(key, nested))
            else:
                element.append(_dict_to_xml(key, item))
    elif isinstance(value, list):
        for item in value:
            element.append(_dict_to_xml("item", item))
    elif value is None:
        element.text = ""
    else:
        element.text = str(value)
    return element


def _is_empty(value: Any) -> bool:
    return value in (None, "", [], {})


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _load_jsonish(value: Any) -> Any:
    if value in (None, ""):
        return None
    if isinstance(value, (list, dict)):
        return copy.deepcopy(value)
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return None
    return None
