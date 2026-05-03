import json
import logging
from typing import Any


logger = logging.getLogger(__name__)

NOISE_DYNAMIC_CLASS_OPERATIONS = {
    "java.lang.System.currentTimeMillis",
    "java.lang.System.nanoTime",
}

_BUILTIN_SPECS: list[dict[str, Any]] = []
_plugins_loaded_for_metadata = False

def _get_all_specs() -> list[dict[str, Any]]:
    """Aggregate repository capture specs from built-in list + all registered plugins."""
    specs = list(_BUILTIN_SPECS)
    try:
        from utils.system_plugin import get_all_plugins
        for plugin in get_all_plugins():
            specs.extend(plugin.get_repository_specs())
    except ImportError:
        logger.debug("system_plugin not available, using built-in specs only")
    return specs


def _build_method_metadata() -> dict[tuple[str, str], dict[str, Any]]:
    metadata: dict[tuple[str, str], dict[str, Any]] = {}
    for spec in _get_all_specs():
        for method in spec["methods"]:
            metadata[(spec["full_class_name"], method["method_name"])] = {
                "full_class_name": spec["full_class_name"],
                "database": spec["database"],
                "type": spec["type"],
                **method,
            }
    return metadata


_METHOD_METADATA: dict[tuple[str, str], dict[str, Any]] = _build_method_metadata()


def refresh_method_metadata(load_plugin_modules: bool = False) -> None:
    """Rebuild _METHOD_METADATA after plugins are registered. Call once at startup."""
    global _plugins_loaded_for_metadata
    if load_plugin_modules and not _plugins_loaded_for_metadata:
        try:
            from utils.system_plugin import load_plugins
            load_plugins()
            _plugins_loaded_for_metadata = True
        except ImportError:
            logger.debug("system_plugin not available, refreshing without plugin discovery")
    global _METHOD_METADATA
    _METHOD_METADATA = _build_method_metadata()


def get_dynamic_class_configurations() -> list[dict[str, str]]:
    return [
        {
            "fullClassName": spec["full_class_name"],
            "methodName": method["method_name"],
            "parameterTypes": method["parameter_types"],
            "keyFormula": method["key_formula"],
        }
        for spec in _get_all_specs()
        for method in spec["methods"]
    ]


