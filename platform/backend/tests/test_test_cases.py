"""Tests for test case CRUD, clone, export, import, from-recording, add-to-suite."""
import json
import io
import pytest

import asyncio
import uuid
from datetime import datetime
from models.recording import Recording
import database as _db_module
from sqlalchemy import select, update
from models.replay import ReplayJob, ReplayResult
from models.suite import SuiteCase


def _seed_recordings(app_id: int, transaction_codes: list):
    """Seed Recording rows and return their IDs (in insertion order)."""
    async def _run():
        async with _db_module.async_session_factory() as session:
            rows = []
            for code in transaction_codes:
                row = Recording(
                    application_id=app_id,
                    request_method="POST",
                    request_uri="/api/service",
                    request_body=f"<req><service_id>{code or 'UNKNOWN'}</service_id></req>",
                    response_status=200,
                    response_body="<response><code>0000</code></response>",
                    transaction_code=code,
                    scene_key=f"{code or 'UNKNOWN'}|POST|/api/service|success" if code else None,
                    dedupe_hash=uuid.uuid4().hex,
                    governance_status="candidate",
                )
                session.add(row)
                rows.append(row)
            await session.commit()
            for row in rows:
                await session.refresh(row)
            return [row.id for row in rows]
    return asyncio.get_event_loop().run_until_complete(_run())


