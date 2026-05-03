"""Generic sub-call list merge and de-duplication helpers."""

import json


def merge_sub_calls(primary: list[dict] | None, secondary: list[dict] | None) -> list[dict]:
    """Merge two sub-call lists, deduplicating by JSON signature."""
    merged: list[dict] = []
    seen: set[str] = set()
    for group in (primary or [], secondary or []):
        for item in group if isinstance(group, list) else [group]:
            if not isinstance(item, dict):
                continue
            signature = json.dumps(item, ensure_ascii=False, sort_keys=True)
            if signature in seen:
                continue
            seen.add(signature)
            merged.append(item)
    return merged


def exclude_duplicate_database_sub_calls(
    preferred: list[dict] | None,
    candidates: list[dict] | None,
) -> list[dict]:
    """Remove database sub-calls from candidates that already exist in preferred."""
    identities = {
        identity
        for identity in (_database_sub_call_identity(item) for item in (preferred or []))
        if identity is not None
    }
    if not identities:
        return candidates or []
    filtered: list[dict] = []
    for item in candidates or []:
        identity = _database_sub_call_identity(item)
        if identity is not None and identity in identities:
            continue
        filtered.append(item)
    return filtered


def _database_sub_call_identity(item: dict | None) -> tuple[str, str, str] | None:
    if not isinstance(item, dict):
        return None
    sub_type = str(item.get("type") or "").strip().lower()
    if sub_type not in {"mysql", "jdbc"}:
        return None
    operation = str(item.get("operation") or "").strip()
    table = str(item.get("table") or "").strip()
    if not operation or not table:
        return None
    return sub_type, operation, table
