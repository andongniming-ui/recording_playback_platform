from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_DB = ROOT_DIR / "data" / "arex_recorder.db"
DEFAULT_SSH_KEYS_DIR = ROOT_DIR / "ssh_keys"


class Settings(BaseSettings):
    db_type: str = "sqlite"
    db_url: str = f"sqlite+aiosqlite:///{DEFAULT_SQLITE_DB}"
    secret_key: str = "changeme-in-production"
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
    arex_agent_jar_path: str = "/home/test/arex-agent/arex-agent.jar"
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
    # 日志落盘：留空则不写文件，填路径则启用 RotatingFileHandler
    log_file: str = ""
    log_max_bytes: int = 10 * 1024 * 1024   # 10 MB
    log_backup_count: int = 5
    # N-LS MySQL（用于从 bank_sub_call_log 获取业务步骤）
    nls_mysql_host: str = ""
    nls_mysql_port: int = 3306
    nls_mysql_user: str = "root"
    nls_mysql_password: str = ""
    # didi MySQL（用于补全 JdbcTemplate 读写子调用）
    didi_mysql_host: str = "127.0.0.1"
    didi_mysql_port: int = 3307
    didi_mysql_user: str = "root"
    didi_mysql_password: str = "root123"
    didi_mysql_db_sat: str = "didi_alpha"
    didi_mysql_db_uat: str = "didi_beta"

    model_config = SettingsConfigDict(
        env_prefix="AR_",
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
