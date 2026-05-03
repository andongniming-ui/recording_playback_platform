"""Tests for recording session CRUD, recording listing, and session sync."""
import asyncio
import base64
import json
import logging
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import database
from sqlalchemy import select, update
from api.v1.sessions import (
    _count_visible_recordings_from_arex,
    _extract_sub_calls,
    _fetch_didi_sub_calls,
    _fetch_dynamic_class_sub_calls,
    _remove_sub_invocation_recordings,
    _sync_active_session_preview,
    _sync_from_arex_storage,
)
from integration.arex_client import ArexClient
from models.arex_mocker import ArexMocker
from models.audit import RecordingAuditLog
from models.recording import Recording, RecordingSession
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


@pytest.mark.asyncio
async def test_active_count_uses_remote_count_when_details_lag():
    class FakeArexClient:
        async def count_recordings(self, **_kwargs):
            return 3

        async def query_recordings(self, **_kwargs):
            return {"records": []}

    count = await _count_visible_recordings_from_arex(
        FakeArexClient(),
        app_id="loan-jar",
        begin_time=datetime.fromisoformat("2026-04-22T10:00:00+00:00"),
        end_time=datetime.fromisoformat("2026-04-22T10:05:00+00:00"),
    )

    assert count == 3


@pytest.mark.asyncio
async def test_active_count_applies_transaction_code_filter_to_remote_records():
    class FakeArexClient:
        async def count_recordings(self, **_kwargs):
            return 3

        async def query_recordings(self, **_kwargs):
            return {
                "records": [
                    {
                        "targetRequest": {
                            "attributes": {
                                "HttpMethod": "GET",
                                "RequestPath": "/repeater/query?code=RP54KH01&idcard=440203198709237790",
                            }
                        }
                    },
                    {
                        "targetRequest": {
                            "attributes": {
                                "HttpMethod": "GET",
                                "RequestPath": "/order/query?idcard=440203198709237790",
                            }
                        }
                    },
                    {
                        "targetRequest": {
                            "attributes": {
                                "HttpMethod": "GET",
                                "RequestPath": "/repeater/query?code=OTHER&idcard=440203198709237790",
                            }
                        }
                    },
                ]
            }

    count = await _count_visible_recordings_from_arex(
        FakeArexClient(),
        app_id="credit",
        begin_time=datetime.fromisoformat("2026-04-30T10:00:00+00:00"),
        end_time=datetime.fromisoformat("2026-04-30T10:05:00+00:00"),
        recording_filter_prefixes=["=RP54KH01"],
        transaction_code_fields=["code"],
    )

    assert count == 1


def test_list_sessions_supports_created_at_sort_order(client, admin_headers, created_app):
    app_id = created_app["id"]
    first = _create_session(client, app_id, admin_headers, "sort-a").json()
    second = _create_session(client, app_id, admin_headers, "sort-b").json()

    async def _seed_order():
        async with database.async_session_factory() as db:
            await db.execute(
                update(database.Base.metadata.tables["recording_session"])
                .where(database.Base.metadata.tables["recording_session"].c.id == first["id"])
                .values(created_at=datetime.fromisoformat("2026-04-21T09:00:00"))
            )
            await db.execute(
                update(database.Base.metadata.tables["recording_session"])
                .where(database.Base.metadata.tables["recording_session"].c.id == second["id"])
                .values(created_at=datetime.fromisoformat("2026-04-21T10:00:00"))
            )
            await db.commit()

    asyncio.get_event_loop().run_until_complete(_seed_order())

    asc_resp = client.get(
        "/api/v1/sessions",
        params={"application_id": app_id, "sort_by": "created_at", "sort_order": "asc"},
        headers=admin_headers,
    )
    assert asc_resp.status_code == 200
    asc_ids = [item["id"] for item in asc_resp.json()[:2]]
    assert asc_ids == [first["id"], second["id"]]

    desc_resp = client.get(
        "/api/v1/sessions",
        params={"application_id": app_id, "sort_by": "created_at", "sort_order": "desc"},
        headers=admin_headers,
    )
    assert desc_resp.status_code == 200
    desc_ids = [item["id"] for item in desc_resp.json()[:2]]
    assert desc_ids == [second["id"], first["id"]]


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


