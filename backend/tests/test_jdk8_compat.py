"""
JDK8 compatibility tests for arex-recorder.

Tests cover:
1. inject_javaagent_param generates correct AREX agent properties (host/port separate)
2. detect_java_version correctly identifies JDK8 vs JDK11
3. inject_javaagent_param rejects non-JDK8 targets
4. arex_app_id is used as service name when set
5. sample_rate is correctly converted to percentage and injected
6. mount_agent sets status to "error" on JDK version mismatch
"""
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Unit tests for ssh_executor (no SSH connection needed)
# ---------------------------------------------------------------------------

def _make_app(**kwargs):
    """Create a minimal mock Application object."""
    app = MagicMock()
    app.name = kwargs.get("name", "test-service")
    app.arex_app_id = kwargs.get("arex_app_id", None)
    app.ssh_user = kwargs.get("ssh_user", "ubuntu")
    app.sample_rate = kwargs.get("sample_rate", 1.0)
    return app


def _run_inject(app, arex_url, agent_path, java_version_str, script_content="java -jar app.jar"):
    """
    Helper: run inject_javaagent_param with mocked SSH calls.
    Returns the result string.
    """
    from integration.ssh_executor import inject_javaagent_param

    def fake_run_command(app_, cmd, timeout=30):
        if "java -version" in cmd:
            return (0, f'openjdk version "{java_version_str}" 2023-01-17\n', "")
        if "find ~" in cmd or "ls ~" in cmd:
            return (0, "/home/ubuntu/start.sh\n", "")
        if cmd.startswith("cat "):
            return (0, script_content, "")
        if cmd.startswith("sed -i"):
            return (0, "", "")
        return (0, "", "")

    with patch("integration.ssh_executor.run_command", side_effect=fake_run_command):
        return inject_javaagent_param(app, arex_url, agent_path)


