# Recording Playback Platform

基于 [AREX](https://github.com/arextest/arex-agent-java) 框架的完整录制回放管理平台，适用于 Java JDK8 + Spring Boot + MySQL 技术栈。

A full-featured AREX recording & replay management platform for Java JDK8 + Spring Boot + MySQL systems.

---

## 功能模块 / Features

| 模块 | 说明 |
|------|------|
| 应用管理 | 注册目标服务，支持宿主机脚本和 Docker Compose 两种接入方式 |
| 录制中心 | 管理录制会话，支持开始/停止录制，收集 arex-storage 结果，预览请求/子调用，批量转为测试用例 |
| 测试用例库 | 用例 CRUD、克隆、标签/状态过滤、JSON 编辑器、HAR/JSON 导入导出 |
| 回放引擎 | 并发回放（1-50），WebSocket 实时进度，AREX 自动 Mock MySQL 子调用 |
| 差异对比 | deepdiff 全字段递归对比，JSONPath 忽略规则，自定义断言（eq/contains/regex/range） |
| 结果分析 | 失败分类汇总，HTML 报告导出 |
| 定时任务 | Cron 表达式调度，关联测试套件批量执行，执行后推送钉钉/企微通知 |
| 测试套件 | 用例拖拽排序，批量执行，套件级别回放 |
| CI/CD 集成 | API Token 管理，HTTP 触发回放，Webhook 回调通知 CI 系统 |
| 用户权限 | JWT 认证，RBAC（Admin / Editor / Viewer），接口级权限控制 |
| Dashboard | ECharts 通过率趋势图，失败分布饼图，实时统计卡片 |
| 系统设置 | AREX storage 配置，脱敏规则管理 |

---

## 变更记录 / Changelog

- 变更记录见 `CHANGELOG.md`

---

## 技术栈 / Tech Stack

| 层次 | 技术 |
|------|------|
| 后端 | Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2, APScheduler |
| 认证 | python-jose (JWT), passlib (bcrypt), RBAC |
| 集成 | Paramiko (SSH/SFTP), httpx (async HTTP), deepdiff |
| 前端 | Vue3, Vite, TypeScript, Naive UI, ECharts, Pinia, Monaco Editor |
| 数据库 | MySQL 8.0（生产）/ SQLite（开发，零配置） |
| 测试 | pytest, pytest-asyncio, httpx AsyncClient |

---

## 快速开始 / Quick Start

### 先决条件 / Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose（用于 MySQL）

### 本地开发

```bash
# 1. 进入平台目录
cd /home/recording_playback_platform/platform

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，至少修改 AR_SECRET_KEY

# 3. 启动 MySQL
docker-compose up -d db

# 4. 安装后端依赖
pip install -r requirements.txt

# 5. 启动后端（自动建表，创建默认管理员）
# 注意：后端使用的是 backend/ 目录内的扁平导入，需在 backend 目录下启动
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 6. 安装前端依赖并启动
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173，使用默认账号登录：

| 字段 | 值 |
|------|----|
| 用户名 | admin |
| 密码 | admin123 |

> **请在首次登录后立即修改密码。**

### Docker 一键启动

```bash
docker-compose up -d --build
```

服务端口：
- 前端开发模式：http://localhost:5173
- 前端 Docker 预览模式：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- MySQL：localhost:3307

---

## 配置说明 / Configuration

复制 `.env.example` 到 `.env` 并按需修改：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AR_DB_TYPE` | `sqlite` | 数据库类型：`sqlite` / `mysql` |
| `AR_DB_URL` | SQLite 文件路径 | 数据库连接字符串 |
| `AR_SECRET_KEY` | `changeme-in-production` | **生产必须修改**，JWT 签名密钥 |
| `AR_AREX_STORAGE_URL` | `http://127.0.0.1:8000` | AREX Storage 代理地址 |
| `AR_AREX_AGENT_STORAGE_URL` | 空 | JDK8/旧版 AREX agent 专用上报地址；配置后挂载时优先注入到 Agent，通常指向本平台后端代理地址 |
| `AR_AREX_AGENT_JAR_PATH` | `/home/test/arex-agent/arex-agent.jar` | AREX Agent JAR 本地路径 |
| `AR_SSH_KEYS_DIR` | `./ssh_keys` | SSH 私钥存储目录 |
| `AR_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access Token 过期时间（分钟） |
| `AR_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh Token 过期时间（天） |
| `AR_DEFAULT_REPLAY_CONCURRENCY` | `5` | 默认回放并发数 |
| `AR_DEFAULT_REPLAY_TIMEOUT_MS` | `5000` | 默认回放超时（毫秒） |
| `AR_AREX_FLUSH_DELAY_S` | `1.0` | 回放后等待 AREX agent flush 子调用的秒数 |
| `AR_AREX_FLUSH_MAX_RETRIES` | `3` | flush 后子调用为空时的最大重试次数 |
| `AR_AREX_FLUSH_RETRY_INTERVAL_S` | `0.5` | flush 重试间隔（秒） |
| `AR_LOG_FILE` | 空 | 日志文件路径；留空则只输出到标准日志 |
| `AR_LOG_MAX_BYTES` | `10485760` | 单个日志文件最大大小 |
| `AR_LOG_BACKUP_COUNT` | `5` | 日志轮转保留份数 |
| `AR_NLS_MYSQL_*` | 空 / 默认端口 | N-LS 补充子调用查询所用 MySQL 配置 |
| `AR_DIDI_MYSQL_*` | 本地默认值 | Didi JdbcTemplate 子调用补全所用 MySQL 配置 |
| `AR_CORS_ORIGINS` | `["*"]` | 允许的跨域来源列表 |
| `AR_DEBUG` | `false` | 是否开启调试模式 |

---

## 系统架构 / Architecture

```
[目标 SpringBoot 服务 (JDK8)]
        ↕ JVM Agent
[arex-agent.jar]  ←宿主机/Compose 注入← [recording playback backend]
        ↓ 录制数据上报
[arex-storage 官方存储服务]
        ↓ REST API
[recording playback backend (FastAPI / Python 3.11)]
        ↓ HTTP 回放
[目标 SpringBoot 服务]
        ↕
[recording playback frontend (Vue3 + Naive UI)]
```

**进程模型：** FastAPI async + APScheduler AsyncIOScheduler
**Agent 通信：** `arex_proxy.py` 兼容旧版 AREX agent 上报协议（`batchSaveMockers` zstd 解压转发）。对于 JDK8/旧版 agent，建议配置 `AR_AREX_AGENT_STORAGE_URL` 指向本平台后端地址，让 Agent 先通过本平台代理再转发到 arex-storage。Docker Compose 模式下，平台会生成 override 并注入 `JAVA_TOOL_OPTIONS`，不再依赖手工修改启动脚本。

---

## API 文档 / API Docs

启动后端后访问：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

所有 API 均以 `/api/v1/` 为前缀，支持 Bearer Token 认证。

---

## 测试 / Testing

```bash
# 运行全部测试（当前 160+ 个测试函数）
pytest backend/tests/ -v

# 仅运行特定模块
pytest backend/tests/test_auth.py -v
pytest backend/tests/test_compare.py -v

# 带覆盖率报告
pytest backend/tests/ -v --cov=backend --cov-report=term-missing
```

测试使用内存 SQLite，外部依赖（SSH、arex-storage、通知 Webhook）均已 Mock，无需外部服务。

---

## 生产部署 / Production Deployment

```bash
# 1. 修改 .env
AR_DB_TYPE=mysql
AR_DB_URL=mysql+aiomysql://user:pass@db-host:3306/arex_recorder
AR_SECRET_KEY=<随机32位以上字符串>
AR_DEBUG=false

# 2. 构建并启动
docker-compose up -d --build

# 3. 查看日志
docker-compose logs -f backend
```

**生产注意事项：**
- 必须修改 `AR_SECRET_KEY` 为随机字符串（`openssl rand -hex 32`）
- 建议配置 Nginx 反向代理，开启 HTTPS
- SSH 私钥文件权限设为 `600`

---

## 扩展开发 / Extension

### 添加通知渠道

在 `backend/utils/notify.py` 中继承 `NotifyProvider` 并注册到 `get_provider()`：

```python
class FeiShuNotify(NotifyProvider):
    async def send(self, webhook: str, payload: dict) -> bool:
        ...

def get_provider(notify_type: str) -> NotifyProvider:
    ...
    if notify_type == "feishu":
        return FeiShuNotify()
```

### 添加自定义断言类型

在 `backend/utils/assertions.py` 中扩展 `evaluate_assertions()` 的 `rule_type` 分支。

### API 版本升级

所有路由挂载于 `/api/v1/`，新版本只需创建 `backend/api/v2/` 并在 `main.py` 注册新前缀。

---

## 目录结构 / Directory Structure

```
platform/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 环境配置
│   ├── database.py          # SQLAlchemy async
│   ├── models/              # ORM 模型（11 个表）
│   ├── schemas/             # Pydantic v2 schemas
│   ├── api/v1/              # REST API 路由（11 个模块）
│   ├── integration/         # arex_client, arex_proxy, ssh_executor
│   ├── core/                # scheduler, replay_executor, security
│   └── utils/               # diff, assertions, desensitize, notify
├── frontend/
│   └── src/
│       ├── views/           # 12 个页面视图
│       ├── components/      # 通用组件
│       ├── store/           # Pinia 状态
│       ├── router/          # Vue Router
│       └── api/             # Axios 封装
├── backend/tests/           # pytest 测试套件（当前 160+ 个测试函数）
├── docker-compose.yml
├── CHANGELOG.md
├── requirements.txt
└── .env.example
```

---

## License

MIT
