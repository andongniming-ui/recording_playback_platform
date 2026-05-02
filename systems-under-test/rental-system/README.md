# Rental System (租车系统)

基于 Spring Boot 2.7.18 + JDK8 + MySQL + XML 格式请求的租车管理系统，包含基准系统和对标差异系统，用于录制回放对比测试。

## 项目结构

```
rental-system/
├── pom.xml                    # 父 POM
├── create_databases.sql       # 数据库建表 + 种子数据
├── send_samples.sh            # 示例请求脚本
├── 接口清单.md                 # 完整接口文档（含差异说明）
├── rental-common/             # 共享模块（实体、DTO、工具类）
├── rental-base/               # 基准系统 (端口 20081)
│   └── start.sh
├── rental-compare/            # 差异系统 (端口 20082)
│   └── start.sh
└── postman/                   # Postman 集合和环境配置
```

## 快速启动

```bash
# 1. 初始化数据库
mysql -h localhost -P 3307 -u root -proot123 < create_databases.sql

# 2. 编译项目
cd /home/recording_playback_platform/systems-under-test/rental-system
mvn clean package -DskipTests

# 3. 启动基准系统（默认带 AREX Agent）
cd rental-base && ./start.sh

# 4. 启动差异系统（默认带 AREX Agent）
cd ../rental-compare && ./start.sh

# 5. 发送示例请求到 base；如需 compare：TARGET=http://127.0.0.1:20082 ./send_samples.sh
cd .. && ./send_samples.sh
```

启动脚本默认读取：

```bash
AREX_AGENT_JAR=/home/test/arex-platform_v1/backend/arex-agent/arex-agent.jar
AREX_STORAGE_HOST=127.0.0.1:8000
AREX_RECORD_RATE=100
```

如果平台部署在局域网另一台机器，把 `AREX_STORAGE_HOST` 改成平台机器 IP，例如：

```bash
AREX_STORAGE_HOST=192.168.43.64:8000 ./rental-base/start.sh
```

## 服务端口

| 系统 | 端口 |
|------|------|
| rental-base | 20081 |
| rental-compare | 20082 |

## 技术栈

- Java 1.8
- Spring Boot 2.7.18
- Spring JDBC (JdbcTemplate)
- MySQL 8.0 (com.mysql:mysql-connector-j)
- Jackson XML (jackson-dataformat-xml)
- Logback (日志)

## 数据表

| 表名 | 说明 |
|------|------|
| rental_user | 用户表 |
| rental_store | 门店表 |
| rental_vehicle | 车辆表 |
| rental_order | 订单表 |
| rental_payment | 支付表 |
| transaction_log | 交易日志表（流水号可查全链路信息）|

## 接口统计

- 总接口：30 个
- 含子调用（外呼）接口：15 个
- 纯数据库接口：15 个
- 基准 vs 差异：8 个接口有差异

## 请求格式

当前代码实际支持的请求格式是紧凑 XML body：

```xml
<body>
  <trans_code>VEH002</trans_code>
  <vehicle_id>1</vehicle_id>
</body>
```

请求头建议带：

```text
Content-Type: application/xml
Accept: application/xml
X-Serial-No: 202604290000000001
```

不要使用旧版 `<request><header>...</header><body>...</body></request>` 包装，当前 Controller 的 `@RequestBody` DTO 不会按该格式解析。

## 日志系统

每个请求自动生成 18 位流水号，所有交易信息（请求/响应/子调用/数据库操作）写入：
- `transaction_log` 数据库表（按 serial_no 查询）
- `runtime/logs/rental-base/transaction.log` 文件

## AREX 兼容性说明

本项目数据库访问方式是 Spring `JdbcTemplate`。AREX 0.4.8 对 `JdbcTemplate`/原生 JDBC 的数据库子调用录制能力有限，因此不要把数据库子调用作为该项目的唯一验收点；主 Servlet 入口和 HTTP 子调用仍可用于平台录制、回放和差异对比。