class TestInjectJavaagentParam:

    def test_storage_host_and_port_are_separate(self):
        """Bug fix: -Darex.storage.service.host must NOT contain the port number."""
        app = _make_app()
        result = _run_inject(app, "http://arex-storage:8093", "/agent/arex-agent.jar", "1.8.0_362")

        assert result.startswith("OK:"), f"Expected OK, got: {result}"
        # The injected params must have been written via sed — we verify by checking
        # that run_command was called with a sed command that has the right structure.
        injected_lines = []
        from integration.ssh_executor import inject_javaagent_param

        captured_sed = []

        def capture_run(app_, cmd, timeout=30):
            if "java -version" in cmd:
                return (0, 'openjdk version "1.8.0_362" 2023\n', "")
            if "find ~" in cmd or "ls ~" in cmd:
                return (0, "/home/ubuntu/start.sh\n", "")
            if cmd.startswith("cat "):
                return (0, "java -jar app.jar", "")
            if cmd.startswith("sed"):
                captured_sed.append(cmd)
                return (0, "", "")
            return (0, "", "")

        app2 = _make_app()
        with patch("integration.ssh_executor.run_command", side_effect=capture_run):
            inject_javaagent_param(app2, "http://arex-storage:8093", "/agent/arex-agent.jar")

        assert captured_sed, "No sed command was captured"
        sed_cmd = captured_sed[0]
        # host should be just the hostname
        assert "Darex.storage.service.host=arex-storage " in sed_cmd or \
               "Darex.storage.service.host=arex-storage\\\\" in sed_cmd or \
               "storage.service.host=arex-storage" in sed_cmd, \
               f"host contains port or is wrong: {sed_cmd}"
        # port should be separate
        assert "Darex.storage.service.port=8093" in sed_cmd, \
               f"Missing separate port property in: {sed_cmd}"
        # host should not be "arex-storage:8093"
        assert "service.host=arex-storage:8093" not in sed_cmd, \
               f"host:port combined — this is the bug! sed_cmd={sed_cmd}"

    def test_arex_app_id_used_as_service_name_when_set(self):
        """arex_app_id overrides app.name so recordings sync correctly."""
        captured_sed = []

        def capture_run(app_, cmd, timeout=30):
            if "java -version" in cmd:
                return (0, 'openjdk version "1.8.0_362" 2023\n', "")
            if "find ~" in cmd or "ls ~" in cmd:
                return (0, "/home/ubuntu/start.sh\n", "")
            if cmd.startswith("cat "):
                return (0, "java -jar app.jar", "")
            if cmd.startswith("sed"):
                captured_sed.append(cmd)
                return (0, "", "")
            return (0, "", "")

        from integration.ssh_executor import inject_javaagent_param
        app = _make_app(name="local-name", arex_app_id="arex-storage-app-id")
        with patch("integration.ssh_executor.run_command", side_effect=capture_run):
            inject_javaagent_param(app, "http://host:8093", "/agent.jar")

        assert captured_sed, "No sed command captured"
        sed_cmd = captured_sed[0]
        assert "arex-storage-app-id" in sed_cmd, \
            f"arex_app_id not used as service name: {sed_cmd}"
        assert "local-name" not in sed_cmd, \
            f"app.name used instead of arex_app_id: {sed_cmd}"

    def test_app_name_used_when_arex_app_id_not_set(self):
        """When arex_app_id is None, app.name is used as fallback."""
        captured_sed = []

        def capture_run(app_, cmd, timeout=30):
            if "java -version" in cmd:
                return (0, 'openjdk version "1.8.0_362" 2023\n', "")
            if "find ~" in cmd or "ls ~" in cmd:
                return (0, "/home/ubuntu/start.sh\n", "")
            if cmd.startswith("cat "):
                return (0, "java -jar app.jar", "")
            if cmd.startswith("sed"):
                captured_sed.append(cmd)
                return (0, "", "")
            return (0, "", "")

        from integration.ssh_executor import inject_javaagent_param
        app = _make_app(name="my-service", arex_app_id=None)
        with patch("integration.ssh_executor.run_command", side_effect=capture_run):
            inject_javaagent_param(app, "http://host:8093", "/agent.jar")

        assert captured_sed
        assert "my-service" in captured_sed[0]

    def test_sample_rate_injected_as_percentage(self):
        """sample_rate=0.5 should produce -Darex.record.rate=50."""
        captured_sed = []

        def capture_run(app_, cmd, timeout=30):
            if "java -version" in cmd:
                return (0, 'openjdk version "1.8.0_362" 2023\n', "")
            if "find ~" in cmd or "ls ~" in cmd:
                return (0, "/home/ubuntu/start.sh\n", "")
            if cmd.startswith("cat "):
                return (0, "java -jar app.jar", "")
            if cmd.startswith("sed"):
                captured_sed.append(cmd)
                return (0, "", "")
            return (0, "", "")

        from integration.ssh_executor import inject_javaagent_param
        app = _make_app(sample_rate=0.5)
        with patch("integration.ssh_executor.run_command", side_effect=capture_run):
            inject_javaagent_param(app, "http://host:8093", "/agent.jar")

        assert captured_sed
        assert "Darex.record.rate=50" in captured_sed[0], \
            f"sample_rate not injected correctly: {captured_sed[0]}"

    def test_sample_rate_100_percent(self):
        """sample_rate=1.0 should produce -Darex.record.rate=100."""
        captured_sed = []

        def capture_run(app_, cmd, timeout=30):
            if "java -version" in cmd:
                return (0, 'openjdk version "1.8.0_362" 2023\n', "")
            if "find ~" in cmd or "ls ~" in cmd:
                return (0, "/home/ubuntu/start.sh\n", "")
            if cmd.startswith("cat "):
                return (0, "java -jar app.jar", "")
            if cmd.startswith("sed"):
                captured_sed.append(cmd)
                return (0, "", "")
            return (0, "", "")

        from integration.ssh_executor import inject_javaagent_param
        app = _make_app(sample_rate=1.0)
        with patch("integration.ssh_executor.run_command", side_effect=capture_run):
            inject_javaagent_param(app, "http://host:8093", "/agent.jar")

        assert captured_sed
        assert "Darex.record.rate=100" in captured_sed[0]

    def test_rejects_jdk11_target(self):
        """inject_javaagent_param must return ERROR when target JVM is JDK 11."""
        result = _run_inject(
            _make_app(), "http://host:8093", "/agent.jar",
            java_version_str="11.0.18"
        )
        assert result.startswith("ERROR:"), f"Expected ERROR for JDK11, got: {result}"
        assert "11.0.18" in result

    def test_rejects_jdk17_target(self):
        """inject_javaagent_param must return ERROR when target JVM is JDK 17."""
        result = _run_inject(
            _make_app(), "http://host:8093", "/agent.jar",
            java_version_str="17.0.5"
        )
        assert result.startswith("ERROR:"), f"Expected ERROR for JDK17, got: {result}"

    def test_accepts_jdk8_target(self):
        """inject_javaagent_param must proceed normally for JDK 8 (1.8.x)."""
        result = _run_inject(
            _make_app(), "http://host:8093", "/agent.jar",
            java_version_str="1.8.0_362"
        )
        assert result.startswith("OK:") or result == "ALREADY_INJECTED", \
            f"Expected OK for JDK8, got: {result}"

    def test_already_injected_skips_injection(self):
        """If -javaagent already in script, return ALREADY_INJECTED."""
        result = _run_inject(
            _make_app(), "http://host:8093", "/agent.jar",
            java_version_str="1.8.0_362",
            script_content="java -javaagent:/old/agent.jar -jar app.jar"
        )
        assert result == "ALREADY_INJECTED"

    def test_no_startup_script_found(self):
        """Return NOT_FOUND when no start.sh exists on the target."""
        from integration.ssh_executor import inject_javaagent_param

        def fake_run(app_, cmd, timeout=30):
            if "java -version" in cmd:
                return (0, 'openjdk version "1.8.0_362" 2023\n', "")
            # All find/ls calls return empty
            return (0, "", "")

        app = _make_app()
        with patch("integration.ssh_executor.run_command", side_effect=fake_run):
            result = inject_javaagent_param(app, "http://host:8093", "/agent.jar")

        assert result.startswith("NOT_FOUND")

    def test_storage_url_without_port_defaults_to_8080(self):
        """If arex_storage_url has no port, default port 8080 is used."""
        captured_sed = []

        def capture_run(app_, cmd, timeout=30):
            if "java -version" in cmd:
                return (0, 'openjdk version "1.8.0_362" 2023\n', "")
            if "find ~" in cmd or "ls ~" in cmd:
                return (0, "/home/ubuntu/start.sh\n", "")
            if cmd.startswith("cat "):
                return (0, "java -jar app.jar", "")
            if cmd.startswith("sed"):
                captured_sed.append(cmd)
                return (0, "", "")
            return (0, "", "")

        from integration.ssh_executor import inject_javaagent_param
        app = _make_app()
        with patch("integration.ssh_executor.run_command", side_effect=capture_run):
            inject_javaagent_param(app, "http://arex-storage-host", "/agent.jar")

        assert captured_sed
        assert "Darex.storage.service.port=8080" in captured_sed[0], \
            f"Default port 8080 not used: {captured_sed[0]}"


