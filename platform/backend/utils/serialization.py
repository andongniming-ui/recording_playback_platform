"""Serialization helpers shared by audit logging and API code."""
import json


def json_text(value) -> str | None:
    if value in (None, "", [], {}):
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)
