from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_DB = ROOT_DIR / "data" / "arex_recorder.db"
DEFAULT_SSH_KEYS_DIR = ROOT_DIR / "ssh_keys"


class Settings(BaseSettings):
    db_type: str = "sqlite"
    db_url: str = f"sqlite+aiosqlite:///{DEFAULT_SQLITE_DB}"
    secret_key: str = "local-dev-only-change-this-secret-key"
    enforce_secure_secret: bool = False
    ssh_keys_dir: str = str(DEFAULT_SSH_KEYS_DIR)
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    # Initial admin password for first-run setup.
    # If empty, a random password is generated and printed to the console.
    admin_init_password: str = ""
    debug: bool = False
    # AREX storage 连接
    arex_storage_url: str = "http://127.0.0.1:8000"
    arex_agent_storage_url: str = ""   # 留空则回退到 arex_storage_url
    docker_agent_storage_url: str = "http://host.docker.internal:8000"
    arex_agent_jar_path: str = "/opt/arex/arex-agent.jar"
    # JWT
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    # 回放默认配置
    default_replay_concurrency: int = 5
    default_replay_timeout_ms: int = 5000
    # 回放后等待 AREX Agent 异步上报子调用的时间（秒）
    arex_flush_delay_s: float = 1.0
    # AREX flush 后子调用为空时的重试配置
    arex_flush_max_retries: int = 3           # 最多重试次数（0 = 不重试）
    arex_flush_retry_interval_s: float = 0.5  # 每次重试间隔（秒）
    # 回放任务心跳。进程崩溃后，超过 timeout 仍未更新心跳的 RUNNING 任务会被恢复为 FAILED。
    replay_job_heartbeat_interval_s: float = 5.0
    replay_job_heartbeat_timeout_s: float = 300.0
    # 日志落盘：留空则不写文件，填路径则启用 RotatingFileHandler
    log_file: str = ""
    log_max_bytes: int = 10 * 1024 * 1024   # 10 MB
    log_backup_count: int = 5
    # ── System plugin configs (moved from hardcoded to plugin, kept here for .env) ──
    # N-LS plugin MySQL
    nls_mysql_host: str = ""
    nls_mysql_port: int = 3306
    nls_mysql_user: str = "root"
    nls_mysql_password: str = ""
    # Didi plugin MySQL
    didi_mysql_host: str = ""
    didi_mysql_port: int = 3306
    didi_mysql_user: str = "root"
    didi_mysql_password: str = ""
    didi_mysql_db_sat: str = ""
    didi_mysql_db_uat: str = ""

    model_config = SettingsConfigDict(
        env_prefix="AR_",
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
