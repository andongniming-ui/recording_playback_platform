from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_type: str = "sqlite"
    db_url: str = "sqlite+aiosqlite:////home/test/arex-recorder/data/arex_recorder.db"
    secret_key: str = "changeme-in-production"
    ssh_keys_dir: str = "/home/test/arex-recorder/ssh_keys"
    cors_origins: list[str] = ["*"]
    debug: bool = False
    # AREX storage 连接
    arex_storage_url: str = "http://localhost:8093"
    arex_agent_storage_url: str = ""   # 留空则回退到 arex_storage_url
    docker_agent_storage_url: str = "http://host.docker.internal:8093"
    arex_agent_jar_path: str = "/home/test/arex-agent/arex-agent.jar"
    # JWT
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    # 回放默认配置
    default_replay_concurrency: int = 5
    default_replay_timeout_ms: int = 5000
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

    model_config = SettingsConfigDict(env_prefix="AR_", env_file=".env", env_file_encoding="utf-8")


settings = Settings()