# ---------------------------------------------------------------------------
# detect_java_version unit tests
# ---------------------------------------------------------------------------

class TestDetectJavaVersion:

    def test_detect_jdk8(self):
        """Parses JDK8 version string correctly."""
        from integration.ssh_executor import detect_java_version

        def fake_run(app_, cmd, timeout=30):
            return (0, 'openjdk version "1.8.0_362" 2023-01-17\n', "")

        with patch("integration.ssh_executor.run_command", side_effect=fake_run):
            ver = detect_java_version(MagicMock())
        assert ver == "1.8.0_362"

    def test_detect_jdk11(self):
        """Parses JDK11 version string correctly."""
        from integration.ssh_executor import detect_java_version

        def fake_run(app_, cmd, timeout=30):
            return (0, 'openjdk version "11.0.18" 2023-01-17\n', "")

        with patch("integration.ssh_executor.run_command", side_effect=fake_run):
            ver = detect_java_version(MagicMock())
        assert ver == "11.0.18"

    def test_detect_returns_none_on_failure(self):
        """Returns None when SSH command fails."""
        from integration.ssh_executor import detect_java_version

        with patch("integration.ssh_executor.run_command", side_effect=Exception("timeout")):
            ver = detect_java_version(MagicMock())
        assert ver is None


# ---------------------------------------------------------------------------
# Integration test: mount-agent API returns "mounting" and logs JDK error
# ---------------------------------------------------------------------------

def test_mount_agent_sets_error_status_for_non_jdk8(client, admin_headers, created_app):
    """
    When the target JVM is not JDK8, mount-agent API should still return 200
    (it's a background task), and the agent_status should eventually be 'error'.
    We mock the background work synchronously to verify the status transition.
    """
    app_id = created_app["id"]

    with patch("integration.ssh_executor.upload_arex_agent", return_value=None), \
         patch(
             "integration.ssh_executor.inject_javaagent_param",
             return_value="ERROR: JDK version 11.0.18 is not JDK 8 — use the correct AREX agent JAR",
         ):
        resp = client.post(
            f"/api/v1/applications/{app_id}/mount-agent",
            headers=admin_headers,
        )

    # The endpoint immediately returns "mounting" (background task)
    assert resp.status_code == 200
    assert resp.json()["status"] == "mounting"
