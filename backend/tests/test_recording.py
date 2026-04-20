"""Tests for recording session CRUD, recording listing, and session sync."""
import base64
import json
import logging
from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import database
from sqlalchemy import select
from api.v1.sessions import (
    _extract_sub_calls,
    _fetch_didi_sub_calls,
    _fetch_dynamic_class_sub_calls,
    _remove_sub_invocation_recordings,
    _sync_from_arex_storage,
)
from integration.arex_client import ArexClient
from models.arex_mocker import ArexMocker
from models.recording import Recording
from utils.governance import infer_transaction_code


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

def _create_session(client, app_id, headers, name="test-session"):
    return client.post(
        "/api/v1/sessions",
        json={"application_id": app_id, "name": name},
        headers=headers,
    )


def test_create_session(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = _create_session(client, app_id, admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "test-session"
    assert body["status"] == "idle"
    assert body["application_id"] == app_id


def test_list_sessions(client, admin_headers, created_app):
    app_id = created_app["id"]
    _create_session(client, app_id, admin_headers, "sess-a")
    _create_session(client, app_id, admin_headers, "sess-b")

    resp = client.get("/api/v1/sessions", headers=admin_headers)
    assert resp.status_code == 200
    sessions = resp.json()
    assert len(sessions) >= 2


def test_list_sessions_filter_by_app(client, admin_headers, created_app):
    app_id = created_app["id"]
    _create_session(client, app_id, admin_headers, "filtered-session")

    resp = client.get(
        f"/api/v1/sessions?application_id={app_id}", headers=admin_headers
    )
    assert resp.status_code == 200
    for s in resp.json():
        assert s["application_id"] == app_id


def test_list_sessions_supports_search_and_status_filters(client, admin_headers, created_app):
    app_id = created_app["id"]
    first = _create_session(client, app_id, admin_headers, "daily-orders").json()
    second = _create_session(client, app_id, admin_headers, "nightly-billing").json()

    start_resp = client.post(f"/api/v1/sessions/{second['id']}/start", headers=admin_headers)
    assert start_resp.status_code == 200

    resp = client.get("/api/v1/sessions?search=nightly&status=active", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["id"] == second["id"]
    assert body[0]["status"] == "active"
    assert all(item["id"] != first["id"] for item in body)


def test_get_session(client, admin_headers, created_app):
    app_id = created_app["id"]
    created = _create_session(client, app_id, admin_headers).json()
    sess_id = created["id"]

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == sess_id


def test_get_session_not_found(client, admin_headers):
    resp = client.get("/api/v1/sessions/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_delete_session(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    resp = client.delete(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 204

    resp2 = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp2.status_code == 404


def test_create_session_invalid_app(client, admin_headers):
    resp = client.post(
        "/api/v1/sessions",
        json={"application_id": 9999, "name": "orphan"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_start_stop_session_flow_and_sync_alias(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "start-stop-session").json()["id"]

    with patch("api.v1.sessions._sync_from_arex_storage", new=AsyncMock(return_value=None)):
        start_resp = client.post(f"/api/v1/sessions/{sess_id}/start", headers=admin_headers)
        assert start_resp.status_code == 200
        assert start_resp.json()["status"] == "active"

        stop_resp = client.post(f"/api/v1/sessions/{sess_id}/stop", json={}, headers=admin_headers)
        assert stop_resp.status_code == 200
        assert stop_resp.json()["status"] == "collecting"

        sync_resp = client.post(f"/api/v1/sessions/{sess_id}/sync", json={}, headers=admin_headers)
        assert sync_resp.status_code == 409

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "collecting"


# ---------------------------------------------------------------------------
# Recording listing
# ---------------------------------------------------------------------------

def test_list_recordings_empty(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_infer_transaction_code_supports_transaction_id_xml():
    xml = """
    <request>
      <transaction_id>car001_open</transaction_id>
      <SYS_EVT_TRACE_ID>1234567890123456789012345</SYS_EVT_TRACE_ID>
    </request>
    """

    assert infer_transaction_code(xml) == "car001_open"


def test_arex_client_treats_naive_datetimes_as_utc():
    dt = datetime.fromisoformat("2026-04-19 00:42:38.836565")
    assert ArexClient._to_epoch_ms(dt) == 1776559358836


@pytest.mark.asyncio
async def test_remove_sub_invocation_recordings_falls_back_to_internal_uri_and_loopback_httpclient_path(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "cleanup-internal").json()["id"]

    async with database.async_session_factory() as db:
        db.add_all(
            [
                Recording(
                    session_id=sess_id,
                    application_id=app_id,
                    record_id="main-1",
                    request_method="POST",
                    request_uri="/api/car/service",
                    request_headers='{"host":"172.25.109.28:18081"}',
                    request_body="<request><code>car000001</code></request>",
                    response_status=200,
                    response_body="<response/>",
                ),
                Recording(
                    session_id=sess_id,
                    application_id=app_id,
                    record_id="internal-1",
                    request_method="GET",
                    request_uri="/internal/didi/risk",
                    request_headers='{"host":"172.25.109.28:18081"}',
                    request_body="",
                    response_status=200,
                    response_body="{}",
                ),
                Recording(
                    session_id=sess_id,
                    application_id=app_id,
                    record_id="internal-2",
                    request_method="GET",
                    request_uri="/api/healthz",
                    request_headers='{"host":"127.0.0.1:18081"}',
                    request_body="",
                    response_status=200,
                    response_body="{}",
                ),
                ArexMocker(
                    record_id="main-1",
                    app_id="didi-car-sat",
                    category_name="HttpClient",
                    is_entry_point=False,
                    mocker_data=json.dumps(
                        {
                            "operationName": "/api/healthz",
                            "targetRequest": {
                                "body": None,
                                "attributes": {"HttpMethod": "GET"},
                            },
                            "targetResponse": {
                                "body": json.dumps({"status": "UP"}),
                                "attributes": None,
                            },
                        }
                    ),
                    created_at_ms=1776562276902,
                ),
            ]
        )
        await db.commit()

    async with database.async_session_factory() as db:
        removed = await _remove_sub_invocation_recordings(sess_id, db)
        await db.commit()

    assert removed == 2

    async with database.async_session_factory() as db:
        rows = (
            await db.execute(
                select(Recording.record_id).where(Recording.session_id == sess_id).order_by(Recording.id)
            )
        ).scalars().all()
    assert rows == ["main-1"]


@pytest.mark.asyncio
async def test_remove_sub_invocation_recordings_keeps_main_request_when_user_calls_loopback_host(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "keep-loopback-main").json()["id"]

    async with database.async_session_factory() as db:
        db.add(
            Recording(
                session_id=sess_id,
                application_id=app_id,
                record_id="main-loopback",
                request_method="POST",
                request_uri="/api/car/service",
                request_headers='{"host":"127.0.0.1:18081"}',
                request_body="<request><code>car000001</code></request>",
                response_status=200,
                response_body="<response/>",
            )
        )
        await db.commit()

    async with database.async_session_factory() as db:
        removed = await _remove_sub_invocation_recordings(sess_id, db)
        await db.commit()

    assert removed == 0

    async with database.async_session_factory() as db:
        rows = (
            await db.execute(
                select(Recording.record_id).where(Recording.session_id == sess_id).order_by(Recording.id)
            )
        ).scalars().all()
    assert rows == ["main-loopback"]


def test_extract_sub_calls_filters_time_noise_dynamic_class():
    detail = {
        "subCallInfo": [
            {
                "type": "DynamicClass",
                "operationName": "java.lang.System.currentTimeMillis",
                "response": 1776562276901,
            },
            {
                "type": "HttpClient",
                "operationName": "/internal/didi/risk",
                "request": {"txnCode": "car000001"},
                "response": {"decision": "AUTO_PASS"},
            },
        ]
    }

    sub_calls = _extract_sub_calls(detail, {})

    assert len(sub_calls) == 1
    assert sub_calls[0]["type"] == "HttpClient"
    assert sub_calls[0]["operation"] == "/internal/didi/risk"


@pytest.mark.asyncio
async def test_fetch_dynamic_class_sub_calls_filters_time_noise_from_arex_mocker(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "dynamic-noise").json()["id"]

    async with database.async_session_factory() as db:
        db.add_all(
            [
                ArexMocker(
                    record_id="rid-1",
                    app_id="didi-car-sat",
                    category_name="DynamicClass",
                    is_entry_point=False,
                    mocker_data=json.dumps(
                        {
                            "operationName": "java.lang.System.currentTimeMillis",
                            "targetRequest": {"body": None, "attributes": None},
                            "targetResponse": {"body": "1776562276901", "attributes": None},
                        }
                    ),
                    created_at_ms=1776562276901,
                ),
                ArexMocker(
                    record_id="rid-1",
                    app_id="didi-car-sat",
                    category_name="HttpClient",
                    is_entry_point=False,
                    mocker_data=json.dumps(
                        {
                            "operationName": "/internal/didi/risk",
                            "targetRequest": {
                                "body": json.dumps({"txnCode": "car000001"}),
                                "attributes": {"HttpMethod": "GET"},
                            },
                            "targetResponse": {
                                "body": json.dumps({"decision": "AUTO_PASS"}),
                                "attributes": None,
                            },
                        }
                    ),
                    created_at_ms=1776562276902,
                ),
            ]
        )
        await db.commit()

    async with database.async_session_factory() as db:
        sub_calls = await _fetch_dynamic_class_sub_calls("rid-1", db)

    assert len(sub_calls) == 1
    assert sub_calls[0]["type"] == "HttpClient"
    assert sub_calls[0]["operation"] == "/internal/didi/risk"


@pytest.mark.asyncio
async def test_fetch_dynamic_class_sub_calls_normalizes_repository_methods_to_mysql(
    client, admin_headers, created_app
):
    _create_session(client, created_app["id"], admin_headers, "dynamic-repository")

    async with database.async_session_factory() as db:
        db.add_all(
            [
                ArexMocker(
                    record_id="rid-db-1",
                    app_id="didi-car-sat",
                    category_name="DynamicClass",
                    is_entry_point=False,
                    mocker_data=json.dumps(
                        {
                            "operationName": "com.arex.demo.didi.common.repository.CarDataRepository.findVehicle",
                            "targetRequest": {
                                "body": json.dumps(["沪A12345", "VIN001"]),
                                "attributes": None,
                            },
                            "targetResponse": {
                                "body": json.dumps({"plate_no": "沪A12345", "owner_customer_no": "C10001"}),
                                "attributes": None,
                            },
                        }
                    ),
                    created_at_ms=1776562276910,
                ),
                ArexMocker(
                    record_id="rid-db-1",
                    app_id="didi-car-sat",
                    category_name="DynamicClass",
                    is_entry_point=False,
                    mocker_data=json.dumps(
                        {
                            "operationName": "com.arex.demo.didi.common.repository.CarDataRepository.saveAudit",
                            "targetRequest": {
                                "body": json.dumps([
                                    "car000001",
                                    "REQ-001",
                                    "C10001",
                                    "沪A12345",
                                    "LOW",
                                    "1280.50",
                                    "sat",
                                ]),
                                "attributes": None,
                            },
                            "targetResponse": {
                                "body": None,
                                "attributes": None,
                            },
                        }
                    ),
                    created_at_ms=1776562276911,
                ),
            ]
        )
        await db.commit()

    async with database.async_session_factory() as db:
        sub_calls = await _fetch_dynamic_class_sub_calls("rid-db-1", db)

    assert len(sub_calls) == 2
    assert sub_calls[0]["type"] == "MySQL"
    assert sub_calls[0]["source"] == "agent"
    assert sub_calls[0]["table"] == "car_vehicle"
    assert sub_calls[0]["operation"] == "SELECT car_vehicle"
    assert sub_calls[0]["params"]["plateNo"] == "沪A12345"
    assert sub_calls[0]["params"]["vin"] == "VIN001"
    assert sub_calls[1]["type"] == "MySQL"
    assert sub_calls[1]["source"] == "agent"
    assert sub_calls[1]["table"] == "car_order_audit"
    assert sub_calls[1]["operation"] == "INSERT car_order_audit"
    assert sub_calls[1]["status"] == "WRITE"
    assert sub_calls[1]["params"]["requestNo"] == "REQ-001"


def test_proxy_config_exposes_car_data_repository_dynamic_class_rules(client):
    resp = client.post("/api/config/agent/load", json={"appId": "didi-car-sat"})
    assert resp.status_code == 200
    body = resp.json()
    rules = body["body"]["dynamicClassConfigurationList"]
    assert any(
        item["fullClassName"] == "com.arex.demo.didi.common.repository.CarDataRepository"
        and item["methodName"] == "findVehicle"
        for item in rules
    )
    assert any(
        item["fullClassName"] == "com.arex.demo.didi.common.repository.CarDataRepository"
        and item["methodName"] == "saveAudit"
        for item in rules
    )


@pytest.mark.asyncio
async def test_sync_session_keeps_total_count_as_session_total_and_parses_operation_name(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    query_side_effect = [
        {"body": [{"recordId": "r-1"}, {"recordId": "r-2"}]},
        {"body": [{"recordId": "r-2"}, {"recordId": "r-3"}]},
    ]

    async def fake_view_recording(*args):
        record_id = args[-1]
        return {
            "operationName": {
                "r-1": "GET /api/orders/1",
                "r-2": "POST /api/orders",
                "r-3": "DELETE /api/orders/3",
            }[record_id],
            "requestHeaders": {"Content-Type": "application/json"},
            "targetRequest": "<xml><id>r-3</id></xml>" if record_id == "r-3" else {"id": record_id},
            "responseStatusCode": 200,
            "targetResponse": "<xml><ok>true</ok></xml>" if record_id == "r-3" else {"ok": True},
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=query_side_effect)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 3

    async with database.async_session_factory() as db:
        rows = (
            await db.execute(
                select(Recording).where(Recording.session_id == sess_id).order_by(Recording.record_id)
            )
        ).scalars().all()

    assert [row.record_id for row in rows] == ["r-1", "r-2", "r-3"]
    assert rows[0].request_method == "GET"
    assert rows[0].request_uri == "/api/orders/1"
    assert rows[1].request_method == "POST"
    assert rows[1].request_uri == "/api/orders"
    assert rows[2].request_body == "<xml><id>r-3</id></xml>"
    assert rows[2].response_body == "<xml><ok>true</ok></xml>"


@pytest.mark.asyncio
async def test_sync_recordings_merges_detail_http_and_repository_db_sub_calls(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "merge-http-db").json()["id"]

    async with database.async_session_factory() as db:
        db.add(
            ArexMocker(
                record_id="merge-1",
                app_id="didi-car-sat",
                category_name="DynamicClass",
                is_entry_point=False,
                mocker_data=json.dumps(
                    {
                        "operationName": "com.arex.demo.didi.common.repository.CarDataRepository.findCustomer",
                        "targetRequest": {"body": json.dumps(["C10001"]), "attributes": None},
                        "targetResponse": {"body": json.dumps({"customer_no": "C10001"}), "attributes": None},
                    }
                ),
                created_at_ms=1776562276950,
            )
        )
        await db.commit()

    async def fake_query_recordings(*args, **kwargs):
        return {"body": [{"recordId": "merge-1"}]}

    async def fake_view_recording(record_id):
        return {
            "operationName": "POST /api/car/service",
            "targetRequest": {
                "body": "<request><transaction_id>car000001</transaction_id></request>",
                "attributes": {
                    "Headers": {"Content-Type": "text/xml"},
                    "HttpMethod": "POST",
                    "RequestPath": "/api/car/service",
                },
            },
            "targetResponse": {
                "body": "<response><code>0000</code></response>",
            },
            "subCallInfo": [
                {
                    "type": "HttpClient",
                    "operationName": "/internal/didi/risk",
                    "request": {"txnCode": "car000001"},
                    "response": {"decision": "AUTO_PASS"},
                }
            ],
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=fake_query_recordings)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    sub_calls = body[0]["sub_calls"]
    assert len(sub_calls) == 2
    assert any(item["type"] == "HttpClient" and item["operation"] == "/internal/didi/risk" for item in sub_calls)
    assert any(item["type"] == "MySQL" and item["operation"] == "SELECT car_customer" for item in sub_calls)


@pytest.mark.asyncio
async def test_fetch_didi_sub_calls_reconstructs_complex_transaction_db_steps():
    request_body = """
    <request>
      <code>car000001</code>
      <request_no>REQ-car000001-live</request_no>
      <customer_no>C10001</customer_no>
      <plate_no>沪A10001</plate_no>
      <vin>VIN0000000000000001</vin>
      <policy_no>P10001</policy_no>
      <claim_no>CL10001</claim_no>
      <garage_code>G001</garage_code>
      <city>SHANGHAI</city>
    </request>
    """

    cursor = AsyncMock()
    cursor.description = []
    desc_by_sql = {
        "FROM car_vehicle": [("plate_no",), ("owner_customer_no",), ("vehicle_status",)],
        "FROM car_customer": [("customer_no",), ("tier_level",)],
        "FROM car_policy": [("policy_no",), ("policy_status",)],
        "FROM car_claim": [("claim_no",), ("claim_status",)],
        "FROM car_dispatch": [("dispatch_no",), ("city",)],
        "FROM car_order_audit": [("request_no",), ("txn_code",), ("plate_no",)],
    }

    async def _execute(sql, params=None):
        for marker, desc in desc_by_sql.items():
            if marker in sql:
                cursor.description = desc
                return

    cursor.execute = _execute
    cursor.fetchone = AsyncMock(side_effect=[
        ("沪A10001", "C10001", "ACTIVE"),
        ("C10001", "VIP"),
        ("P10001", "VALID"),
        ("CL10001", "OPEN"),
        ("D10001", "SHANGHAI"),
        ("REQ-car000001-live", "car000001", "沪A10001"),
        ("沪A10001", "C10001", "ACTIVE"),
    ])

    conn = AsyncMock()
    conn.cursor = AsyncMock(return_value=cursor)
    conn.close = MagicMock()

    with patch("api.v1.sessions.settings") as mock_settings, \
         patch("aiomysql.connect", AsyncMock(return_value=conn)):
        mock_settings.didi_mysql_host = "127.0.0.1"
        mock_settings.didi_mysql_port = 3307
        mock_settings.didi_mysql_user = "root"
        mock_settings.didi_mysql_password = "root123"
        mock_settings.didi_mysql_db_sat = "didi_alpha"
        mock_settings.didi_mysql_db_uat = "didi_beta"

        sub_calls = await _fetch_didi_sub_calls(request_body, "didi-car-sat")

    assert len(sub_calls) == 7
    assert sub_calls[0]["operation"] == "SELECT car_vehicle"
    assert sub_calls[0]["source"] == "reconstructed"
    assert sub_calls[0]["response"]["plate_no"] == "沪A10001"
    assert sub_calls[1]["operation"] == "SELECT car_customer"
    assert sub_calls[1]["response"]["tier_level"] == "VIP"
    assert sub_calls[5]["operation"] == "INSERT car_order_audit"
    assert sub_calls[5]["source"] == "reconstructed"
    assert sub_calls[5]["status"] == "WRITE"
    assert sub_calls[6]["operation"] == "UPDATE car_vehicle"
    assert sub_calls[6]["params"]["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_sync_recordings_extracts_transaction_code_and_supports_governance_filters(
    client, admin_headers, created_app, caplog
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    async def fake_query_recordings(*args, **kwargs):
        return {"body": [{"recordId": "tx-1"}, {"recordId": "tx-2"}]}

    async def fake_view_recording(record_id):
        return {
            "operationName": "POST /api/bank/service",
            "targetRequest": f"""
              <request>
                <service_id>{'OPEN_ACCOUNT' if record_id == 'tx-1' else 'OPEN_ACCOUNT'}</service_id>
                <customer_no>C001</customer_no>
              </request>
            """,
            "responseStatusCode": 200,
            "targetResponse": "<response><code>0000</code></response>",
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=fake_query_recordings)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        with caplog.at_level(logging.INFO, logger="uvicorn.error"):
            await _sync_from_arex_storage(
                session_id=sess_id,
                application_id=app_id,
                begin_time=None,
                end_time=None,
                page_size=50,
                page_index=0,
            )

    resp = client.get(
        f"/api/v1/sessions/{sess_id}/recordings?transaction_code=OPEN_ACCOUNT",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert all(item["transaction_code"] == "OPEN_ACCOUNT" for item in body)
    assert all(item["governance_status"] == "raw" for item in body)
    assert all(item["duplicate_count"] == 2 for item in body)
    assert "同步会话" in caplog.text
    assert "transaction_code=OPEN_ACCOUNT" in caplog.text
    assert "uri=/api/bank/service" in caplog.text

    update_resp = client.patch(
        f"/api/v1/sessions/recordings/{body[0]['id']}",
        json={"governance_status": "candidate"},
        headers=admin_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["governance_status"] == "candidate"

    filtered = client.get(
        f"/api/v1/sessions/{sess_id}/recordings?governance_status=candidate",
        headers=admin_headers,
    )
    assert filtered.status_code == 200
    assert [item["id"] for item in filtered.json()] == [body[0]["id"]]


@pytest.mark.asyncio
async def test_sync_recordings_normalizes_sub_calls_for_database_details(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    async def fake_query_recordings(*args, **kwargs):
        return {"body": [{"recordId": "db-1"}]}

    async def fake_view_recording(record_id):
        request_body = base64.b64encode(
            b"<request><service_id>OPEN_ACCOUNT</service_id></request>"
        ).decode()
        response_body = base64.b64encode(
            b"<response><code>0000</code><msg>ok</msg></response>"
        ).decode()
        return {
            "operationName": "POST /api/bank/service",
            "targetRequest": {
                "body": request_body,
                "attributes": {
                    "Headers": {"Content-Type": "text/xml"},
                    "HttpMethod": "POST",
                    "RequestPath": "/api/bank/service",
                },
            },
            "targetResponse": {
                "body": response_body,
            },
            "subCallInfo": [
                {
                    "callType": "MySQL",
                    "request": {"sql": "SELECT * FROM account WHERE id = 1"},
                    "params": {"id": 1},
                    "database": "bank",
                    "table": "account",
                    "operationName": "selectAccount",
                    "traceId": "trace-1",
                    "response": {"rows": [{"account_no": "62226222000000033"}]},
                    "elapsedMs": 12,
                    "children": [
                        {
                            "type": "Redis",
                            "request": "GET account:1",
                            "response": "HIT",
                            "duration": 3,
                            "endpoint": "redis://cache-1",
                            "children": [
                                {
                                    "type": "RPC",
                                    "request": {"method": "loadCacheWarmup"},
                                    "response": {"status": "ok"},
                                    "elapsedMs": 1,
                                    "traceId": "trace-redis-1",
                                }
                            ],
                        }
                    ],
                },
                {
                    "type": "Redis",
                    "request": "GET account:1",
                    "response": "HIT",
                    "duration": 3,
                },
            ],
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=fake_query_recordings)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert isinstance(body[0]["sub_calls"], list)
    assert body[0]["sub_calls"][0]["type"] == "MySQL"
    assert body[0]["sub_calls"][0]["database"] == "bank"
    assert body[0]["sub_calls"][0]["operation"] == "selectAccount"
    assert body[0]["sub_calls"][0]["trace_id"] == "trace-1"
    assert body[0]["sub_calls"][0]["sql"] == "SELECT * FROM account WHERE id = 1"
    assert body[0]["sub_calls"][0]["params"]["id"] == 1
    assert body[0]["sub_calls"][0]["request"]["sql"] == "SELECT * FROM account WHERE id = 1"
    assert body[0]["sub_calls"][0]["response"]["rows"][0]["account_no"] == "62226222000000033"
    assert body[0]["sub_calls"][0]["children"][0]["type"] == "Redis"
    assert body[0]["sub_calls"][0]["children"][0]["children"][0]["type"] == "RPC"
    assert body[0]["sub_calls"][0]["children"][0]["children"][0]["trace_id"] == "trace-redis-1"
    assert body[0]["sub_calls"][0]["children"][0]["endpoint"] == "redis://cache-1"
    assert body[0]["sub_calls"][1]["type"] == "Redis"
    assert body[0]["sub_calls"][1]["request"] == "GET account:1"


@pytest.mark.asyncio
async def test_sync_recordings_filters_by_transaction_code_rules(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_resp = client.post(
        "/api/v1/sessions",
        json={
            "application_id": app_id,
            "name": "filter-car001",
            "recording_filter_prefixes": ["car001", "=car002_detail", "re:^car003.*$"],
        },
        headers=admin_headers,
    )
    assert sess_resp.status_code == 201
    sess_id = sess_resp.json()["id"]

    async def fake_query_recordings(*args, **kwargs):
        return {"body": [{"recordId": "keep-prefix"}, {"recordId": "keep-exact"}, {"recordId": "keep-regex"}, {"recordId": "drop-1"}]}

    async def fake_view_recording(record_id):
        mapping = {
            "keep-prefix": ("car001_open", "tx_code"),
            "keep-exact": ("car002_detail", "rct_code"),
            "keep-regex": ("car003_query", "tx_code"),
            "drop-1": ("car004_misc", "rct_code"),
        }
        code, tag_name = mapping[record_id]
        return {
            "operationName": "POST /api/bank/service",
            "targetRequest": f"<request><{tag_name}>{code}</{tag_name}></request>",
            "targetResponse": "<response><code>0000</code></response>",
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=fake_query_recordings)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            recording_filter_prefixes=["car001", "=car002_detail", "re:^car003.*$"],
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 3
    assert resp.json()["recording_filter_prefixes"] == ["car001", "=car002_detail", "re:^car003.*$"]

    recordings_resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert recordings_resp.status_code == 200
    recordings = recordings_resp.json()
    assert len(recordings) == 3
    assert {item["transaction_code"] for item in recordings} == {"car001_open", "car002_detail", "car003_query"}


@pytest.mark.asyncio
async def test_recording_detail_exposes_recursive_sub_calls_and_alias_fields(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    async def fake_query_recordings(*args, **kwargs):
        return {"body": [{"recordId": "db-2"}]}

    async def fake_view_recording(record_id):
        return {
            "operationName": "POST /api/bank/service",
            "targetRequest": {
                "body": base64.b64encode(
                    b"<request><service_id>OPEN_ACCOUNT</service_id></request>"
                ).decode(),
                "attributes": {
                    "Headers": {"Content-Type": "text/xml"},
                    "HttpMethod": "POST",
                    "RequestPath": "/api/bank/service",
                },
            },
            "targetResponse": {
                "body": base64.b64encode(b"<response><code>0000</code></response>").decode(),
            },
            "subInvocations": [
                {
                    "name": "MySQL",
                    "statement": "SELECT id, account_no FROM account WHERE id = ?",
                    "arguments": {"id": 1},
                    "dbName": "bank",
                    "tableName": "account",
                    "methodName": "selectAccount",
                    "spanId": "span-1",
                    "parentId": "root-span",
                    "threadName": "http-nio-8080-exec-1",
                    "children": [
                        {
                            "name": "Redis",
                            "command": "GET account:1",
                            "response": "HIT",
                            "elapsed": 2,
                            "endpoint": "redis://cache-1",
                        }
                    ],
                }
            ],
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=fake_query_recordings)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1

    recording = body[0]
    assert recording["sub_calls"][0]["type"] == "MySQL"
    assert recording["sub_calls"][0]["sql"] == "SELECT id, account_no FROM account WHERE id = ?"
    assert recording["sub_calls"][0]["params"]["id"] == 1
    assert recording["sub_calls"][0]["database"] == "bank"
    assert recording["sub_calls"][0]["table"] == "account"
    assert recording["sub_calls"][0]["operation"] == "selectAccount"
    assert recording["sub_calls"][0]["span_id"] == "span-1"
    assert recording["sub_calls"][0]["parent_id"] == "root-span"
    assert recording["sub_calls"][0]["thread_name"] == "http-nio-8080-exec-1"
    assert recording["sub_calls"][0]["children"][0]["type"] == "Redis"
    assert recording["sub_calls"][0]["children"][0]["request"] == "GET account:1"

    detail = client.get(f"/api/v1/sessions/recordings/{recording['id']}", headers=admin_headers)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert isinstance(detail_body["sub_calls"], list)
    assert detail_body["sub_calls"][0]["children"][0]["type"] == "Redis"
    assert detail_body["sub_calls"][0]["children"][0]["endpoint"] == "redis://cache-1"
    assert detail_body["sub_calls"][0]["children"][0]["elapsed_ms"] == 2.0


def test_recording_groups_select_preferred_representative(client, admin_headers, created_app):
    import asyncio
    from datetime import datetime, timedelta, timezone
    from models.recording import Recording

    async def _seed():
        async with database.async_session_factory() as db:
            base = datetime.now(timezone.utc)
            rows = [
                Recording(
                    application_id=created_app["id"],
                    request_method="POST",
                    request_uri="/api/bank/service",
                    request_body="<request><service_id>OPEN_ACCOUNT</service_id></request>",
                    response_status=200,
                    response_body="<response/>",
                    transaction_code="OPEN_ACCOUNT",
                    scene_key="OPEN_ACCOUNT|POST|/api/bank/service|success",
                    dedupe_hash="hash-1",
                    governance_status="raw",
                    recorded_at=base,
                ),
                Recording(
                    application_id=created_app["id"],
                    request_method="POST",
                    request_uri="/api/bank/service",
                    request_body="<request><service_id>OPEN_ACCOUNT</service_id></request>",
                    response_status=200,
                    response_body="<response/>",
                    transaction_code="OPEN_ACCOUNT",
                    scene_key="OPEN_ACCOUNT|POST|/api/bank/service|success",
                    dedupe_hash="hash-2",
                    governance_status="approved",
                    recorded_at=base - timedelta(minutes=5),
                ),
            ]
            db.add_all(rows)
            await db.commit()
            for row in rows:
                await db.refresh(row)
            return rows

    rows = asyncio.get_event_loop().run_until_complete(_seed())
    resp = client.get(
        f"/api/v1/sessions/recordings/groups?application_id={created_app['id']}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["transaction_code"] == "OPEN_ACCOUNT"
    assert body[0]["approved_count"] == 1
    assert body[0]["raw_count"] == 1
    assert body[0]["representative_recording_id"] == rows[1].id