TC_PAYLOAD = {
    "name": "GET /api/users",
    "request_method": "GET",
    "request_uri": "/api/users",
    "expected_status": 200,
}


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def _create_tc(client, headers, **overrides):
    payload = dict(TC_PAYLOAD, **overrides)
    resp = client.post("/api/v1/test-cases", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_test_case(client, admin_headers):
    body = _create_tc(client, admin_headers)
    assert body["name"] == TC_PAYLOAD["name"]
    assert body["status"] == "draft"
    assert "id" in body


def test_list_test_cases(client, admin_headers):
    _create_tc(client, admin_headers, name="case-1")
    _create_tc(client, admin_headers, name="case-2")

    resp = client.get("/api/v1/test-cases", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_list_test_cases_supports_created_at_sort_order(client, admin_headers):
    first = _create_tc(client, admin_headers, name="sort-case-1")
    second = _create_tc(client, admin_headers, name="sort-case-2")

    async def _seed_order():
        async with _db_module.async_session_factory() as db:
            await db.execute(
                update(_db_module.Base.metadata.tables["test_case"])
                .where(_db_module.Base.metadata.tables["test_case"].c.id == first["id"])
                .values(created_at=datetime.fromisoformat("2026-04-21T09:00:00"))
            )
            await db.execute(
                update(_db_module.Base.metadata.tables["test_case"])
                .where(_db_module.Base.metadata.tables["test_case"].c.id == second["id"])
                .values(created_at=datetime.fromisoformat("2026-04-21T10:00:00"))
            )
            await db.commit()

    asyncio.get_event_loop().run_until_complete(_seed_order())

    asc_resp = client.get(
        "/api/v1/test-cases",
        params={"sort_by": "created_at", "sort_order": "asc"},
        headers=admin_headers,
    )
    assert asc_resp.status_code == 200
    asc_ids = [item["id"] for item in asc_resp.json()[:2]]
    assert asc_ids == [first["id"], second["id"]]

    desc_resp = client.get(
        "/api/v1/test-cases",
        params={"sort_by": "created_at", "sort_order": "desc"},
        headers=admin_headers,
    )
    assert desc_resp.status_code == 200
    desc_ids = [item["id"] for item in desc_resp.json()[:2]]
    assert desc_ids == [second["id"], first["id"]]


def test_get_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers)
    resp = client.get(f"/api/v1/test-cases/{tc['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == tc["id"]


def test_get_test_case_not_found(client, admin_headers):
    resp = client.get("/api/v1/test-cases/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_update_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers)
    resp = client.put(
        f"/api/v1/test-cases/{tc['id']}",
        json={"status": "active"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_delete_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers)
    resp = client.delete(f"/api/v1/test-cases/{tc['id']}", headers=admin_headers)
    assert resp.status_code == 204

    resp2 = client.get(f"/api/v1/test-cases/{tc['id']}", headers=admin_headers)
    assert resp2.status_code == 404


def test_bulk_delete_test_cases_clears_suite_links_and_replay_results(client, admin_headers):
    first = _create_tc(client, admin_headers, name="bulk-case-1", governance_status="approved", scene_key="bulk-1")
    second = _create_tc(client, admin_headers, name="bulk-case-2", governance_status="approved", scene_key="bulk-2")

    suite_resp = client.post(
        "/api/v1/suites",
        json={"name": "bulk-suite"},
        headers=admin_headers,
    )
    assert suite_resp.status_code == 201
    suite_id = suite_resp.json()["id"]

    add_resp = client.post(
        f"/api/v1/test-cases/{first['id']}/add-to-suite",
        json={"suite_id": suite_id},
        headers=admin_headers,
    )
    assert add_resp.status_code == 201

    async def _seed_replay_result():
        async with _db_module.async_session_factory() as db:
            job = ReplayJob(name="linked-job", status="DONE", total=1, passed=1)
            db.add(job)
            await db.flush()
            db.add(
                ReplayResult(
                    job_id=job.id,
                    test_case_id=first["id"],
                    status="PASS",
                    request_method="GET",
                    request_uri="/api/v1/test",
                    is_pass=True,
                )
            )
            await db.commit()
            return job.id

    job_id = asyncio.get_event_loop().run_until_complete(_seed_replay_result())

    resp = client.post(
        "/api/v1/test-cases/bulk-delete",
        json={"ids": [first["id"], second["id"]]},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 2

    async def _assert_cleanup():
        async with _db_module.async_session_factory() as db:
            remaining_cases = (
                await db.execute(select(_db_module.Base.metadata.tables["test_case"].c.id))
            ).scalars().all()
            suite_links = (
                await db.execute(select(SuiteCase).where(SuiteCase.suite_id == suite_id))
            ).scalars().all()
            replay_result = (
                await db.execute(select(ReplayResult).where(ReplayResult.job_id == job_id))
            ).scalar_one()
            return remaining_cases, suite_links, replay_result.test_case_id

    remaining_cases, suite_links, replay_result_case_id = asyncio.get_event_loop().run_until_complete(_assert_cleanup())
    assert first["id"] not in remaining_cases
    assert second["id"] not in remaining_cases
    assert suite_links == []
    assert replay_result_case_id is None


# ---------------------------------------------------------------------------
# Clone
# ---------------------------------------------------------------------------

def test_clone_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers, name="original")
    resp = client.post(
        f"/api/v1/test-cases/{tc['id']}/clone",
        headers=admin_headers,
    )
    assert resp.status_code == 201
    clone = resp.json()
    assert clone["name"] == "original (copy)"
    assert clone["id"] != tc["id"]
    assert clone["status"] == "draft"


# ---------------------------------------------------------------------------
# Export / Import
# ---------------------------------------------------------------------------

def test_export_test_cases(client, admin_headers):
    tc = _create_tc(client, admin_headers, name="export-me")
    resp = client.get(
        f"/api/v1/test-cases/export?ids={tc['id']}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    exported = resp.json()
    assert isinstance(exported, list)
    assert exported[0]["name"] == "export-me"


def test_import_test_cases(client, admin_headers):
    cases = [
        {
            "name": "imported-case",
            "request_method": "POST",
            "request_uri": "/api/login",
        }
    ]
    file_bytes = json.dumps(cases).encode()
    resp = client.post(
        "/api/v1/test-cases/import",
        files={"file": ("cases.json", io.BytesIO(file_bytes), "application/json")},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["imported"] == 1


def test_import_invalid_json(client, admin_headers):
    resp = client.post(
        "/api/v1/test-cases/import",
        files={"file": ("bad.json", io.BytesIO(b"not json at all"), "application/json")},
        headers=admin_headers,
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Add to suite
# ---------------------------------------------------------------------------

def test_add_to_suite(client, admin_headers):
    tc = _create_tc(client, admin_headers, governance_status="approved", scene_key="suite-case-1")
    # Create suite
    suite_resp = client.post(
        "/api/v1/suites",
        json={"name": "my-suite"},
        headers=admin_headers,
    )
    assert suite_resp.status_code == 201
    suite_id = suite_resp.json()["id"]

    resp = client.post(
        f"/api/v1/test-cases/{tc['id']}/add-to-suite",
        json={"suite_id": suite_id},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["order_index"] == 1


def test_create_from_recording_carries_transaction_code_and_governance(client, admin_headers, created_app):
    session_resp = client.post(
        "/api/v1/sessions",
        json={"application_id": created_app["id"], "name": "case-source"},
        headers=admin_headers,
    )
    session_id = session_resp.json()["id"]

    recording_resp = client.patch(
        "/api/v1/sessions/recordings/1",
        json={"governance_status": "approved"},
        headers=admin_headers,
    )
    if recording_resp.status_code == 404:
        from models.recording import Recording
        import database
        import asyncio

        async def _seed():
            async with database.async_session_factory() as db:
                row = Recording(
                    session_id=session_id,
                    application_id=created_app["id"],
                    request_method="POST",
                    request_uri="/api/bank/service",
                    request_body="<request><service_id>OPEN_ACCOUNT</service_id></request>",
                    response_status=200,
                    response_body="<response><code>0000</code></response>",
                    transaction_code="OPEN_ACCOUNT",
                    scene_key="OPEN_ACCOUNT|POST|/api/bank/service|success",
                    dedupe_hash="seed-hash",
                    governance_status="approved",
                )
                db.add(row)
                await db.commit()
                await db.refresh(row)
                return row.id

        recording_id = asyncio.get_event_loop().run_until_complete(_seed())
    else:
        recording_id = 1

    resp = client.post(
        "/api/v1/test-cases/from-recording",
        json={"recording_id": recording_id},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["transaction_code"] == "OPEN_ACCOUNT"
    assert body["governance_status"] == "approved"
    assert body["scene_key"] == "OPEN_ACCOUNT|POST|/api/bank/service|success"


def test_create_from_recording_rebuilds_unknown_scene_key_when_txncode_can_be_inferred(
    client, admin_headers, created_app
):
    session_resp = client.post(
        "/api/v1/sessions",
        json={"application_id": created_app["id"], "name": "waimai-case-source"},
        headers=admin_headers,
    )
    session_id = session_resp.json()["id"]

    from models.recording import Recording
    import database
    import asyncio

    async def _seed():
        async with database.async_session_factory() as db:
            row = Recording(
                session_id=session_id,
                application_id=created_app["id"],
                request_method="POST",
                request_uri="/waimai/gateway/json",
                request_body='{"txnCode":"PLACE_ORDER","params":{"orderId":"ORD_001"}}',
                response_status=200,
                response_body='{"status":"SUCCESS"}',
                transaction_code=None,
                scene_key="unknown_tx|POST|/waimai/gateway/json|success",
                dedupe_hash="seed-waimai-hash",
                governance_status="raw",
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            return row.id

    recording_id = asyncio.get_event_loop().run_until_complete(_seed())

    resp = client.post(
        "/api/v1/test-cases/from-recording",
        json={"recording_id": recording_id},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["transaction_code"] == "PLACE_ORDER"
    assert body["scene_key"] == "PLACE_ORDER|POST|/waimai/gateway/json|success"


def test_suite_supports_suite_type(client, admin_headers):
    resp = client.post(
        "/api/v1/suites",
        json={"name": "daily-smoke", "suite_type": "smoke"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["suite_type"] == "smoke"

    list_resp = client.get("/api/v1/suites?suite_type=smoke", headers=admin_headers)
    assert list_resp.status_code == 200
    assert any(item["id"] == body["id"] for item in list_resp.json())


def test_add_to_smoke_suite_requires_approved_case(client, admin_headers):
    tc = _create_tc(client, admin_headers, governance_status="candidate", scene_key="S1")
    suite_resp = client.post(
        "/api/v1/suites",
        json={"name": "smoke-suite", "suite_type": "smoke"},
        headers=admin_headers,
    )
    suite_id = suite_resp.json()["id"]

    resp = client.post(
        f"/api/v1/test-cases/{tc['id']}/add-to-suite",
        json={"suite_id": suite_id},
        headers=admin_headers,
    )
    assert resp.status_code == 400
    assert "Only approved test cases" in resp.json()["detail"]


def test_suite_rejects_duplicate_scene_key_selection(client, admin_headers):
    first = _create_tc(client, admin_headers, governance_status="approved", transaction_code="OPEN_ACCOUNT", scene_key="scene-a")
    second = _create_tc(client, admin_headers, name="dup", governance_status="approved", transaction_code="OPEN_ACCOUNT", scene_key="scene-a")
    suite_resp = client.post(
        "/api/v1/suites",
        json={"name": "reg-suite", "suite_type": "regression"},
        headers=admin_headers,
    )
    suite_id = suite_resp.json()["id"]

    resp = client.put(
        f"/api/v1/suites/{suite_id}/cases",
        json={"case_ids": [first["id"], second["id"]]},
        headers=admin_headers,
    )
    assert resp.status_code == 400
    assert "Duplicate scene_key" in resp.json()["detail"]


def test_auto_smoke_suite_selects_one_approved_case_per_transaction(client, admin_headers):
    app = client.post(
        "/api/v1/applications",
        json={
            "name": "auto-smoke-app",
            "ssh_host": "127.0.0.1",
            "ssh_user": "deploy",
            "ssh_port": 22,
            "service_port": 8080,
        },
        headers=admin_headers,
    ).json()

    first = _create_tc(
        client,
        admin_headers,
        application_id=app["id"],
        governance_status="approved",
        transaction_code="OPEN_ACCOUNT",
        scene_key="open-account-scene-1",
        request_uri="/open/1",
    )
    second = _create_tc(
        client,
        admin_headers,
        application_id=app["id"],
        governance_status="approved",
        transaction_code="OPEN_ACCOUNT",
        scene_key="open-account-scene-2",
        request_uri="/open/2",
    )
    third = _create_tc(
        client,
        admin_headers,
        application_id=app["id"],
        governance_status="approved",
        transaction_code="QUERY_BALANCE",
        scene_key="query-balance-scene-1",
        request_uri="/query/1",
    )

    resp = client.post(
        "/api/v1/suites/auto-smoke",
        json={"application_id": app["id"], "name": "auto-smoke"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "auto-smoke"
    assert len(body["added_case_ids"]) == 2
    assert set(body["added_case_ids"]).issubset({first["id"], second["id"], third["id"]})

    suite_resp = client.get(f"/api/v1/suites/{body['suite_id']}", headers=admin_headers)
    assert suite_resp.status_code == 200
    suite_body = suite_resp.json()
    assert suite_body["suite_type"] == "smoke"
    assert len(suite_body["cases"]) == 2


# ---------------------------------------------------------------------------
# Batch check
# ---------------------------------------------------------------------------

def test_batch_check_no_conflicts(client, admin_headers, created_app):
    rec_ids = _seed_recordings(created_app["id"], ["OPEN_ACCOUNT", "CLOSE_ACCOUNT"])

    resp = client.post(
        "/api/v1/test-cases/batch-check",
        json={"recording_ids": rec_ids},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    assert all(not item["has_existing"] for item in items)
    codes = {item["transaction_code"] for item in items}
    assert codes == {"OPEN_ACCOUNT", "CLOSE_ACCOUNT"}


def test_batch_check_detects_conflict(client, admin_headers, created_app):
    rec_ids = _seed_recordings(created_app["id"], ["FREEZE_ACCOUNT", "UNFREEZE_ACCOUNT"])

    # Create a test case from rec_ids[0] to create conflict
    client.post(
        "/api/v1/test-cases/from-recording",
        json={"recording_id": rec_ids[0]},
        headers=admin_headers,
    )

    resp = client.post(
        "/api/v1/test-cases/batch-check",
        json={"recording_ids": rec_ids},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    by_id = {item["recording_id"]: item for item in resp.json()}

    assert by_id[rec_ids[0]]["has_existing"] is True
    assert by_id[rec_ids[0]]["existing_case_id"] is not None
    assert by_id[rec_ids[1]]["has_existing"] is False


# ---------------------------------------------------------------------------
# Batch from recordings
# ---------------------------------------------------------------------------

def test_batch_from_recordings_creates_cases(client, admin_headers, created_app):
    rec_ids = _seed_recordings(created_app["id"], ["OPEN_ACCOUNT", "CLOSE_ACCOUNT"])

    resp = client.post(
        "/api/v1/test-cases/batch-from-recordings",
        json={"recording_ids": rec_ids, "prefix": "银行"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert body["created"] == 2
    assert body["failed"] == 0
    names = {r["name"] for r in body["results"]}
    assert "银行 - OPEN_ACCOUNT" in names
    assert "银行 - CLOSE_ACCOUNT" in names
    assert all(r["status"] == "created" for r in body["results"])


def test_batch_from_recordings_fallback_name_when_no_transaction_code(client, admin_headers, created_app):
    rec_ids = _seed_recordings(created_app["id"], [None])  # no transaction code

    resp = client.post(
        "/api/v1/test-cases/batch-from-recordings",
        json={"recording_ids": rec_ids, "prefix": "前缀"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["created"] == 1
    name = body["results"][0]["name"]
    assert name.startswith("前缀 - POST")


def test_batch_from_recordings_handles_missing_recording(client, admin_headers):
    resp = client.post(
        "/api/v1/test-cases/batch-from-recordings",
        json={"recording_ids": [99999], "prefix": "test"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["failed"] == 1
    assert body["results"][0]["status"] == "failed"
    assert "not found" in body["results"][0]["error"].lower()


def test_batch_from_recordings_rolls_back_when_any_recording_missing(client, admin_headers, created_app):
    rec_ids = _seed_recordings(created_app["id"], ["VALID_CODE"])
    ids = [rec_ids[0], 99998]  # 一个有效，一个无效

    resp = client.post(
        "/api/v1/test-cases/batch-from-recordings",
        json={"recording_ids": ids, "prefix": "混合"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert body["created"] == 0
    assert body["failed"] == 2
    assert all(item["status"] == "failed" for item in body["results"])
