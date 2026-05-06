# Fitness Demo 内网验证手册

本文档用于验证“平台在内网服务器、Fitness 被测系统在另一台内网机器”时，录制链路是否可用。

## 1. 环境假设

| 角色 | 示例地址 | 说明 |
|---|---|---|
| 平台机器 | `192.168.3.9` | 运行录制回放平台后端和前端 |
| Fitness 被测系统机器 | `192.168.3.58` | 运行 `fitness-compare-system` |
| Fitness 服务端口 | `18080` | Spring Boot 业务端口 |
| 平台后端端口 | `8000` | AREX Agent 上报地址 |
| 平台前端端口 | `5173` | 浏览器访问地址 |

实际内网部署时，把 IP 换成自己的服务器地址。

## 2. 启动平台

在平台机器执行：

```bash
cd /home/recording_playback_platform/deploy/intranet
cp .env.production.example .env.production
vi .env.production
./deploy-intranet.sh
curl http://127.0.0.1:8000/api/health
```

在 Fitness 机器验证能访问平台：

```powershell
curl.exe http://192.168.3.9:8000/api/health
```

## 3. 启动 Fitness 被测系统

把固定版本 AREX Agent 放到 Fitness 机器，例如：

```text
H:\test\arex-agent\arex-agent-0.4.8.jar
```

PowerShell 推荐用一行命令，避免反引号换行导致 JVM 参数被截断：

```powershell
java -javaagent:H:\test\arex-agent\arex-agent-0.4.8.jar -Darex.service.name=fitness-sat -Darex.storage.service.host=192.168.3.9 -Darex.storage.service.port=8000 -Darex.record.rate=1 -Dserver.port=18080 -Dfitness.system-code=sat -Dfitness.provider-base-url=http://192.168.3.58:18080 -jar target\fitness-compare-system-1.0.0.jar
```

健康检查：

```powershell
curl.exe http://127.0.0.1:18080/health
curl.exe http://192.168.3.58:18080/health
```

如果 Fitness 需要 MySQL，先确保账号密码和库已经正确初始化。

## 4. 平台新增应用填写

在平台页面进入“应用管理 -> 新增应用”。

| 字段 | 建议填写 |
|---|---|
| 应用名称 | `fitness-sat` |
| 描述 | `Fitness demo SAT` |
| 宿主机地址 | `192.168.3.58` |
| 宿主机用户 | 台式机 SSH 用户；如果不用平台远程启动，可先填实际用户名 |
| 宿主机端口 | `22` |
| 启动模式 | 手动启动时可以先保留默认；需要平台远程启动时再配置脚本 |
| 服务端口 | `18080` |
| JVM 进程名 | `fitness-compare-system-1.0.0.jar` |
| AREX App ID | `fitness-sat` |
| AREX Storage 地址 | `http://192.168.3.9:8000` |
| 采样率 | `1` |
| 交易码提取字段 | `apiCode`、`scenarioId` 或先留空 |

关键点：

- `AREX App ID` 必须等于 JVM 启动参数 `-Darex.service.name=fitness-sat`。
- `AREX Storage 地址` 必须是 Fitness 机器能访问的平台后端地址。
- 录制不到数据时，先检查平台后端日志和 Fitness 启动日志里的 AREX 上报地址。

## 5. 创建录制会话

在“录制中心”选择 `fitness-sat`，新建会话，例如：

```text
fitness-sat-api-recording
```

保持会话为录制中，然后在 Fitness 机器发请求。

## 6. 请求样例

PowerShell：

```powershell
curl.exe -X POST http://127.0.0.1:18080/fitness/api01 -H "Content-Type: application/xml" -d "<FitnessRequest><memberId>M10001</memberId><channel>APP</channel></FitnessRequest>"
curl.exe -X POST http://127.0.0.1:18080/fitness/api07 -H "Content-Type: application/xml" -d "<FitnessRequest><memberId>M10001</memberId><channel>APP</channel></FitnessRequest>"
```

也可以从平台机器请求 Fitness：

```bash
curl -X POST http://192.168.3.58:18080/fitness/api01 \
  -H "Content-Type: application/xml" \
  -d "<FitnessRequest><memberId>M10001</memberId><channel>APP</channel></FitnessRequest>"
```

## 7. 验证录制结果

在平台录制中心检查：

1. 会话录制数是否增加。
2. 会话详情里是否出现 `/fitness/api01`、`/fitness/api07`。
3. 录制详情里 request / response body 是否完整。
4. 如果有子调用，检查子调用面板是否有 HTTP 或 DB 调用。

数据库辅助检查：

```bash
mysql -h127.0.0.1 -P3307 -uarex -p arex_recorder -e "select id, application_id, request_uri, recorded_at from recording order by id desc limit 10;"
```

## 8. 常见问题

| 现象 | 优先检查 |
|---|---|
| 平台页面正常，但录制数一直是 0 | `AREX App ID` 是否等于 `-Darex.service.name` |
| Fitness 能请求成功，但平台没有数据 | Fitness 机器能否访问 `http://平台IP:8000/api/health` |
| 平台同步失败 | 后端 `AR_AREX_STORAGE_URL` 和应用 `AREX Storage 地址` 是否正确 |
| PowerShell 报 JVM 找不到主类 `.service.name` | 不要把 `-Darex.service.name` 拆错，优先使用一行启动命令 |
| MySQL 报 `Access denied` | Fitness 的 `FITNESS_DB_USERNAME` / `FITNESS_DB_PASSWORD` 是否和本机 MySQL 一致 |
| MySQL 报 `Public Key Retrieval is not allowed` | JDBC URL 增加 `allowPublicKeyRetrieval=true`，或调整 MySQL 用户认证方式 |
