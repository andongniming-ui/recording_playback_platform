"""Tests for compare rule CRUD and unit tests for diff.py / assertions.py."""
import json
import pytest


@pytest.fixture
def rule_payload():
    """Return a fresh compare-rule payload dict for each test."""
    return {
        "name": "ignore-timestamps",
        "scope": "global",
        "rule_type": "ignore",
        "config": json.dumps({"path": "timestamp"}),
        "is_active": True,
    }


# ---------------------------------------------------------------------------
# Compare rule CRUD
# ---------------------------------------------------------------------------

def test_create_compare_rule(client, admin_headers, rule_payload):
    resp = client.post("/api/v1/compare-rules", json=rule_payload, headers=admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "ignore-timestamps"
    assert body["rule_type"] == "ignore"
    assert "id" in body


def test_list_compare_rules(client, admin_headers, rule_payload):
    client.post("/api/v1/compare-rules", json=rule_payload, headers=admin_headers)
    resp = client.get("/api/v1/compare-rules", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1


def test_get_compare_rule(client, admin_headers, rule_payload):
    rule = client.post(
        "/api/v1/compare-rules", json=rule_payload, headers=admin_headers
    ).json()
    resp = client.get(f"/api/v1/compare-rules/{rule['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == rule["id"]


def test_get_compare_rule_not_found(client, admin_headers):
    resp = client.get("/api/v1/compare-rules/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_update_compare_rule(client, admin_headers, rule_payload):
    rule = client.post(
        "/api/v1/compare-rules", json=rule_payload, headers=admin_headers
    ).json()
    resp = client.put(
        f"/api/v1/compare-rules/{rule['id']}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_delete_compare_rule(client, admin_headers, rule_payload):
    rule = client.post(
        "/api/v1/compare-rules", json=rule_payload, headers=admin_headers
    ).json()
    resp = client.delete(
        f"/api/v1/compare-rules/{rule['id']}", headers=admin_headers
    )
    assert resp.status_code == 204

    resp2 = client.get(
        f"/api/v1/compare-rules/{rule['id']}", headers=admin_headers
    )
    assert resp2.status_code == 404


# ---------------------------------------------------------------------------
# Unit tests for utils/diff.py
# ---------------------------------------------------------------------------

def test_diff_identical_responses():
    from utils.diff import compute_diff

    original = '{"code": 0, "message": "ok"}'
    replayed = '{"code": 0, "message": "ok"}'
    diff_json, score = compute_diff(original, replayed)
    assert diff_json is None
    assert score == 0.0


def test_diff_different_responses():
    from utils.diff import compute_diff

    original = '{"code": 0, "data": "hello"}'
    replayed = '{"code": 1, "data": "world"}'
    diff_json, score = compute_diff(original, replayed)
    assert diff_json is not None
    assert score > 0.0


def test_diff_with_ignore_fields():
    from utils.diff import compute_diff

    original = '{"code": 0, "timestamp": 1000}'
    replayed = '{"code": 0, "timestamp": 9999}'
    diff_json, score = compute_diff(original, replayed, ignore_fields=["timestamp"])
    assert diff_json is None
    assert score == 0.0


def test_smart_noise_reduction_for_xml_keeps_account_number_diff():
    from utils.diff import compute_diff

    original = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<response>
  <service_id>OPEN_ACCOUNT</service_id>
  <code>0000</code>
  <msg>开户成功</msg>
  <timestamp>1775888580157</timestamp>
  <body>
    <account_no>62226222000000017</account_no>
    <customer_no>C001</customer_no>
    <open_date>20260411142300</open_date>
  </body>
</response>"""
    replayed = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<response>
  <service_id>OPEN_ACCOUNT</service_id>
  <code>0000</code>
  <msg>开户成功</msg>
  <timestamp>1775892082536</timestamp>
  <body>
    <account_no>62226222000000019</account_no>
    <customer_no>C001</customer_no>
    <open_date>20260411152122</open_date>
  </body>
</response>"""

    diff_json, score = compute_diff(original, replayed, smart_noise_reduction=True)

    assert diff_json is not None
    assert "account_no" in diff_json
    assert "timestamp" not in diff_json
    assert "open_date" not in diff_json
    assert score > 0.0


def test_diff_none_inputs():
    from utils.diff import compute_diff

    diff_json, score = compute_diff(None, None)
    assert diff_json is None
    assert score == 0.0


# ---------------------------------------------------------------------------
# Unit tests for utils/assertions.py
# ---------------------------------------------------------------------------

def test_assertion_status_code_eq_pass():
    from utils.assertions import evaluate_assertions

    assertions = [{"type": "status_code_eq", "value": 200}]
    results = evaluate_assertions(assertions, '{"ok": true}', 200, 0.0)
    assert len(results) == 1
    assert results[0]["passed"] is True


def test_assertion_status_code_eq_fail():
    from utils.assertions import evaluate_assertions

    assertions = [{"type": "status_code_eq", "value": 200}]
    results = evaluate_assertions(assertions, '{"ok": false}', 500, 0.0)
    assert results[0]["passed"] is False


def test_assertion_json_path_eq():
    from utils.assertions import evaluate_assertions

    assertions = [{"type": "json_path_eq", "path": "code", "value": 0}]
    results = evaluate_assertions(assertions, '{"code": 0, "msg": "ok"}', 200, 0.0)
    assert results[0]["passed"] is True


def test_assertion_response_not_empty():
    from utils.assertions import evaluate_assertions, assertions_all_passed

    assertions = [{"type": "response_not_empty"}]
    results = evaluate_assertions(assertions, "", 200, 0.0)
    assert results[0]["passed"] is False

    results2 = evaluate_assertions(assertions, '{"data": 1}', 200, 0.0)
    assert results2[0]["passed"] is True
    assert assertions_all_passed(results2) is True


def test_assertions_all_passed_empty():
    from utils.assertions import assertions_all_passed

    assert assertions_all_passed([]) is True
    assert assertions_all_passed(None) is True
