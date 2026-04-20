import json
from typing import Any


NOISE_DYNAMIC_CLASS_OPERATIONS = {
    "java.lang.System.currentTimeMillis",
    "java.lang.System.nanoTime",
}


_REPOSITORY_CAPTURE_SPECS: list[dict[str, Any]] = [
    {
        "full_class_name": "com.cxm.nls.repository.BankJdbcRepository",
        "database": "mysql",
        "type": "MySQL",
        "methods": [
            {
                "method_name": "findCustomerByIdNo",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["idNo"],
                "table": "bank_customer",
                "operation": "SELECT bank_customer",
                "status": "READ",
            },
            {
                "method_name": "findCustomerByNo",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerNo"],
                "table": "bank_customer",
                "operation": "SELECT bank_customer",
                "status": "READ",
            },
            {
                "method_name": "findAccountByNo",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["accountNo"],
                "table": "bank_account",
                "operation": "SELECT bank_account",
                "status": "READ",
            },
            {
                "method_name": "findPrimaryAccountByCustomerNo",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerNo"],
                "table": "bank_account",
                "operation": "SELECT bank_account",
                "status": "READ",
            },
            {
                "method_name": "findLoanByNo",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["loanNo"],
                "table": "bank_loan",
                "operation": "SELECT bank_loan",
                "status": "READ",
            },
            {
                "method_name": "findRecentStatements",
                "parameter_types": "java.lang.String@int",
                "key_formula": "#p0",
                "parameter_names": ["accountNo", "limit"],
                "table": "bank_statement_line",
                "operation": "SELECT bank_statement_line",
                "status": "READ",
            },
            {
                "method_name": "findRecentTransactionsByAccountNo",
                "parameter_types": "java.lang.String@int",
                "key_formula": "#p0",
                "parameter_names": ["accountNo", "limit"],
                "table": "bank_transaction_log",
                "operation": "SELECT bank_transaction_log",
                "status": "READ",
            },
            {
                "method_name": "countSubCalls",
                "parameter_types": "long",
                "key_formula": "#p0",
                "parameter_names": ["txLogId"],
                "table": "bank_sub_call_log",
                "operation": "SELECT bank_sub_call_log",
                "status": "READ",
            },
        ],
    },
    {
        "full_class_name": "com.arex.demo.didi.common.repository.CarDataRepository",
        "database": "mysql",
        "type": "MySQL",
        "methods": [
            {
                "method_name": "findVehicle",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["plateNo", "vin"],
                "table": "car_vehicle",
                "operation": "SELECT car_vehicle",
                "status": "READ",
            },
            {
                "method_name": "findCustomer",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerNo"],
                "table": "car_customer",
                "operation": "SELECT car_customer",
                "status": "READ",
            },
            {
                "method_name": "findPolicy",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["policyNo", "plateNo"],
                "table": "car_policy",
                "operation": "SELECT car_policy",
                "status": "READ",
            },
            {
                "method_name": "findClaim",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["claimNo", "plateNo"],
                "table": "car_claim",
                "operation": "SELECT car_claim",
                "status": "READ",
            },
            {
                "method_name": "findDispatch",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["plateNo", "garageCode"],
                "table": "car_dispatch",
                "operation": "SELECT car_dispatch",
                "status": "READ",
            },
            {
                "method_name": "saveAudit",
                "parameter_types": "java.lang.String@java.lang.String@java.lang.String@java.lang.String@java.lang.String@java.math.BigDecimal@java.lang.String",
                "key_formula": "#p1",
                "parameter_names": [
                    "txnCode",
                    "requestNo",
                    "customerNo",
                    "plateNo",
                    "riskLevel",
                    "quotedAmount",
                    "variantId",
                ],
                "table": "car_order_audit",
                "operation": "INSERT car_order_audit",
                "status": "WRITE",
            },
            {
                "method_name": "updateVehicleStatus",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["plateNo", "status"],
                "table": "car_vehicle",
                "operation": "UPDATE car_vehicle",
                "status": "WRITE",
            },
        ],
    },
]


_METHOD_METADATA: dict[tuple[str, str], dict[str, Any]] = {}
for _spec in _REPOSITORY_CAPTURE_SPECS:
    for _method in _spec["methods"]:
        _METHOD_METADATA[(_spec["full_class_name"], _method["method_name"])] = {
            "full_class_name": _spec["full_class_name"],
            "database": _spec["database"],
            "type": _spec["type"],
            **_method,
        }


def get_dynamic_class_configurations() -> list[dict[str, str]]:
    return [
        {
            "fullClassName": spec["full_class_name"],
            "methodName": method["method_name"],
            "parameterTypes": method["parameter_types"],
            "keyFormula": method["key_formula"],
        }
        for spec in _REPOSITORY_CAPTURE_SPECS
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
    return _METHOD_METADATA.get((class_name, method_name))


def is_noise_dynamic_mocker(operation_name: str | None, category_name: str | None) -> bool:
    return (category_name or "").strip().lower() == "dynamicclass" and (operation_name or "").strip() in NOISE_DYNAMIC_CLASS_OPERATIONS


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
    return sub_call
