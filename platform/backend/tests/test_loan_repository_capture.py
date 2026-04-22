"""
TDD tests for:
  Fix 1 (P0): LoanDataRepository DynamicClass metadata in repository_capture.py
  Fix 2 (P2): BankJdbcRepository dead code removed from repository_capture.py
  Fix 3 (P2): AREX flush delay reads from settings.arex_flush_delay_s
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from utils.repository_capture import (
    get_dynamic_class_configurations,
    lookup_repository_capture_metadata,
    normalize_repository_sub_call,
)


# ---------------------------------------------------------------------------
# Fix 1: LoanDataRepository must be in repository_capture.py
# ---------------------------------------------------------------------------


def test_loan_find_customer_metadata_exists():
    meta = lookup_repository_capture_metadata(
        "com.arex.demo.loan.repository.LoanDataRepository.findCustomer"
    )
    assert meta is not None, "LoanDataRepository.findCustomer should be registered"
    assert meta["table"] == "customer"
    assert meta["operation"] == "SELECT customer"
    assert meta["status"] == "READ"
    assert meta["parameter_names"] == ["customerId"]


def test_loan_find_product_metadata_exists():
    meta = lookup_repository_capture_metadata(
        "com.arex.demo.loan.repository.LoanDataRepository.findProduct"
    )
    assert meta is not None, "LoanDataRepository.findProduct should be registered"
    assert meta["table"] == "product_rule"
    assert meta["operation"] == "SELECT product_rule"
    assert meta["status"] == "READ"
    assert meta["parameter_names"] == ["productId"]


def test_loan_is_on_blacklist_metadata_exists():
    meta = lookup_repository_capture_metadata(
        "com.arex.demo.loan.repository.LoanDataRepository.isOnBlacklist"
    )
    assert meta is not None, "LoanDataRepository.isOnBlacklist should be registered"
    assert meta["table"] == "blacklist"
    assert meta["operation"] == "SELECT blacklist"
    assert meta["status"] == "READ"
    assert meta["parameter_names"] == ["customerId"]


def test_loan_dynamic_class_configs_included():
    configs = get_dynamic_class_configurations()
    loan_entries = [c for c in configs if "LoanDataRepository" in c["fullClassName"]]
    assert len(loan_entries) >= 3, f"Expected >=3 LoanDataRepository configs, got {len(loan_entries)}"
    method_names = {c["methodName"] for c in loan_entries}
    assert "findCustomer" in method_names
    assert "findProduct" in method_names
    assert "isOnBlacklist" in method_names


def test_normalize_loan_find_customer_produces_structured_sub_call():
    mocker = {
        "operationName": "com.arex.demo.loan.repository.LoanDataRepository.findCustomer",
        "targetRequest": {"body": '["C001"]'},
        "targetResponse": {"body": '{"customer_id": "C001", "age": 35, "status": "ACTIVE"}'},
    }
    result = normalize_repository_sub_call(mocker, "DynamicClass")
    assert result is not None
    assert result["type"] == "MySQL"
    assert result["table"] == "customer"
    assert result["operation"] == "SELECT customer"
    assert result["status"] == "READ"
    # single-param list → mapped to {paramName: value}
    assert result.get("params") == {"customerId": "C001"}
    assert result["response"] == {"customer_id": "C001", "age": 35, "status": "ACTIVE"}


def test_normalize_loan_find_product_produces_structured_sub_call():
    mocker = {
        "operationName": "com.arex.demo.loan.repository.LoanDataRepository.findProduct",
        "targetRequest": {"body": '["PROD-001"]'},
        "targetResponse": {"body": '{"product_id": "PROD-001", "min_age": 18, "max_age": 60}'},
    }
    result = normalize_repository_sub_call(mocker, "DynamicClass")
    assert result is not None
    assert result["type"] == "MySQL"
    assert result["table"] == "product_rule"
    assert result.get("params") == {"productId": "PROD-001"}


def test_normalize_loan_is_on_blacklist_produces_structured_sub_call():
    mocker = {
        "operationName": "com.arex.demo.loan.repository.LoanDataRepository.isOnBlacklist",
        "targetRequest": {"body": '["C001"]'},
        "targetResponse": {"body": "false"},
    }
    result = normalize_repository_sub_call(mocker, "DynamicClass")
    assert result is not None
    assert result["table"] == "blacklist"
    assert result.get("params") == {"customerId": "C001"}


# ---------------------------------------------------------------------------
# Fix 2: BankJdbcRepository dead code must be removed
# ---------------------------------------------------------------------------


def test_bank_jdbc_repository_find_customer_removed():
    meta = lookup_repository_capture_metadata(
        "com.cxm.nls.repository.BankJdbcRepository.findCustomerByIdNo"
    )
    assert meta is None, (
        "BankJdbcRepository.findCustomerByIdNo is dead code with no matching test system "
        "and should have been removed from repository_capture.py"
    )


def test_bank_jdbc_repository_not_in_dynamic_configs():
    configs = get_dynamic_class_configurations()
    bank_entries = [c for c in configs if "BankJdbcRepository" in c["fullClassName"]]
    assert len(bank_entries) == 0, (
        f"BankJdbcRepository should be removed from dynamic class configs, found: {bank_entries}"
    )


# ---------------------------------------------------------------------------
# Fix 3: AREX flush delay reads from settings
# ---------------------------------------------------------------------------


def test_arex_flush_delay_setting_has_default():
    from config import settings
    assert hasattr(settings, "arex_flush_delay_s"), (
        "settings must have arex_flush_delay_s field"
    )
    assert settings.arex_flush_delay_s == 1.0, (
        f"Default flush delay should be 1.0s, got {settings.arex_flush_delay_s}"
    )


def test_replay_executor_uses_settings_flush_delay():
    """_AREX_AGENT_FLUSH_DELAY_S must equal settings.arex_flush_delay_s (not a hardcoded literal)."""
    from config import settings
    import core.replay_executor as executor
    assert executor._AREX_AGENT_FLUSH_DELAY_S == settings.arex_flush_delay_s, (
        "_AREX_AGENT_FLUSH_DELAY_S in replay_executor must come from settings.arex_flush_delay_s"
    )