def test_bulk_delete_sessions_blocks_active_and_deletes_idle(client, admin_headers, created_app):
    app_id = created_app["id"]
    idle_id = _create_session(client, app_id, admin_headers, "idle-session").json()["id"]
    active_id = _create_session(client, app_id, admin_headers, "active-session").json()["id"]

    start_resp = client.post(f"/api/v1/sessions/{active_id}/start", headers=admin_headers)
    assert start_resp.status_code == 200

    blocked = client.post(
        "/api/v1/sessions/bulk-delete",
        json={"ids": [idle_id, active_id]},
        headers=admin_headers,
    )
    assert blocked.status_code == 409

    deleted = client.post(
        "/api/v1/sessions/bulk-delete",
        json={"ids": [idle_id]},
        headers=admin_headers,
    )
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] == 1

    missing = client.get(f"/api/v1/sessions/{idle_id}", headers=admin_headers)
    assert missing.status_code == 404


def test_create_session_invalid_app(client, admin_headers):
    resp = client.post(
        "/api/v1/sessions",
        json={"application_id": 9999, "name": "orphan"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_start_stop_session_flow_and_sync_alias(client):
    from api.v1.sessions import _enqueue_collection, sync_recordings
    from models.application import Application
    from models.recording import RecordingSession
    from schemas.recording import SyncRequest
    from fastapi import HTTPException

    scheduled = {}

    def _fake_create_task(coro, *, name=None):
        scheduled["name"] = name
        coro.close()
        task = MagicMock()
        task.add_done_callback = MagicMock()
        return task

    async def _run():
        async with database.async_session_factory() as db:
            app = Application(
                name="test-app",
                ssh_host="127.0.0.1",
                ssh_user="tester",
                ssh_port=22,
                service_port=8080,
                agent_status="offline",
                sample_rate=1.0,
            )
            db.add(app)
            await db.commit()
            await db.refresh(app)

            sess = RecordingSession(
                application_id=app.id,
                name="start-stop-session",
                status="active",
                start_time=datetime.fromisoformat("2026-04-22T10:00:00+00:00"),
                total_count=0,
            )
            db.add(sess)
            await db.commit()
            await db.refresh(sess)

            with patch("api.v1.sessions.asyncio.create_task", side_effect=_fake_create_task) as create_task_mock:
                out = await _enqueue_collection(sess.id, sess, SyncRequest(), db)

            assert out["status"] == "collecting"
            create_task_mock.assert_called_once()
            assert scheduled["name"] == f"recording-sync-{sess.id}"

            await db.refresh(sess)
            assert sess.status == "collecting"

            with pytest.raises(HTTPException) as exc_info:
                await sync_recordings(sess.id, SyncRequest(), db, None)
            assert exc_info.value.status_code == 409

    asyncio.get_event_loop().run_until_complete(_run())


def test_session_audit_logs_capture_sync_flow(client, admin_headers, created_app):
    app_id = created_app["id"]
    session = _create_session(client, app_id, admin_headers, "audit-session").json()

    async def _fake_count(*args, **kwargs):
        return 1

    async def _fake_query(*args, **kwargs):
        if kwargs.get("page_index", 0) == 0:
            return {"records": [{"recordId": "RID-1", "creationTime": 1776952806632}]}
        return {"records": []}

    async def _fake_view(_record_id):
        return {
            "recordId": "RID-1",
            "creationTime": 1776952806632,
            "responseStatusCode": 200,
            "operationName": "POST /credit/gateway",
            "targetRequest": {
                "body": "<request><txn_code>CRD_ADMIT</txn_code></request>",
                "attributes": {
                    "HttpMethod": "POST",
                    "RequestPath": "/credit/gateway",
                    "Headers": {"content-type": "application/xml"},
                },
            },
            "targetResponse": {
                "body": "<response><status>SUCCESS</status></response>",
            },
        }

    async def _run():
        with (
            patch.object(ArexClient, "count_recordings", new=AsyncMock(side_effect=_fake_count)),
            patch.object(ArexClient, "query_recordings", new=AsyncMock(side_effect=_fake_query)),
            patch.object(ArexClient, "view_recording", new=AsyncMock(side_effect=_fake_view)),
            patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        ):
            await _sync_from_arex_storage(
                session_id=session["id"],
                application_id=app_id,
                finalize_session=True,
            )

    asyncio.get_event_loop().run_until_complete(_run())

    resp = client.get(f"/api/v1/sessions/{session['id']}/audit-logs", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    event_types = {item["event_type"] for item in body}
    assert {"sync_started", "page_fetched", "record_saved", "sync_finished"} <= event_types
    assert any(item["request_uri"] == "/credit/gateway" for item in body if item["event_type"] == "record_saved")
    saved_entry = next(item for item in body if item["event_type"] == "record_saved")

    filtered_resp = client.get(
        f"/api/v1/sessions/{session['id']}/audit-logs",
        params={
            "event_type": "record_saved",
            "record_id": "RID-1",
            "transaction_code": "CRD_ADMIT",
            "recording_id": saved_entry["recording_id"],
        },
        headers=admin_headers,
    )
    assert filtered_resp.status_code == 200, filtered_resp.text
    filtered_body = filtered_resp.json()
    assert len(filtered_body) == 1
    assert filtered_body[0]["record_id"] == "RID-1"

    async def _count_audits():
        async with database.async_session_factory() as db:
            result = await db.execute(
                select(RecordingAuditLog).where(RecordingAuditLog.session_id == session["id"])
            )
            return result.scalars().all()

    assert len(asyncio.get_event_loop().run_until_complete(_count_audits())) >= 4


def test_enqueue_collection_schedules_detached_async_task(client, admin_headers, created_app):
    from api.v1.sessions import _enqueue_collection
    from schemas.recording import SyncRequest
    from models.recording import RecordingSession

    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "enqueue-collection").json()["id"]

    scheduled = {}

    def _fake_create_task(coro, *, name=None):
        scheduled["name"] = name
        coro.close()
        task = MagicMock()
        task.add_done_callback = MagicMock()
        return task

    async def _run():
        async with database.async_session_factory() as db:
            sess = (
                await db.execute(select(RecordingSession).where(RecordingSession.id == sess_id))
            ).scalar_one()
            sess.status = "active"
            sess.start_time = datetime.fromisoformat("2026-04-22T10:00:00")
            await db.commit()
            await db.refresh(sess)

            with (
                patch("api.v1.sessions._sync_from_arex_storage", new=AsyncMock(return_value=None)) as sync_mock,
                patch("api.v1.sessions.asyncio.create_task", side_effect=_fake_create_task) as create_task_mock,
            ):
                out = await _enqueue_collection(sess_id, sess, SyncRequest(), db)

            assert out["status"] == "collecting"
            create_task_mock.assert_called_once()
            assert scheduled["name"] == f"recording-sync-{sess_id}"
            sync_mock.assert_called_once()
            _, kwargs = sync_mock.call_args
            assert kwargs["begin_time"].isoformat() == "2026-04-22T10:00:00+08:00"
            assert kwargs["end_time"].tzinfo is not None

            await db.refresh(sess)
            assert sess.status == "collecting"

    asyncio.get_event_loop().run_until_complete(_run())


# ---------------------------------------------------------------------------
# Recording listing
# ---------------------------------------------------------------------------

def test_list_recordings_empty(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_recording_delete_bulk_delete_and_sort_refresh_session_total_count(client, admin_headers, created_app):
    app_id = created_app["id"]
    session_id = _create_session(client, app_id, admin_headers, "recording-sort").json()["id"]

    async def _seed_recordings():
        async with database.async_session_factory() as db:
            db.add_all(
                [
                    Recording(
                        session_id=session_id,
                        application_id=app_id,
                        request_method="POST",
                        request_uri="/api/car/service",
                        request_body="<request><code>car000001</code></request>",
                        response_status=200,
                        response_body="<response/>",
                        transaction_code="car000001",
                        dedupe_hash="rec-sort-1",
                        recorded_at=datetime.fromisoformat("2026-04-21T09:00:00"),
                    ),
                    Recording(
                        session_id=session_id,
                        application_id=app_id,
                        request_method="POST",
                        request_uri="/api/car/service",
                        request_body="<request><code>car000002</code></request>",
                        response_status=200,
                        response_body="<response/>",
                        transaction_code="car000002",
                        dedupe_hash="rec-sort-2",
                        recorded_at=datetime.fromisoformat("2026-04-21T10:00:00"),
                    ),
                    Recording(
                        session_id=session_id,
                        application_id=app_id,
                        request_method="POST",
                        request_uri="/api/car/service",
                        request_body="<request><code>car000003</code></request>",
                        response_status=200,
                        response_body="<response/>",
                        transaction_code="car000003",
                        dedupe_hash="rec-sort-3",
                        recorded_at=datetime.fromisoformat("2026-04-21T11:00:00"),
                    ),
                ]
            )
            await db.commit()
            rows = (
                await db.execute(
                    select(Recording.id)
                    .where(Recording.session_id == session_id)
                    .order_by(Recording.recorded_at)
                )
            ).scalars().all()
            await db.execute(
                update(database.Base.metadata.tables["recording_session"])
                .where(database.Base.metadata.tables["recording_session"].c.id == session_id)
                .values(total_count=3)
            )
            await db.commit()
            return rows

    recording_ids = asyncio.get_event_loop().run_until_complete(_seed_recordings())

    asc_resp = client.get(
        f"/api/v1/sessions/{session_id}/recordings",
        params={"sort_by": "recorded_at", "sort_order": "asc"},
        headers=admin_headers,
    )
    assert asc_resp.status_code == 200
    assert [item["id"] for item in asc_resp.json()] == recording_ids

    desc_resp = client.get(
        f"/api/v1/sessions/{session_id}/recordings",
        params={"sort_by": "recorded_at", "sort_order": "desc"},
        headers=admin_headers,
    )
    assert desc_resp.status_code == 200
    assert [item["id"] for item in desc_resp.json()] == list(reversed(recording_ids))

    delete_resp = client.delete(f"/api/v1/sessions/recordings/{recording_ids[0]}", headers=admin_headers)
    assert delete_resp.status_code == 204

    session_resp = client.get(f"/api/v1/sessions/{session_id}", headers=admin_headers)
    assert session_resp.status_code == 200
    assert session_resp.json()["total_count"] == 2

    bulk_resp = client.post(
        "/api/v1/sessions/recordings/bulk-delete",
        json={"ids": recording_ids[1:]},
        headers=admin_headers,
    )
    assert bulk_resp.status_code == 200
    assert bulk_resp.json()["deleted"] == 2

    final_session_resp = client.get(f"/api/v1/sessions/{session_id}", headers=admin_headers)
    assert final_session_resp.status_code == 200
    assert final_session_resp.json()["total_count"] == 0

    final_list_resp = client.get(f"/api/v1/sessions/{session_id}/recordings", headers=admin_headers)
    assert final_list_resp.status_code == 200
    assert final_list_resp.json() == []


def test_infer_transaction_code_supports_transaction_id_xml():
    xml = """
    <request>
      <transaction_id>car001_open</transaction_id>
      <SYS_EVT_TRACE_ID>1234567890123456789012345</SYS_EVT_TRACE_ID>
    </request>
    """

    assert infer_transaction_code(xml) == "car001_open"


def test_infer_transaction_code_supports_txncode_json():
    body = json.dumps(
        {
            "txnCode": "PLACE_ORDER",
            "params": {
                "orderId": "ORD_001",
            },
        }
    )

    assert infer_transaction_code(body) == "PLACE_ORDER"


def test_infer_transaction_code_supports_custom_candidate_keys():
    body = json.dumps(
        {
            "payload": {
                "sys_code": "LOAN_APPLY",
            },
        }
    )

    assert infer_transaction_code(body, candidate_keys=["sys_code"]) == "LOAN_APPLY"


def test_infer_transaction_code_supports_query_parameters():
    uri = "/loan/query?code=RP54KH01&idcard=110101199001011234"

    assert infer_transaction_code(uri, candidate_keys=["code"]) == "RP54KH01"


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


def test_recording_list_includes_quality_recommendation(client, admin_headers, created_app):
    async def _seed():
        async with database.async_session_factory() as db:
            sess = RecordingSession(
                application_id=created_app["id"],
                name="quality-session",
                status="done",
                total_count=1,
            )
            db.add(sess)
            await db.flush()
            rec = Recording(
                session_id=sess.id,
                application_id=created_app["id"],
                record_id="quality-rid",
                request_method="GET",
                request_uri="/health",
                response_status=200,
                response_body="",
                transaction_code=None,
                governance_status="raw",
                sub_calls="[]",
            )
            db.add(rec)
            await db.commit()
            return sess.id

    session_id = asyncio.get_event_loop().run_until_complete(_seed())

    resp = client.get(f"/api/v1/sessions/{session_id}/recordings", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body[0]["quality_score"] < 80
    assert body[0]["quality_level"] in {"warning", "bad"}
    assert body[0]["quality_recommendation"] in {"candidate", "reject"}
    assert body[0]["quality_reasons"]


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


@pytest.mark.asyncio
async def test_fetch_dynamic_class_sub_calls_normalizes_waimai_repository_methods_to_mysql(
    client, admin_headers, created_app
):
    _create_session(client, created_app["id"], admin_headers, "waimai-dynamic-repository")

    async with database.async_session_factory() as db:
        db.add_all(
            [
                ArexMocker(
                    record_id="rid-waimai-db-1",
                    app_id="waimai-base",
                    category_name="DynamicClass",
                    is_entry_point=False,
                    mocker_data=json.dumps(
                        {
                            "operationName": "com.arex.demo.waimai.repository.WaimaiDataRepository.insertOrder",
                            "targetRequest": {
                                "body": json.dumps(["ORD_001", "C10001", "M20001", "CREATED"]),
                                "attributes": None,
                            },
                            "targetResponse": {
                                "body": None,
                                "attributes": None,
                            },
                        }
                    ),
                    created_at_ms=1776562276912,
                ),
                ArexMocker(
                    record_id="rid-waimai-db-1",
                    app_id="waimai-base",
                    category_name="DynamicClass",
                    is_entry_point=False,
                    mocker_data=json.dumps(
                        {
                            "operationName": "com.arex.demo.waimai.repository.WaimaiDataRepository.queryOrder",
                            "targetRequest": {
                                "body": json.dumps(["ORD_001"]),
                                "attributes": None,
                            },
                            "targetResponse": {
                                "body": json.dumps(
                                    {"order_id": "ORD_001", "customer_id": "C10001", "status": "CREATED"}
                                ),
                                "attributes": None,
                            },
                        }
                    ),
                    created_at_ms=1776562276913,
                ),
            ]
        )
        await db.commit()

    async with database.async_session_factory() as db:
        sub_calls = await _fetch_dynamic_class_sub_calls("rid-waimai-db-1", db)

    assert len(sub_calls) == 2
    assert sub_calls[0]["type"] == "MySQL"
    assert sub_calls[0]["source"] == "agent"
    assert sub_calls[0]["table"] == "orders"
    assert sub_calls[0]["operation"] == "INSERT orders"
    assert sub_calls[0]["status"] == "WRITE"
    assert sub_calls[0]["params"]["orderId"] == "ORD_001"
    assert sub_calls[1]["type"] == "MySQL"
    assert sub_calls[1]["source"] == "agent"
    assert sub_calls[1]["table"] == "orders"
    assert sub_calls[1]["operation"] == "SELECT orders"
    assert sub_calls[1]["status"] == "READ"
    assert sub_calls[1]["params"]["orderId"] == "ORD_001"
    assert sub_calls[1]["response"]["status"] == "CREATED"


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


def test_proxy_config_exposes_waimai_data_repository_dynamic_class_rules(client):
    resp = client.post("/api/config/agent/load", json={"appId": "waimai-base"})
    assert resp.status_code == 200
    body = resp.json()
    rules = body["body"]["dynamicClassConfigurationList"]
    assert any(
        item["fullClassName"] == "com.arex.demo.waimai.repository.WaimaiDataRepository"
        and item["methodName"] == "insertOrder"
        for item in rules
    )
    assert any(
        item["fullClassName"] == "com.arex.demo.waimai.repository.WaimaiDataRepository"
        and item["methodName"] == "queryOrder"
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
async def test_sync_recordings_paginates_all_pages(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "paginate-all-pages").json()["id"]

    async def fake_count_recordings(*args, **kwargs):
        return 3

    async def fake_query_recordings(*args, **kwargs):
        page_index = kwargs["page_index"]
        if page_index == 0:
            return {"body": [{"recordId": "page-1"}, {"recordId": "page-2"}]}
        if page_index == 1:
            return {"body": [{"recordId": "page-3"}]}
        return {"body": []}

    async def fake_view_recording(record_id):
        return {
            "operationName": "POST /api/bank/service",
            "targetRequest": f"<request><service_id>{record_id}</service_id></request>",
            "responseStatusCode": 200,
            "targetResponse": f"<response><code>{record_id}</code></response>",
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.count_recordings", new=AsyncMock(side_effect=fake_count_recordings)),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=fake_query_recordings)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=2,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"
    assert resp.json()["total_count"] == 3

    recordings_resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert recordings_resp.status_code == 200
    assert len(recordings_resp.json()) == 3


def test_list_recordings_active_session_triggers_preview_sync(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "active-preview").json()["id"]

    async def _mark_active():
        async with database.async_session_factory() as db:
            await db.execute(
                update(database.Base.metadata.tables["recording_session"])
                .where(database.Base.metadata.tables["recording_session"].c.id == sess_id)
                .values(
                    status="active",
                    start_time=datetime.fromisoformat("2026-04-22T10:00:00"),
                )
            )
            await db.commit()

    asyncio.get_event_loop().run_until_complete(_mark_active())

    with patch("api.v1.sessions._sync_active_session_preview", new=AsyncMock(return_value=None)) as preview_mock:
        resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)

    assert resp.status_code == 200
    preview_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_sync_active_session_preview_handles_naive_start_time(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers, "active-preview-naive").json()["id"]

    async with database.async_session_factory() as db:
        await db.execute(
            update(database.Base.metadata.tables["recording_session"])
            .where(database.Base.metadata.tables["recording_session"].c.id == sess_id)
            .values(
                status="active",
                start_time=datetime.fromisoformat("2026-04-22T10:00:00"),
            )
        )
        await db.execute(
            database.Base.metadata.tables["recording"].insert().values(
                session_id=sess_id,
                application_id=app_id,
                request_method="POST",
                request_uri="/api/test",
                governance_status="raw",
                recorded_at=datetime(2026, 4, 22, 10, 5, 0, tzinfo=timezone.utc),
            )
        )
        await db.commit()

    with patch("api.v1.sessions._sync_from_arex_storage", new=AsyncMock(return_value=None)) as sync_mock:
        async with database.async_session_factory() as db:
            await _sync_active_session_preview(sess_id, db)

    sync_mock.assert_awaited_once()
    _, kwargs = sync_mock.await_args
    assert kwargs["finalize_session"] is False
    assert kwargs["begin_time"] == datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)


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
async def test_sync_recordings_uses_application_transaction_code_fields(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    update_resp = client.put(
        f"/api/v1/applications/{app_id}",
        json={"transaction_code_fields": ["sys_code"]},
        headers=admin_headers,
    )
    assert update_resp.status_code == 200, update_resp.text

    sess_id = _create_session(client, app_id, admin_headers, "filter-sys-code").json()["id"]

    async def fake_query_recordings(*args, **kwargs):
        return {"body": [{"recordId": "keep-sys-code"}]}

    async def fake_view_recording(record_id):
        return {
            "operationName": "POST /api/bank/service",
            "targetRequest": "<request><sys_code>loan_apply</sys_code></request>",
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

    recordings_resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert recordings_resp.status_code == 200
    recordings = recordings_resp.json()
    assert len(recordings) == 1
    assert recordings[0]["transaction_code"] == "loan_apply"


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
