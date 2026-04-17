"""Tests for recording session CRUD, recording listing, and session sync."""
import base64
import pytest
from unittest.mock import AsyncMock, patch

import database
from sqlalchemy import select
from api.v1.sessions import _sync_from_arex_storage
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
      <transaction_id>A0201M14I</transaction_id>
      <SYS_EVT_TRACE_ID>1234567890123456789012345</SYS_EVT_TRACE_ID>
    </request>
    """

    assert infer_transaction_code(xml) == "A0201M14I"


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
async def test_sync_recordings_extracts_transaction_code_and_supports_governance_filters(
    client, admin_headers, created_app
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
            "name": "filter-a0201",
            "recording_filter_prefixes": ["A0201", "=B0301M01A", "re:^C0901.*$"],
        },
        headers=admin_headers,
    )
    assert sess_resp.status_code == 201
    sess_id = sess_resp.json()["id"]

    async def fake_query_recordings(*args, **kwargs):
        return {"body": [{"recordId": "keep-prefix"}, {"recordId": "keep-exact"}, {"recordId": "keep-regex"}, {"recordId": "drop-1"}]}

    async def fake_view_recording(record_id):
        mapping = {
            "keep-prefix": ("A0201M14I", "tx_code"),
            "keep-exact": ("B0301M01A", "rct_code"),
            "keep-regex": ("C0901XYZ", "tx_code"),
            "drop-1": ("D0101X01", "rct_code"),
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
            recording_filter_prefixes=["A0201", "=B0301M01A", "re:^C0901.*$"],
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 3
    assert resp.json()["recording_filter_prefixes"] == ["A0201", "=B0301M01A", "re:^C0901.*$"]

    recordings_resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert recordings_resp.status_code == 200
    recordings = recordings_resp.json()
    assert len(recordings) == 3
    assert {item["transaction_code"] for item in recordings} == {"A0201M14I", "B0301M01A", "C0901XYZ"}


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
