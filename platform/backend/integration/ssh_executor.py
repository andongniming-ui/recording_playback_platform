"""
SSH/SFTP operations on target hosts via Paramiko.
All methods are sync (run in thread pool via asyncio.to_thread).
"""
import logging
import re
import shlex
import time
from pathlib import Path
from urllib.parse import urlparse
import json
import paramiko
from config import settings
from models.application import Application

logger = logging.getLogger(__name__)


def _build_client(app: Application, retries: int = 3) -> paramiko.SSHClient:
    """Build SSH client with retry mechanism."""
    client = paramiko.SSHClient()
    if settings.ssh_known_hosts_path:
        client.load_host_keys(settings.ssh_known_hosts_path)
    else:
        client.load_system_host_keys()

    if settings.ssh_strict_host_key_checking:
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
    else:
        logger.warning(
            "SSH strict host key checking is disabled; automatically trusting host %s",
            app.ssh_host,
        )
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs: dict = {
        "hostname": app.ssh_host,
        "port": app.ssh_port,
        "username": app.ssh_user,
        "timeout": 10,
    }

    if app.ssh_key_path:
        connect_kwargs["key_filename"] = app.ssh_key_path
    elif app.ssh_password:
        connect_kwargs["password"] = app.ssh_password

    last_error = None
    for attempt in range(retries):
        try:
            client.connect(**connect_kwargs)
            return client
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(1)
    raise last_error