def _parse_json_like(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return value


def _stringify_non_empty(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def _first_attr(attrs: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = attrs.get(name)
        if value not in (None, ""):
            return value
    return None


def normalize_generic_database_sub_call(mocker: dict, category_name: str | None = None) -> dict[str, Any] | None:
    """Normalize native JDBC/MySQL mockers when no repository mapping exists."""
    category = (category_name or "").strip()
    operation_name = mocker.get("operationName")
    target_request = mocker.get("targetRequest") or {}
    target_response = mocker.get("targetResponse") or {}
    request_attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
    response_attrs = (target_response.get("attributes") or {}) if isinstance(target_response, dict) else {}
    normalized_category = category.lower()
    normalized_operation = str(operation_name or "").lower()
    combined = " ".join([normalized_category, normalized_operation])

    if not any(marker in combined for marker in ("mysql", "jdbc", "database", "sql")):
        return None

    request_body = target_request.get("body") if isinstance(target_request, dict) else target_request
    response_body = target_response.get("body") if isinstance(target_response, dict) else target_response
    request_value = _parse_json_like(request_body)
    response_value = _parse_json_like(response_body)
    sql_text = (
        _first_attr(request_attrs, "Sql", "SQL", "sql", "statement", "query")
        or (request_value.get("sql") if isinstance(request_value, dict) else None)
        or (request_value.get("statement") if isinstance(request_value, dict) else None)
        or (request_value if isinstance(request_value, str) and re_like_sql(request_value) else None)
        or operation_name
    )
    params_value = (
        _first_attr(request_attrs, "parameters", "Parameters", "params", "Params", "args", "Args", "arguments", "Arguments")
        or (request_value.get("parameters") if isinstance(request_value, dict) else None)
        or (request_value.get("params") if isinstance(request_value, dict) else None)
        or (request_value.get("args") if isinstance(request_value, dict) else None)
        or (request_value.get("arguments") if isinstance(request_value, dict) else None)
    )
    params_value = _parse_json_like(params_value)
    if params_value is not None and not isinstance(params_value, (dict, list, tuple)):
        params_value = [params_value]
    operation = _first_attr(request_attrs, "Operation", "operation", "methodName") or operation_name or sql_text
    database = _first_attr(request_attrs, "Database", "database", "dbName", "schema", "catalog", "datasource")
    table = _first_attr(request_attrs, "Table", "table", "tableName")
    elapsed = _first_attr(response_attrs, "ElapsedMs", "elapsedMs", "cost", "duration")

    sub_call = {
        "type": "MySQL" if "mysql" in combined or "jdbc" in combined or "sql" in combined else category or "Database",
        "source": "agent",
        "database": _stringify_non_empty(database),
        "table": _stringify_non_empty(table),
        "operation": _stringify_non_empty(operation),
        "request": request_value,
        "response": response_value,
    }
    if sql_text:
        sub_call["sql"] = _stringify_non_empty(sql_text)
        sub_call["sql_text"] = _stringify_non_empty(sql_text)
    if params_value is not None:
        sub_call["params"] = list(params_value) if isinstance(params_value, tuple) else params_value
    if elapsed is not None:
        try:
            sub_call["elapsed_ms"] = float(elapsed)
        except (TypeError, ValueError):
            pass
    return {key: value for key, value in sub_call.items() if value is not None}


def re_like_sql(value: str) -> bool:
    return value.strip().split(" ", 1)[0].upper() in {"SELECT", "INSERT", "UPDATE", "DELETE", "MERGE", "CALL", "WITH"}


def _normalize_method_request(raw_request: Any, parameter_names: list[str]) -> tuple[Any, Any]:
    request_value = _parse_json_like(raw_request)
    if request_value is None:
        return None, None

    if isinstance(request_value, dict):
        if parameter_names:
            params = {
                key: request_value.get(key)
                for key in parameter_names
                if request_value.get(key) not in (None, "", [])
            }
            return request_value, (params or request_value)
        return request_value, request_value

    if isinstance(request_value, list):
        if parameter_names:
            params = {
                name: request_value[index]
                for index, name in enumerate(parameter_names)
                if index < len(request_value) and request_value[index] not in (None, "", [])
            }
            return (params or request_value), (params or request_value)
        return request_value, request_value

    if len(parameter_names) == 1:
        params = {parameter_names[0]: request_value}
        return params, params

    return request_value, None


def lookup_repository_capture_metadata(operation_name: str | None) -> dict[str, Any] | None:
    operation = (operation_name or "").strip()
    if not operation:
        return None
    class_name, sep, method_name = operation.rpartition(".")
    if not sep:
        return None
    metadata = _METHOD_METADATA.get((class_name, method_name))
    if metadata is not None:
        return metadata
    refresh_method_metadata(load_plugin_modules=True)
    return _METHOD_METADATA.get((class_name, method_name))


def is_noise_dynamic_mocker(operation_name: str | None, category_name: str | None) -> bool:
    return (category_name or "").strip().lower() == "dynamicclass" and (operation_name or "").strip() in NOISE_DYNAMIC_CLASS_OPERATIONS


def _build_sql_text(metadata: dict[str, Any], params_value: Any) -> str | None:
    """Build a human-readable SQL hint from Repository method metadata and params.

    Examples:
        SELECT * FROM customer WHERE customerId='C001'
        INSERT INTO orders (orderId='O001', status='PENDING')
        UPDATE orders SET status='DELIVERED' WHERE orderId='O001'
    """
    status = (metadata.get("status") or "").upper()
    table = metadata.get("table") or ""
    if not table:
        return None

    params_str = ""
    if isinstance(params_value, dict) and params_value:
        items = ", ".join(f"{k}='{v}'" for k, v in params_value.items())
        params_str = f"({items})"

    if status == "READ":
        if params_str:
            return f"SELECT * FROM {table} WHERE {params_str[1:-1]}"
        return f"SELECT * FROM {table}"
    elif status == "WRITE":
        operation = (metadata.get("operation") or "").upper()
        if operation.startswith("INSERT"):
            return f"INSERT INTO {table} {params_str}" if params_str else f"INSERT INTO {table}"
        elif operation.startswith("UPDATE"):
            if params_str:
                pairs = list(params_value.items()) if isinstance(params_value, dict) else []
                if len(pairs) > 1:
                    set_part = ", ".join(f"{k}='{v}'" for k, v in pairs[1:])
                    where_part = f"{pairs[0][0]}='{pairs[0][1]}'"
                    return f"UPDATE {table} SET {set_part} WHERE {where_part}"
            return f"UPDATE {table} {params_str}" if params_str else f"UPDATE {table}"
        elif operation.startswith("DELETE"):
            return f"DELETE FROM {table} WHERE {params_str[1:-1]}" if params_str else f"DELETE FROM {table}"
    return None


def normalize_repository_sub_call(mocker: dict, category_name: str | None = None) -> dict[str, Any] | None:
    operation_name = mocker.get("operationName")
    metadata = lookup_repository_capture_metadata(operation_name)
    if not metadata:
        return None

    target_request = mocker.get("targetRequest") or {}
    target_response = mocker.get("targetResponse") or {}

    request_body = target_request.get("body") if isinstance(target_request, dict) else target_request
    response_body = target_response.get("body") if isinstance(target_response, dict) else target_response
    request_value, params_value = _normalize_method_request(request_body, metadata.get("parameter_names") or [])
    response_value = _parse_json_like(response_body)

    sub_call = {
        "type": metadata.get("type") or category_name or "DynamicClass",
        "source": "agent",
        "database": metadata.get("database"),
        "table": metadata.get("table"),
        "operation": metadata.get("operation") or operation_name,
        "request": request_value,
        "response": response_value,
        "status": metadata.get("status"),
    }
    if params_value is not None:
        sub_call["params"] = params_value
    sql_text = _build_sql_text(metadata, params_value)
    if sql_text:
        sub_call["sql_text"] = sql_text
    return sub_call
