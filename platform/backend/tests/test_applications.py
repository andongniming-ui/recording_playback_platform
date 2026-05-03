"""Tests for application CRUD, test-connection (mocked SSH), and mount-agent."""
import asyncio
import pytest
from unittest.mock import patch
import json

import database
from models.arex_mocker import ArexMocker
from models.recording import Recording


APP_PAYLOAD = {
    "name": "my-service",
    "ssh_host": "10.0.0.5",
    "ssh_user": "ubuntu",
    "ssh_port": 22,
    "service_port": 8080,
}


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def test_create_application(client, admin_headers):
    resp = client.post("/api/v1/applications", json=APP_PAYLOAD, headers=admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "my-service"
    assert body["agent_status"] in ("unknown", "offline")
    assert "id" in body


def test_create_application_persists_transaction_mappings(client, admin_headers):
    payload = {
        **APP_PAYLOAD,
        "transaction_mappings": json.dumps(
            [
                {
                    "transaction_code": "car001_open",
                    "enabled": True,
                    "description": "基础资料字段映射",
                    "request_rules": [
                        {"type": "rename", "source": "name", "target": "cst_name"},
                        {"type": "default", "source": "branch_code", "value": "0101"},
                    ],
                    "response_rules": [
                        {"type": "rename", "source": "cst_name", "target": "name"},
                    ],
                }
            ],
            ensure_ascii=False,
        ),
    }
    resp = client.post("/api/v1/applications", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["transaction_mappings"][0]["transaction_code"] == "car001_open"
    assert body["transaction_mappings"][0]["request_rules"][0]["type"] == "rename"
    assert body["transaction_mappings"][0]["response_rules"][0]["target"] == "name"

    app_id = body["id"]
    fetched = client.get(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert fetched.status_code == 200
    assert fetched.json()["transaction_mappings"][0]["description"] == "基础资料字段映射"


def test_create_application_persists_transaction_code_fields(client, admin_headers):
    payload = {
        **APP_PAYLOAD,
        "transaction_code_fields": ["txnCode", "code", "sys_code"],
    }
    resp = client.post("/api/v1/applications", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["transaction_code_fields"] == ["txnCode", "code", "sys_code"]

    fetched = client.get(f"/api/v1/applications/{body['id']}", headers=admin_headers)
    assert fetched.status_code == 200
    assert fetched.json()["transaction_code_fields"] == ["txnCode", "code", "sys_code"]


def test_create_application_persists_docker_fields(client, admin_headers):
    payload = {
        **APP_PAYLOAD,
        "launch_mode": "docker_compose",
        "docker_workdir": "/home/test/N-LS",
        "docker_compose_file": "docker-compose.yml",
        "docker_service_name": "sat",
        "docker_storage_url": "http://host.docker.internal:8093",
        "docker_agent_path": "/opt/arex/arex-agent.jar",
    }
    resp = client.post("/api/v1/applications", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["launch_mode"] == "docker_compose"
    assert body["docker_workdir"] == "/home/test/N-LS"
    assert body["docker_compose_file"] == "docker-compose.yml"
    assert body["docker_service_name"] == "sat"
    assert body["docker_storage_url"] == "http://host.docker.internal:8093"
    assert body["docker_agent_path"] == "/opt/arex/arex-agent.jar"


def test_create_application_docker_mode_requires_core_fields(client, admin_headers):
    payload = {
        **APP_PAYLOAD,
        "launch_mode": "docker_compose",
    }
    resp = client.post("/api/v1/applications", json=payload, headers=admin_headers)
    assert resp.status_code == 422, resp.text
    assert "docker_workdir" in resp.text
    assert "docker_service_name" in resp.text


def test_list_applications(client, admin_headers):
    client.post("/api/v1/applications", json=APP_PAYLOAD, headers=admin_headers)
    resp = client.get("/api/v1/applications", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_application(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.get(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == app_id


def test_get_application_not_found(client, admin_headers):
    resp = client.get("/api/v1/applications/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_application_diagnostics_reports_recording_and_agent_uploads(client, admin_headers, created_app):
    async def _seed():
        async with database.async_session_factory() as db:
            db.add(
                Recording(
                    application_id=created_app["id"],
                    request_method="GET",
                    request_uri="/api/orders",
                    response_status=200,
                    response_body='{"ok":true}',
                    transaction_code="ORDER_QUERY",
                    governance_status="raw",
                    sub_calls='[{"type":"MySQL","operation":"SELECT orders"}]',
                )
            )
            db.add(
                ArexMocker(
                    record_id="diag-rid",
                    app_id=created_app["name"],
                    category_name="Servlet",
                    is_entry_point=True,
                    mocker_data="{}",
                )
            )
            db.add(
                ArexMocker(
                    record_id="diag-rid",
                    app_id=created_app["name"],
                    category_name="Database",
                    is_entry_point=False,
                    mocker_data="{}",
                )
            )
            await db.commit()

    asyncio.get_event_loop().run_until_complete(_seed())

    resp = client.get(f"/api/v1/applications/{created_app['id']}/diagnostics", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["application_id"] == created_app["id"]
    by_key = {item["key"]: item for item in body["items"]}
    assert by_key["recordings"]["detail"]["count"] == 1
    assert by_key["agent_upload"]["detail"]["count"] == 2
    assert by_key["servlet_entry"]["detail"]["count"] == 1
    assert by_key["sub_calls"]["detail"]["count"] == 1


def test_update_application(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.put(
        f"/api/v1/applications/{app_id}",
        json={
            "description": "updated description",
            "transaction_code_fields": "txnCode\ncode\nsys_code",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "updated description"
    assert resp.json()["transaction_code_fields"] == ["txnCode", "code", "sys_code"]


def test_update_docker_application_allows_partial_fields(client, admin_headers):
    payload = {
        **APP_PAYLOAD,
        "launch_mode": "docker_compose",
        "docker_workdir": "/home/test/N-LS",
        "docker_compose_file": "docker-compose.yml",
        "docker_service_name": "sat",
        "docker_storage_url": "http://host.docker.internal:8093",
        "docker_agent_path": "/opt/arex/arex-agent.jar",
    }
    created = client.post("/api/v1/applications", json=payload, headers=admin_headers)
    assert created.status_code == 201, created.text
    app_id = created.json()["id"]

    resp = client.put(
        f"/api/v1/applications/{app_id}",
        json={"description": "updated description"},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["description"] == "updated description"
    assert resp.json()["launch_mode"] == "docker_compose"


def test_delete_application(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.delete(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert resp.status_code == 204

    # Should now return 404
    resp2 = client.get(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert resp2.status_code == 404


def test_create_application_requires_auth(client):
    resp = client.post("/api/v1/applications", json=APP_PAYLOAD)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# SSH / Agent endpoints (mocked)
# ---------------------------------------------------------------------------

def test_test_connection_success(client, admin_headers, created_app):
    app_id = created_app["id"]
    mock_result = {"success": True, "latency_ms": 5}
    with patch(
        "integration.ssh_executor.test_connection",
        return_value=mock_result,
    ):
        resp = client.post(
            f"/api/v1/applications/{app_id}/test-connection",
            headers=admin_headers,
        )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_mount_agent_starts_background(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.post(
        f"/api/v1/applications/{app_id}/mount-agent",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "mounting"


def test_mount_agent_docker_mode_uses_docker_deployer(client, admin_headers):
    payload = {
        **APP_PAYLOAD,
        "launch_mode": "docker_compose",
        "docker_workdir": "/home/test/N-LS",
        "docker_compose_file": "docker-compose.yml",
        "docker_service_name": "sat",
    }
    created = client.post("/api/v1/applications", json=payload, headers=admin_headers)
    assert created.status_code == 201, created.text
    app_id = created.json()["id"]

    with patch(
        "integration.ssh_executor.deploy_docker_agent",
        return_value="OK: deployed docker agent into /home/test/N-LS/docker-compose.yml",
    ) as deploy_mock:
        resp = client.post(f"/api/v1/applications/{app_id}/mount-agent", headers=admin_headers)

    assert resp.status_code == 200
    assert resp.json()["status"] == "mounting"
    assert deploy_mock.called

    updated = client.get(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert updated.status_code == 200
    assert updated.json()["agent_status"] == "online"


def test_render_docker_compose_override_uses_host_and_container_paths():
    from integration.ssh_executor import render_docker_compose_override

    class DummyApp:
        name = "nls-sat"
        arex_app_id = "nls-sat"
        sample_rate = 0.5
        docker_service_name = "sat"
        docker_agent_path = "/opt/arex/arex-agent.jar"
        docker_workdir = "/home/test/N-LS"
        docker_compose_file = "docker-compose.yml"

    content = render_docker_compose_override(
        DummyApp(),
        "http://host.docker.internal:8093",
        "/home/test/N-LS/.arex-recorder/arex-agent.jar",
        "/opt/arex/arex-agent.jar",
    )

    assert '-javaagent:/opt/arex/arex-agent.jar' in content
    assert '/home/test/N-LS/.arex-recorder/arex-agent.jar:/opt/arex/arex-agent.jar:ro' in content
    assert 'host.docker.internal:host-gateway' in content


def test_render_docker_compose_override_splits_storage_host_and_port_even_with_path():
    from integration.ssh_executor import render_docker_compose_override

    class DummyApp:
        name = "nls-sat"
        arex_app_id = "nls-sat"
        sample_rate = 1.0
        docker_service_name = "sat"
        docker_agent_path = "/opt/arex/arex-agent.jar"
        docker_workdir = "/home/test/N-LS"
        docker_compose_file = "docker-compose.yml"

    content = render_docker_compose_override(
        DummyApp(),
        "http://arex-storage:8093/api/v1",
        "/home/test/N-LS/.arex-recorder/arex-agent.jar",
        "/opt/arex/arex-agent.jar",
    )

    assert "-Darex.storage.service.host=arex-storage" in content
    assert "-Darex.storage.service.port=8093" in content
    assert "/api/v1" not in content


def test_docker_compose_falls_back_to_legacy_binary():
    from integration import ssh_executor

    calls = []

    def fake_run(app, command, timeout=90):
        calls.append(command)
        if "docker compose" in command:
            return (127, "", "docker compose: command not found")
        if "docker-compose" in command:
            return (0, "ok", "")
        return (0, "", "")

    app = type("DummyApp", (), {"docker_workdir": "/home/test/N-LS"})()

    with patch("integration.ssh_executor.run_command", side_effect=fake_run):
        code, out, err = ssh_executor._run_docker_compose_with_fallback(app, "docker compose ps -q sat")

    assert code == 0
    assert out == "ok"
    assert any("docker compose" in c for c in calls)
    assert any("docker-compose" in c for c in calls)


def test_docker_status_without_override_file_uses_base_compose():
    from integration import ssh_executor

    calls = []

    def fake_run(app, command, timeout=60):
        calls.append(command)
        if command.startswith("test -f "):
            return (1, "", "")
        if "docker compose" in command and "ps -q" in command:
            return (0, "container-123\n", "")
        if command.startswith("docker inspect"):
            return (
                0,
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
                "JAVA_HOME=/opt/java\n",
                "",
            )
        return (0, "", "")

    app = type(
        "DummyApp",
        (),
        {
            "docker_workdir": "/home/test/N-LS",
            "docker_service_name": "sat",
            "docker_compose_file": "docker-compose.yml",
        },
    )()

    with patch("integration.ssh_executor.run_command", side_effect=fake_run):
        status = ssh_executor.get_docker_agent_status(app)

    assert status["status"] == "RUNNING"
    assert status["pid"] == "container-123"
    assert status["arex_agent"] is False
    # The first compose ps command should not reference the override file when it is absent.
    assert any("ps -q sat" in cmd and ".arex-recorder" not in cmd for cmd in calls)