def test_connection(app: Application) -> dict:
    """Test SSH connectivity and return result dict."""
    try:
        client = _build_client(app)
        _, stdout, _ = client.exec_command("echo ok")
        out = stdout.read().decode().strip()
        client.close()
        return {"success": out == "ok", "message": "连接成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def discover_pid(app: Application) -> int | None:
    """Discover JVM PID by process name using pgrep."""
    if not app.jvm_process_name:
        logger.debug("[discover_pid] jvm_process_name is None, returning early")
        return None
    try:
        client = _build_client(app)
        name = app.jvm_process_name
        _, stdout, stderr = client.exec_command(f"pgrep -f {shlex.quote(name)}")
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        client.close()
        logger.debug("[discover_pid] name=%r out=%r err=%r", name, out, err)
        for line in out.splitlines():
            line = line.strip()
            if line.isdigit():
                return int(line)
    except Exception as e:
        logger.debug("[discover_pid] exception: %s", e)
    return None


def push_file(app: Application, local_path: str, remote_path: str) -> None:
    """SCP a local file to the target host."""
    client = _build_client(app)
    sftp = client.open_sftp()
    try:
        remote_dir = str(Path(remote_path).parent)
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            _mkdir_p(sftp, remote_dir)
        sftp.put(local_path, remote_path)
    finally:
        sftp.close()
        client.close()


def push_content(app: Application, content: str, remote_path: str) -> None:
    """Push string content as a file to the target host."""
    client = _build_client(app)
    sftp = client.open_sftp()
    try:
        remote_dir = str(Path(remote_path).parent)
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            _mkdir_p(sftp, remote_dir)
        with sftp.open(remote_path, "w") as f:
            f.write(content)
    finally:
        sftp.close()
        client.close()


def run_command(app: Application, command: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a remote command; return (exit_code, stdout, stderr)."""
    client = _build_client(app)
    _, stdout, stderr = client.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    client.close()
    return exit_code, out, err


def _mkdir_p(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    """Recursively create remote directories."""
    parts = remote_dir.rstrip("/").split("/")
    current = ""
    for part in parts:
        if not part:
            current = "/"
            continue
        current = current.rstrip("/") + "/" + part
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def _is_docker_mode(app: Application) -> bool:
    """Return whether the app should be managed as a docker-compose workload."""
    return (getattr(app, "launch_mode", "") or "").lower() == "docker_compose"


def _resolve_agent_storage_url(app: Application, default_url: str) -> str:
    """Resolve the AREX storage URL that the target JVM should use."""
    if _is_docker_mode(app):
        return (
            getattr(app, "docker_storage_url", None)
            or getattr(app, "arex_storage_url", None)
            or default_url
        )
    return getattr(app, "arex_storage_url", None) or default_url


def _resolve_docker_workdir(app: Application) -> str:
    workdir = getattr(app, "docker_workdir", None) or ""
    return workdir.strip().rstrip("/")


def _resolve_docker_compose_file(app: Application) -> str:
    compose_file = getattr(app, "docker_compose_file", None) or "docker-compose.yml"
    if Path(compose_file).is_absolute():
        return compose_file
    workdir = _resolve_docker_workdir(app)
    return f"{workdir}/{compose_file}" if workdir else compose_file


def _resolve_docker_override_file(app: Application) -> str:
    workdir = _resolve_docker_workdir(app)
    override_file = ".arex-recorder/docker-compose.arex.override.yml"
    return f"{workdir}/{override_file}" if workdir else override_file


def _resolve_docker_agent_path(app: Application) -> str:
    agent_path = getattr(app, "docker_agent_path", None) or "/opt/arex/arex-agent.jar"
    return agent_path


def _split_storage_host_port(storage_url: str | None, default_port: str) -> tuple[str, str]:
    """Parse a storage URL into host and port, ignoring scheme/path/query noise."""
    raw = (storage_url or "").strip()
    if not raw:
        return "", default_port
    candidate = raw if "://" in raw else f"http://{raw}"
    parsed = urlparse(candidate)
    host = parsed.hostname or parsed.netloc or raw
    port = str(parsed.port) if parsed.port else default_port
    return host, port


def _remote_path_exists(app: Application, remote_path: str) -> bool:
    """Return whether a remote path exists on the Docker host."""
    exit_code, _, _ = run_command(app, f"test -f {shlex.quote(remote_path)}", timeout=15)
    return exit_code == 0


def render_docker_compose_override(
    app: Application,
    arex_storage_url: str,
    agent_host_path: str,
    agent_container_path: str,
) -> str:
    """Render docker-compose override content for AREX agent injection.

    agent_host_path is the file on the Docker host.
    agent_container_path is the path visible inside the container/JVM.
    """
    service_name = getattr(app, "docker_service_name", None) or app.name
    storage_host, storage_port = _split_storage_host_port(arex_storage_url, "8093")

    sample_rate_pct = max(0, min(100, int(round(float(getattr(app, "sample_rate", 1.0) or 0) * 100))))
    java_tool_options = (
        f"-javaagent:{agent_container_path}"
        f" -Darex.service.name={app.arex_app_id or app.name}"
        f" -Darex.storage.service.host={storage_host}"
        f" -Darex.storage.service.port={storage_port}"
        f" -Darex.record.rate={sample_rate_pct}"
    )
    java_tool_options = json.dumps(java_tool_options, ensure_ascii=False)
    agent_mount_path = _resolve_docker_agent_path(app)

    return (
        "services:\n"
        f"  {service_name}:\n"
        "    extra_hosts:\n"
        "      - \"host.docker.internal:host-gateway\"\n"
        "    environment:\n"
        f"      JAVA_TOOL_OPTIONS: {java_tool_options}\n"
        "    volumes:\n"
        f"      - \"{agent_host_path}:{agent_mount_path}:ro\"\n"
    )


def _run_docker_compose(app: Application, command: str, timeout: int = 90) -> tuple[int, str, str]:
    """Run a docker compose command in the target workdir."""
    workdir = _resolve_docker_workdir(app)
    if not workdir:
        return 1, "", "docker_workdir is required"
    return run_command(app, f"cd {shlex.quote(workdir)} && {command}", timeout=timeout)


def _run_docker_compose_with_fallback(app: Application, command: str, timeout: int = 90) -> tuple[int, str, str]:
    """Run docker compose, falling back to legacy docker-compose if needed."""
    exit_code, out, err = _run_docker_compose(app, command, timeout=timeout)
    if exit_code == 0:
        return exit_code, out, err
    if "docker compose" not in command:
        return exit_code, out, err
    legacy_command = command.replace("docker compose", "docker-compose", 1)
    return _run_docker_compose(app, legacy_command, timeout=timeout)


def deploy_docker_agent(app: Application, local_agent_jar_path: str, arex_storage_url: str) -> str:
    """Upload AREX agent and start/recreate the docker-compose service with injected env."""
    workdir = _resolve_docker_workdir(app)
    service_name = getattr(app, "docker_service_name", None) or app.name
    if not workdir:
        return "ERROR: docker_workdir is required"

    agent_host_path = f"{workdir}/.arex-recorder/arex-agent.jar"
    agent_container_path = _resolve_docker_agent_path(app)
    override_remote_path = _resolve_docker_override_file(app)
    override_content = render_docker_compose_override(
        app,
        arex_storage_url,
        agent_host_path,
        agent_container_path,
    )

    try:
        push_file(app, local_agent_jar_path, agent_host_path)
        push_content(app, override_content, override_remote_path)
        compose_file = _resolve_docker_compose_file(app)
        compose_cmd = (
            f"docker compose -f {shlex.quote(compose_file)} "
            f"-f {shlex.quote(override_remote_path)} up -d --force-recreate {shlex.quote(service_name)}"
        )
        exit_code, out, err = _run_docker_compose_with_fallback(app, compose_cmd, timeout=180)
        if exit_code != 0:
            return f"ERROR: docker compose failed (exit {exit_code}): {err or out}".strip()
        return f"OK: deployed docker agent into {compose_file}"
    except Exception as exc:
        logger.exception("deploy_docker_agent failed: %s", exc)
        return f"ERROR: {exc}"


def remove_docker_agent(app: Application) -> str:
    """Remove AREX override file and recreate the docker-compose service without agent."""
    workdir = _resolve_docker_workdir(app)
    service_name = getattr(app, "docker_service_name", None) or app.name
    if not workdir:
        return "ERROR: docker_workdir is required"

    override_remote_path = _resolve_docker_override_file(app)
    compose_file = _resolve_docker_compose_file(app)
    try:
        run_command(app, f"rm -f {shlex.quote(override_remote_path)}")
        compose_cmd = (
            f"docker compose -f {shlex.quote(compose_file)} "
            f"up -d --force-recreate {shlex.quote(service_name)}"
        )
        exit_code, out, err = _run_docker_compose_with_fallback(app, compose_cmd, timeout=180)
        if exit_code != 0:
            return f"ERROR: docker compose failed (exit {exit_code}): {err or out}".strip()
        return f"OK: removed docker agent from {compose_file}"
    except Exception as exc:
        logger.exception("remove_docker_agent failed: %s", exc)
        return f"ERROR: {exc}"


def get_docker_agent_status(app: Application) -> dict:
    """Check whether the docker-compose service is running with AREX agent env."""
    workdir = _resolve_docker_workdir(app)
    service_name = getattr(app, "docker_service_name", None) or app.name
    if not workdir:
        return {"status": "NOT_CONFIGURED", "pid": None, "arex_agent": False}

    compose_file = _resolve_docker_compose_file(app)
    override_remote_path = _resolve_docker_override_file(app)
    override_exists = _remote_path_exists(app, override_remote_path)
    if override_exists:
        ps_cmd = (
            f"docker compose -f {shlex.quote(compose_file)} "
            f"-f {shlex.quote(override_remote_path)} ps -q {shlex.quote(service_name)}"
        )
    else:
        ps_cmd = (
            f"docker compose -f {shlex.quote(compose_file)} "
            f"ps -q {shlex.quote(service_name)}"
        )

    exit_code, out, err = _run_docker_compose_with_fallback(app, ps_cmd, timeout=60)
    if exit_code != 0 and override_exists:
        base_ps_cmd = f"docker compose -f {shlex.quote(compose_file)} ps -q {shlex.quote(service_name)}"
        exit_code, out, err = _run_docker_compose_with_fallback(app, base_ps_cmd, timeout=60)
    if exit_code != 0:
        logger.debug("get_docker_agent_status: ps failed: %s", err or out)
        return {"status": "NOT_RUNNING", "pid": None, "arex_agent": False}

    cid = out.strip()
    if not cid:
        return {"status": "NOT_RUNNING", "pid": None, "arex_agent": False}

    inspect_cmd = (
        "docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "
        f"{shlex.quote(cid)}"
    )
    exit_code, env_out, env_err = run_command(app, inspect_cmd, timeout=60)
    if exit_code != 0:
        logger.debug("get_docker_agent_status: inspect failed: %s", env_err or env_out)
        return {"status": "RUNNING", "pid": cid, "arex_agent": False, "cmdline": ""}

    arex_present = "JAVA_TOOL_OPTIONS" in env_out and "-javaagent" in env_out
    return {
        "status": "RUNNING",
        "pid": cid,
        "arex_agent": arex_present,
        "cmdline": env_out[:200],
    }


# ---------------------------------------------------------------------------
# AREX agent deployment methods
# ---------------------------------------------------------------------------

def upload_arex_agent(app: Application, local_agent_jar_path: str) -> None:
    """Upload arex-agent.jar to the target server.

    Remote path: ~/arex-agent/arex-agent.jar
    The remote directory is created if it does not exist.
    """
    _, home_out, _ = run_command(app, "echo $HOME")
    home = home_out.strip()
    remote_abs = f"{home}/arex-agent/arex-agent.jar"

    client = _build_client(app)
    sftp = client.open_sftp()
    try:
        remote_dir = f"{home}/arex-agent"
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            _mkdir_p(sftp, remote_dir)
        sftp.put(local_agent_jar_path, remote_abs)
        logger.info("upload_arex_agent: uploaded %s -> %s", local_agent_jar_path, remote_abs)
    finally:
        sftp.close()
        client.close()


def _extract_java_version(output: str) -> str | None:
    """Extract a Java version string from `java -version` output."""
    match = re.search(r'"([^"]+)"', output)
    if match:
        return match.group(1)
    return output or None


def _detect_java_version_with_command(app: Application, command: str) -> str | None:
    """Run a remote Java command and parse the first version line."""
    _, out, err = run_command(app, command)
    output = (out + err).strip()
    return _extract_java_version(output)


def _find_startup_script(app: Application) -> str | None:
    """Find the target JVM startup script, if present."""
    pid = discover_pid(app)
    if pid is not None:
        _, out0, _ = run_command(
            app,
            (
                f'cwd="$(readlink -f /proc/{pid}/cwd 2>/dev/null)"; '
                'for f in "$cwd/start.sh" "$cwd/startup.sh"; do '
                '[ -f "$f" ] && printf "%s" "$f" && exit 0; '
                'done'
            ),
        )
        script_path = out0.strip()
        if script_path:
            return script_path

    if app.jvm_process_name:
        jar_name = shlex.quote(app.jvm_process_name)
        _, out_jar, _ = run_command(
            app,
            (
                f'jar_path="$(find ~ -maxdepth 6 -type f -name {jar_name} 2>/dev/null | head -1)"; '
                'if [ -n "$jar_path" ]; then '
                'jar_dir="$(dirname "$jar_path")"; '
                'for f in "$jar_dir/start.sh" "$(dirname "$jar_dir")/start.sh" '
                '"$jar_dir/startup.sh" "$(dirname "$jar_dir")/startup.sh"; do '
                '[ -f "$f" ] && printf "%s" "$f" && exit 0; '
                'done; '
                'fi'
            ),
        )
        script_path = out_jar.strip()
        if script_path:
            return script_path

    _, out1, _ = run_command(
        app,
        'find ~ -maxdepth 3 \\( -name "start.sh" -o -name "startup.sh" \\) 2>/dev/null | head -1',
    )
    script_path = out1.strip()
    if script_path:
        return script_path

    _, out2, _ = run_command(
        app,
        'ls ~/bin/start.sh ~/start.sh 2>/dev/null | head -1',
    )
    script_path = out2.strip()
    return script_path or None


def detect_java_version(app: Application, script_path: str | None = None) -> str | None:
    """Detect the Java version actually used by the target service.

    Detection order:
    1. Running JVM binary (`/proc/<pid>/exe`) if the target process is already up.
    2. `JAVA_HOME` or explicit java binary found in the startup script.
    3. Fallback to the host default `java -version`.

    Returns a string like "1.8.0_362" (JDK8), "11.0.18" (JDK11), or None on failure.
    """
    try:
        pid = discover_pid(app)
        if pid is not None:
            _, out, err = run_command(app, f"readlink -f /proc/{pid}/exe")
            java_bin = (out + err).strip()
            if java_bin.endswith("/java"):
                detected = _detect_java_version_with_command(
                    app, f"{shlex.quote(java_bin)} -version 2>&1 | head -1"
                )
                if detected:
                    return detected

        if script_path is None:
            script_path = _find_startup_script(app)

        if script_path:
            _, script_content, _ = run_command(app, f"cat {shlex.quote(script_path)}")

            java_home_match = re.search(
                r'^\s*(?:export\s+)?JAVA_HOME\s*=\s*["\']?([^\s"\']+)["\']?',
                script_content,
                re.MULTILINE,
            )
            if java_home_match:
                java_home = java_home_match.group(1).strip()
                if java_home:
                    detected = _detect_java_version_with_command(
                        app, f"{shlex.quote(java_home + '/bin/java')} -version 2>&1 | head -1"
                    )
                    if detected:
                        return detected

            explicit_java_match = re.search(r'(/[^ \t\r\n;|&]+/bin/java)\b', script_content)
            if explicit_java_match:
                java_bin = explicit_java_match.group(1)
                detected = _detect_java_version_with_command(
                    app, f"{shlex.quote(java_bin)} -version 2>&1 | head -1"
                )
                if detected:
                    return detected

        return _detect_java_version_with_command(app, "java -version 2>&1 | head -1")
    except Exception as e:
        logger.warning("detect_java_version failed: %s", e)
        return None


def inject_javaagent_param(app: Application, arex_storage_url: str, agent_remote_path: str) -> str:
    """Inject -javaagent and -Darex.* params into the target JVM startup script.

    Returns one of:
      "OK: injected into {script_path}"
      "ALREADY_INJECTED"
      "NOT_FOUND: no startup script found at ~/start.sh or ~/bin/start.sh"
      "ERROR: JDK version {ver} is not supported — AREX agent requires JDK 8 or JDK 11"
    """
    script_path = _find_startup_script(app)

    # Step 0: verify target JVM version is compatible with AREX agent.
    # AREX agent supports JDK 8 (1.8.x) and JDK 11 (11.x).
    # JDK 17+ may work but is untested; JDK 6/7 are not supported.
    java_ver = detect_java_version(app, script_path=script_path)
    if java_ver:
        supported = (
            java_ver.startswith("1.8.")   # JDK 8
            or java_ver.startswith("11.") # JDK 11
            or java_ver.startswith("17.") # JDK 17 (experimental)
        )
        if not supported:
            logger.warning(
                "inject_javaagent_param: target JVM is %s, "
                "AREX agent requires JDK 8 (1.8.x) or JDK 11 (11.x)", java_ver
            )
            return (
                f"ERROR: JDK version {java_ver} is not supported — "
                "AREX agent requires JDK 8 or JDK 11"
            )
        logger.info("inject_javaagent_param: target JVM detected as %s", java_ver)

    # Step 1: find the startup script
    if not script_path:
        return "NOT_FOUND: no startup script found at ~/start.sh or ~/bin/start.sh"

    # Step 2: read the script content
    _, script_content, _ = run_command(app, f"cat {shlex.quote(script_path)}")

    # Step 3: check if already injected
    if "-javaagent" in script_content:
        return "ALREADY_INJECTED"

    # Step 4: build javaagent string
    # Use arex_app_id as the service name if configured; fall back to app.name.
    # arex_app_id must match the appId in arex-storage so recordings can be synced.
    service_name = app.arex_app_id or app.name

    storage_host, storage_port = _split_storage_host_port(arex_storage_url, "8093")

    # Convert sample_rate (0.0–1.0) to integer percentage (0–100) for AREX agent.
    sample_rate_pct = max(0, min(100, int(round(app.sample_rate * 100))))

    # AREX agent requires host and port as SEPARATE system properties.
    # Do NOT combine as "host:port" — the agent will fail to connect.
    javaagent_param = (
        f"-javaagent:{agent_remote_path}"
        f" -Darex.service.name={service_name}"
        f" -Darex.storage.service.host={storage_host}"
        f" -Darex.storage.service.port={storage_port}"
        f" -Darex.record.rate={sample_rate_pct}"
    )

    # Step 5: inject into the java command line via sed
    escaped_param = javaagent_param.replace('\\', '\\\\').replace('/', '\\/').replace('&', '\\&')
    sed_cmd = f"sed -i 's/java /java {escaped_param} /' {shlex.quote(script_path)}"
    exit_code, _, sed_err = run_command(app, sed_cmd)
    if exit_code != 0:
        logger.warning("inject_javaagent_param: sed failed (exit %d): %s", exit_code, sed_err)

    return f"OK: injected into {script_path}"


def get_javaagent_status(app: Application) -> dict:
    """Check if arex-agent is currently running in the target JVM.

    Returns a dict with keys: status, pid, arex_agent, and optionally cmdline.
    """
    pid = discover_pid(app)
    if pid is None:
        return {"status": "NOT_RUNNING", "pid": None, "arex_agent": False}

    _, cmdline_out, _ = run_command(app, f"cat /proc/{pid}/cmdline | tr '\\0' ' '")
    arex_present = "arex-agent" in cmdline_out

    return {
        "status": "RUNNING",
        "pid": pid,
        "arex_agent": arex_present,
        "cmdline": cmdline_out[:200],
    }
