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


def inject_javaagent_param(app: Application, arex_storage_url: str, agent_remote_path: str) -> str:
    """Inject -javaagent and -Darex.* params into the target JVM startup script.

    Returns one of:
      "OK: injected into {script_path}"
      "ALREADY_INJECTED"
      "NOT_FOUND: no startup script found at ~/start.sh or ~/bin/start.sh"
    """
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
    storage_netloc = re.sub(r'^https?://', '', arex_storage_url).rstrip('/')
    if ':' in storage_netloc:
        storage_host, storage_port = storage_netloc.rsplit(':', 1)
    else:
        storage_host = storage_netloc
        storage_port = "8080"

    javaagent_param = (
        f"-javaagent:{agent_remote_path}"
        f" -Darex.service.name={app.name}"
        f" -Darex.storage.service.host={storage_host}:{storage_port}"
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
