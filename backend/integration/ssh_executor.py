"""
SSH/SFTP operations on target hosts via Paramiko.
All methods are sync (run in thread pool via asyncio.to_thread).
"""
import logging
import re
import time
from pathlib import Path
import paramiko
from models.application import Application

logger = logging.getLogger(__name__)


def _build_client(app: Application, retries: int = 3) -> paramiko.SSHClient:
    """Build SSH client with retry mechanism."""
    client = paramiko.SSHClient()
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
        return {"success": out == "ok", "message": "SSH connection successful"}
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
        _, stdout, stderr = client.exec_command(f"pgrep -f '{name}'")
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


def detect_java_version(app: Application) -> str | None:
    """Detect the Java version on the target host.

    Returns a string like "1.8.0_362" (JDK8), "11.0.18" (JDK11), or None on failure.
    """
    try:
        _, out, err = run_command(app, "java -version 2>&1 | head -1")
        # java -version prints to stderr; redirect above captures it in stdout
        output = (out + err).strip()
        # Typical outputs:
        #   openjdk version "1.8.0_362" 2023-01-17
        #   java version "11.0.18" 2023-01-17
        match = re.search(r'"([^"]+)"', output)
        if match:
            return match.group(1)
        return output or None
    except Exception as e:
        logger.warning("detect_java_version failed: %s", e)
        return None


def inject_javaagent_param(app: Application, arex_storage_url: str, agent_remote_path: str) -> str:
    """Inject -javaagent and -Darex.* params into the target JVM startup script.

    Returns one of:
      "OK: injected into {script_path}"
      "ALREADY_INJECTED"
      "NOT_FOUND: no startup script found at ~/start.sh or ~/bin/start.sh"
      "ERROR: JDK version {ver} is not JDK 8 — use the correct AREX agent JAR"
    """
    # Step 0: verify target JVM is JDK 8
    java_ver = detect_java_version(app)
    if java_ver:
        # JDK8 reports version strings starting with "1.8."
        # JDK11+ reports "11.", "17.", etc.
        if not java_ver.startswith("1.8."):
            logger.warning(
                "inject_javaagent_param: target JVM is %s, expected JDK 8 (1.8.x)", java_ver
            )
            return f"ERROR: JDK version {java_ver} is not JDK 8 — use the correct AREX agent JAR"

    # Step 1: find the startup script
    _, out1, _ = run_command(
        app,
        'find ~ -maxdepth 3 -name "start.sh" -o -name "startup.sh" 2>/dev/null | head -1',
    )
    script_path = out1.strip()

    if not script_path:
        _, out2, _ = run_command(
            app,
            'ls ~/bin/start.sh ~/start.sh 2>/dev/null | head -1',
        )
        script_path = out2.strip()

    if not script_path:
        return "NOT_FOUND: no startup script found at ~/start.sh or ~/bin/start.sh"

    # Step 2: read the script content
    _, script_content, _ = run_command(app, f"cat {script_path}")

    # Step 3: check if already injected
    if "-javaagent" in script_content:
        return "ALREADY_INJECTED"

    # Step 4: build javaagent string
    # Use arex_app_id as the service name if configured; fall back to app.name.
    # arex_app_id must match the appId in arex-storage so recordings can be synced.
    service_name = app.arex_app_id or app.name

    storage_netloc = re.sub(r'^https?://', '', arex_storage_url).rstrip('/')
    if ':' in storage_netloc:
        storage_host, storage_port = storage_netloc.rsplit(':', 1)
    else:
        storage_host = storage_netloc
        storage_port = "8080"

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
    sed_cmd = f"sed -i 's/java /java {escaped_param} /' {script_path}"
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
